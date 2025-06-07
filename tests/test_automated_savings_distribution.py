from typing import Any

import pytest

from src.db.models import AppSettings
from src.savings_distribution.automated_savings_distribution import AutomatedSavingsDistributionService


@pytest.mark.asyncio
async def test_distribute_automated_savings_amount__amount_0(
    load_test_data: None,  # pylint: disable=unused-argument
    automated_distribution_service: AutomatedSavingsDistributionService,
) -> None:
    distribute_amount: int = 0
    moneyboxes: list[dict[str, Any]] = await automated_distribution_service.db_manager.get_moneyboxes()
    sorted_by_priority_moneyboxes: list[dict[str, Any]] = sorted(
        moneyboxes, key=lambda item: item["priority"]
    )

    async with automated_distribution_service.db_manager.async_sessionmaker.begin() as session:
        # calculate savings_distribution amounts for "normal" savings_distribution case
        distribution_amounts: dict[int, int] = await automated_distribution_service.calculate_moneybox_amounts_normal_distribution(
            sorted_by_priority_moneyboxes=sorted_by_priority_moneyboxes,
            distribute_amount=distribute_amount,
        )

        updated_moneyboxes: list[dict[str, Any]] = (
            await automated_distribution_service._distribute_automated_savings_amount(
                # type: ignore  # noqa: ignore  # pylint:disable=line-too-long
                session=session,
                sorted_by_priority_moneyboxes=sorted_by_priority_moneyboxes,
                distribution_amounts=distribution_amounts,
                distribution_description="",
            )
        )

    assert updated_moneyboxes == sorted_by_priority_moneyboxes


@pytest.mark.asyncio
async def test_distribute_automated_savings_amount__amount_negative(
        automated_distribution_service: AutomatedSavingsDistributionService,
) -> None:
    distribute_amount: int = -20
    moneyboxes: list[dict[str, Any]] = await automated_distribution_service.db_manager.get_moneyboxes()
    sorted_by_priority_moneyboxes: list[dict[str, Any]] = sorted(
        moneyboxes, key=lambda item: item["priority"]
    )

    async with automated_distribution_service.db_manager.async_sessionmaker.begin() as session:
        distribution_amounts: dict[int, int] = await automated_distribution_service.calculate_moneybox_amounts_normal_distribution(
            sorted_by_priority_moneyboxes=sorted_by_priority_moneyboxes,
            distribute_amount=distribute_amount,
        )

        updated_moneyboxes: list[dict[str, Any]] = (
            await automated_distribution_service._distribute_automated_savings_amount(
                # type: ignore  # noqa: ignore  # pylint:disable=line-too-long
                session=session,
                sorted_by_priority_moneyboxes=sorted_by_priority_moneyboxes,
                distribution_amounts=distribution_amounts,
                distribution_description="",
            )
        )

    assert updated_moneyboxes == sorted_by_priority_moneyboxes


@pytest.mark.asyncio
async def test_distribute_automated_savings_amount__fill_mode__one_moneybox_with_savings_target_none(  # noqa: ignore  # pylint: disable=line-too-long
        load_test_data: None,
        automated_distribution_service: AutomatedSavingsDistributionService,
) -> None:
    moneyboxes: list[dict[str, Any]] = await automated_distribution_service.db_manager.get_moneyboxes()
    sorted_by_priority_moneyboxes: list[dict[str, Any]] = sorted(
        moneyboxes, key=lambda item: item["priority"]
    )
    app_settings: AppSettings = (
        await automated_distribution_service.db_manager._get_app_settings()  # noqa: ignore  # pylint: disable=protected-access
    )

    async with automated_distribution_service.db_manager.async_sessionmaker.begin() as session:
        distribution_amounts: dict[int, int] = await automated_distribution_service.calculate_moneybox_amounts_fill_distribution(
            sorted_by_priority_moneyboxes=sorted_by_priority_moneyboxes,
            distribute_amount=app_settings.savings_amount,  # 150
        )

        updated_moneyboxes: list[dict[str, Any]] = (
            await automated_distribution_service._distribute_automated_savings_amount(
                # type: ignore  # noqa: ignore  # pylint:disable=line-too-long
                session=session,
                sorted_by_priority_moneyboxes=sorted_by_priority_moneyboxes,
                distribution_amounts=distribution_amounts,
                distribution_description="",
            )
        )

    assert updated_moneyboxes[0]["balance"] == 140
    assert updated_moneyboxes[1]["balance"] == 5
    assert updated_moneyboxes[2]["balance"] == 5  # savings_amount = 0 but ignored in fill_mode
    assert (
        updated_moneyboxes[3]["balance"] == 0
    )  # target: None and wants 10, but fill mode ignores wises


@pytest.mark.asyncio
async def test_distribute_automated_savings_amount__normal_mode__one_moneybox_with_savings_amount_0(
        load_test_data: None,
        automated_distribution_service: AutomatedSavingsDistributionService,
) -> None:
    moneyboxes: list[dict[str, Any]] = await automated_distribution_service.db_manager.get_moneyboxes()
    sorted_by_priority_moneyboxes: list[dict[str, Any]] = sorted(
        moneyboxes, key=lambda item: item["priority"]
    )
    app_settings: AppSettings = (
        await automated_distribution_service.db_manager._get_app_settings()  # noqa: ignore  # pylint: disable=protected-access
    )

    async with automated_distribution_service.db_manager.async_sessionmaker.begin() as session:
        distribution_amounts: dict[int, int] = await automated_distribution_service.calculate_moneybox_amounts_normal_distribution(
            sorted_by_priority_moneyboxes=sorted_by_priority_moneyboxes,
            distribute_amount=app_settings.savings_amount,  # 150
        )

        updated_moneyboxes: list[dict[str, Any]] = (
            await automated_distribution_service._distribute_automated_savings_amount(
                session=session,
                sorted_by_priority_moneyboxes=sorted_by_priority_moneyboxes,
                distribution_amounts=distribution_amounts,
                distribution_description="",
            )
        )

    assert updated_moneyboxes[0]["balance"] == 135
    assert updated_moneyboxes[1]["balance"] == 5
    assert updated_moneyboxes[2]["balance"] == 0  # savings_amount = 0 and respected in normal mode
    assert (
        updated_moneyboxes[3]["balance"] == 10
    )  # savings_target=None, but respected savings_amount=10
