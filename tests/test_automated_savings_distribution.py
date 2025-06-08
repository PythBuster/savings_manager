"""All automated_savings_distribution test are located here."""

from typing import Any

import pytest

from src.db.models import AppSettings
from src.savings_distribution.automated_savings_distribution import (
    AutomatedSavingsDistributionService,
)


@pytest.mark.asyncio
async def test_automated_savings_overflow_moneybox_mode_collect(
    load_test_data: None,  # pylint: disable=unused-argument
    automated_distribution_service: AutomatedSavingsDistributionService,
) -> None:
    await automated_distribution_service.run_automated_savings_distribution()

    moneyboxes = await automated_distribution_service.db_manager.get_moneyboxes()
    expected_data = {
        "Overflow Moneybox": 105,
        "Test Box 1": 5,
        "Test Box 2": 5,
        "Test Box 3": 15,
        "Test Box 4": 20,
        "Test Box 5": 0,
        "Test Box 6": 0,
    }

    for moneybox in moneyboxes:
        assert moneybox["balance"] == expected_data[moneybox["name"]]

    # >>>  test case for bug: issue #71
    # - test if correct overflow moneybox mode is set in transaction log of overflow moneybox
    overflow_moneybox = (
        await automated_distribution_service.db_manager._get_overflow_moneybox()  # noqa: typing  # pylint:disable=protected-access
    )
    overflow_moneybox_transaction_logs = (
        await automated_distribution_service.db_manager.get_transaction_logs(
            moneybox_id=overflow_moneybox.id,
        )
    )

    last_transaction_log = overflow_moneybox_transaction_logs[-1]
    expected_description = "Automated Savings."
    assert last_transaction_log["description"] == expected_description
    # <<<


@pytest.mark.asyncio
async def test_automated_savings_overflow_moneybox_mode_add_to_amount(
    load_test_data: None,  # pylint: disable=unused-argument
    automated_distribution_service: AutomatedSavingsDistributionService,
) -> None:
    await automated_distribution_service.run_automated_savings_distribution()

    moneyboxes = await automated_distribution_service.db_manager.get_moneyboxes()
    expected_data = {
        "Overflow Moneybox": 105,
        "Test Box 1": 5,
        "Test Box 2": 5,
        "Test Box 3": 15,
        "Test Box 4": 20,
        "Test Box 5": 0,
        "Test Box 6": 0,
    }

    for moneybox in moneyboxes:
        assert moneybox["balance"] == expected_data[moneybox["name"]]

    # >>>  test case for bug: issue #71
    # - test if correct overflow moneybox mode is set in transaction log of overflow moneybox
    overflow_moneybox = (
        await automated_distribution_service.db_manager._get_overflow_moneybox()  # noqa: typing  # pylint:disable=protected-access
    )
    overflow_moneybox_transaction_logs = (
        await automated_distribution_service.db_manager.get_transaction_logs(
            moneybox_id=overflow_moneybox.id,
        )
    )

    last_transaction_log = overflow_moneybox_transaction_logs[-1]
    expected_description = "Automated Savings with Add-Mode."
    assert last_transaction_log["description"] == expected_description
    # <<<


@pytest.mark.asyncio
async def test_automated_savings_overflow_moneybox_mode_fill_up(
    load_test_data: None,  # pylint: disable=unused-argument
    automated_distribution_service: AutomatedSavingsDistributionService,
) -> None:
    await automated_distribution_service.run_automated_savings_distribution()

    moneyboxes = await automated_distribution_service.db_manager.get_moneyboxes()
    expected_data = {
        "Overflow Moneybox": 75,
        "Test Box 1": 5,
        "Test Box 2": 5,
        "Test Box 3": 15,
        "Test Box 4": 50,
        "Test Box 5": 0,
        "Test Box 6": 0,
    }

    for moneybox in moneyboxes:
        assert moneybox["balance"] == expected_data[moneybox["name"]]

    # >>> test case for bug: issue #71
    # - test if correct overflow moneybox mode is set in transaction log of overflow moneybox
    overflow_moneybox = (
        await automated_distribution_service.db_manager._get_overflow_moneybox()  # noqa: typing  # pylint:disable=protected-access
    )
    overflow_moneybox_transaction_logs = (
        await automated_distribution_service.db_manager.get_transaction_logs(
            moneybox_id=overflow_moneybox.id,
        )
    )

    last_transaction_log = overflow_moneybox_transaction_logs[-1]
    expected_description = "Fill-Mode: Automated Savings."
    assert last_transaction_log["description"] == expected_description
    # <<<


@pytest.mark.asyncio
async def test_automated_savings_overflow_moneybox_mode_ratio(
    load_test_data: None,  # pylint: disable=unused-argument
    automated_distribution_service: AutomatedSavingsDistributionService,
) -> None:
    await automated_distribution_service.run_automated_savings_distribution()

    moneyboxes = await automated_distribution_service.db_manager.get_moneyboxes()
    expected_data = {
        "Overflow Moneybox": 57,
        "Test Box 1": 5,
        "Test Box 2": 5,
        "Test Box 3": 36,
        "Test Box 4": 47,
        "Test Box 5": 0,
        "Test Box 6": 0,
    }

    for moneybox in moneyboxes:
        assert moneybox["balance"] == expected_data[moneybox["name"]]

    overflow_moneybox = (
        await automated_distribution_service.db_manager._get_overflow_moneybox()  # noqa: typing  # pylint:disable=protected-access
    )
    overflow_moneybox_transaction_logs = (
        await automated_distribution_service.db_manager.get_transaction_logs(
            moneybox_id=overflow_moneybox.id,
        )
    )

    last_transaction_log = overflow_moneybox_transaction_logs[-1]
    expected_description = "Ratio-Mode: Automated Savings."
    assert last_transaction_log["description"] == expected_description


@pytest.mark.asyncio
async def test_automated_savings_overflow_moneybox_mode_ratio__only_overflow_moneybox(
    load_test_data: None,  # pylint: disable=unused-argument
    automated_distribution_service: AutomatedSavingsDistributionService,
) -> None:
    await automated_distribution_service.run_automated_savings_distribution()

    moneyboxes = await automated_distribution_service.db_manager.get_moneyboxes()
    expected_data = {
        "Overflow Moneybox": 150,
    }

    for moneybox in moneyboxes:
        assert moneybox["balance"] == expected_data[moneybox["name"]]

    assert len(moneyboxes) == 1
    assert moneyboxes[0]["balance"] == 150


@pytest.mark.asyncio
async def test_automated_savings_overflow_moneybox_mode_collect__only_overflow_moneybox(
    load_test_data: None,  # pylint: disable=unused-argument
    automated_distribution_service: AutomatedSavingsDistributionService,
) -> None:
    await automated_distribution_service.run_automated_savings_distribution()

    moneyboxes = await automated_distribution_service.db_manager.get_moneyboxes()
    expected_data = {
        "Overflow Moneybox": 150,
    }

    for moneybox in moneyboxes:
        assert moneybox["balance"] == expected_data[moneybox["name"]]

    assert len(moneyboxes) == 1
    assert moneyboxes[0]["balance"] == 150


@pytest.mark.asyncio
async def test_automated_savings_overflow_moneybox_mode_add__only_overflow_moneybox(
    load_test_data: None,  # pylint: disable=unused-argument
    automated_distribution_service: AutomatedSavingsDistributionService,
) -> None:
    await automated_distribution_service.run_automated_savings_distribution()

    moneyboxes = await automated_distribution_service.db_manager.get_moneyboxes()
    expected_data = {
        "Overflow Moneybox": 150,
    }

    for moneybox in moneyboxes:
        assert moneybox["balance"] == expected_data[moneybox["name"]]

    assert len(moneyboxes) == 1
    assert moneyboxes[0]["balance"] == 150


@pytest.mark.asyncio
async def test_automated_savings_overflow_moneybox_mode_fill__only_overflow_moneybox(
    load_test_data: None,  # pylint: disable=unused-argument
    automated_distribution_service: AutomatedSavingsDistributionService,
) -> None:
    await automated_distribution_service.run_automated_savings_distribution()

    moneyboxes = await automated_distribution_service.db_manager.get_moneyboxes()
    expected_data = {
        "Overflow Moneybox": 150,
    }

    for moneybox in moneyboxes:
        assert moneybox["balance"] == expected_data[moneybox["name"]]

    assert len(moneyboxes) == 1
    assert moneyboxes[0]["balance"] == 150


@pytest.mark.asyncio
async def test_distribute_automated_savings_amount__amount_0(
    load_test_data: None,  # pylint: disable=unused-argument
    automated_distribution_service: AutomatedSavingsDistributionService,
) -> None:
    distribute_amount: int = 0
    moneyboxes: list[dict[str, Any]] = (
        await automated_distribution_service.db_manager.get_moneyboxes()
    )
    sorted_by_priority_moneyboxes: list[dict[str, Any]] = sorted(
        moneyboxes, key=lambda item: item["priority"]
    )

    async with automated_distribution_service.db_manager.async_sessionmaker.begin() as session:
        # calculate savings_distribution amounts for "normal" savings_distribution case
        distribution_amounts: dict[int, int] = (
            await automated_distribution_service.calculate_moneybox_amounts_normal_distribution(
                sorted_by_priority_moneyboxes=sorted_by_priority_moneyboxes,
                distribute_amount=distribute_amount,
            )
        )

        updated_moneyboxes: list[dict[str, Any]] = (
            await automated_distribution_service._distribute_automated_savings_amount(  # type: ignore  # noqa: ignore  # pylint:disable=line-too-long, protected-access
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
    moneyboxes: list[dict[str, Any]] = (
        await automated_distribution_service.db_manager.get_moneyboxes()
    )
    sorted_by_priority_moneyboxes: list[dict[str, Any]] = sorted(
        moneyboxes, key=lambda item: item["priority"]
    )

    async with automated_distribution_service.db_manager.async_sessionmaker.begin() as session:
        distribution_amounts: dict[int, int] = (
            await automated_distribution_service.calculate_moneybox_amounts_normal_distribution(
                sorted_by_priority_moneyboxes=sorted_by_priority_moneyboxes,
                distribute_amount=distribute_amount,
            )
        )

        updated_moneyboxes: list[dict[str, Any]] = (
            await automated_distribution_service._distribute_automated_savings_amount(  # type: ignore  # noqa: ignore  # pylint:disable=line-too-long, protected-access
                session=session,
                sorted_by_priority_moneyboxes=sorted_by_priority_moneyboxes,
                distribution_amounts=distribution_amounts,
                distribution_description="",
            )
        )

    assert updated_moneyboxes == sorted_by_priority_moneyboxes


@pytest.mark.asyncio
async def test_distribute_automated_savings_amount__fill_mode__one_moneybox_with_savings_target_none(  # noqa: ignore  # pylint: disable=line-too-long
    load_test_data: None,  # pylint: disable=unused-argument
    automated_distribution_service: AutomatedSavingsDistributionService,
) -> None:
    moneyboxes: list[dict[str, Any]] = (
        await automated_distribution_service.db_manager.get_moneyboxes()
    )
    sorted_by_priority_moneyboxes: list[dict[str, Any]] = sorted(
        moneyboxes, key=lambda item: item["priority"]
    )
    app_settings: AppSettings = (
        await automated_distribution_service.db_manager._get_app_settings()  # noqa: ignore  # pylint: disable=protected-access
    )

    async with automated_distribution_service.db_manager.async_sessionmaker.begin() as session:
        distribution_amounts: dict[int, int] = (
            await automated_distribution_service.calculate_moneybox_amounts_fill_distribution(
                sorted_by_priority_moneyboxes=sorted_by_priority_moneyboxes,
                distribute_amount=app_settings.savings_amount,  # 150
            )
        )

        updated_moneyboxes: list[dict[str, Any]] = (
            await automated_distribution_service._distribute_automated_savings_amount(  # type: ignore  # noqa: ignore  # pylint:disable=line-too-long, protected-access
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
    load_test_data: None,  # pylint: disable=unused-argument
    automated_distribution_service: AutomatedSavingsDistributionService,
) -> None:
    moneyboxes: list[dict[str, Any]] = (
        await automated_distribution_service.db_manager.get_moneyboxes()
    )
    sorted_by_priority_moneyboxes: list[dict[str, Any]] = sorted(
        moneyboxes, key=lambda item: item["priority"]
    )
    app_settings: AppSettings = (
        await automated_distribution_service.db_manager._get_app_settings()  # noqa: ignore  # pylint: disable=protected-access
    )

    async with automated_distribution_service.db_manager.async_sessionmaker.begin() as session:
        distribution_amounts: dict[int, int] = (
            await automated_distribution_service.calculate_moneybox_amounts_normal_distribution(
                sorted_by_priority_moneyboxes=sorted_by_priority_moneyboxes,
                distribute_amount=app_settings.savings_amount,  # 150
            )
        )

        updated_moneyboxes: list[dict[str, Any]] = (
            await automated_distribution_service._distribute_automated_savings_amount(  # type: ignore  # noqa: ignore  # pylint:disable=line-too-long, protected-access
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
