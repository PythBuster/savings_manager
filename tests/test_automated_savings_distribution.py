"""All automated_savings_distribution test are located here."""

from typing import Any

import pytest

from src.custom_types import OverflowMoneyboxAutomatedSavingsModeType
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

    last_transaction_log = overflow_moneybox_transaction_logs[1]
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

    last_transaction_log = overflow_moneybox_transaction_logs[0]
    expected_description = "Fill-Mode: Automated Savings."
    assert last_transaction_log["description"] == expected_description

    last_transaction_log = overflow_moneybox_transaction_logs[1]
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

    last_transaction_log = overflow_moneybox_transaction_logs[0]
    expected_description = "Ratio-Mode: Automated Savings."
    assert last_transaction_log["description"] == expected_description


@pytest.mark.asyncio
async def test_automated_savings_overflow_moneybox_mode_ratio_prioritized(
    load_test_data: None,  # pylint: disable=unused-argument
    automated_distribution_service,
) -> None:
    """
    Test the RATIO_PRIORITIZED overflow moneybox mode.
    Ensures savings are distributed by ratio and adjusted by priority,
    with respect to savings_target constraints.
    """

    await automated_distribution_service.run_automated_savings_distribution()

    moneyboxes = await automated_distribution_service.db_manager.get_moneyboxes()

    expected_data = {
        "Overflow Moneybox": 1,
        "Test Box 1": 3,
        "Test Box 2": 4,
        "Test Box 3": 5,
    }

    for moneybox in moneyboxes:
        assert (
            moneybox["balance"] == expected_data[moneybox["name"]]
        ), f"{moneybox['name']} has unexpected balance"

    overflow_moneybox = (
        await automated_distribution_service.db_manager._get_overflow_moneybox()  # pylint: disable=protected-access
    )
    overflow_moneybox_transaction_logs = (
        await automated_distribution_service.db_manager.get_transaction_logs(
            moneybox_id=overflow_moneybox.id,
        )
    )

    last_transaction_log = overflow_moneybox_transaction_logs[0]
    expected_description = "Ratio-Prioritized-Mode: Automated Savings."
    assert (
        last_transaction_log["description"] == expected_description
    ), f"Unexpected transaction description: {last_transaction_log['description']}"


@pytest.mark.asyncio
async def test_automated_savings_overflow_moneybox_mode_ratio_prioritized__zero_distribution(
    load_test_data: None,  # pylint: disable=unused-argument
    automated_distribution_service,
) -> None:
    """
    Test the RATIO_PRIORITIZED mode when savings_amount is 0.
    No distribution should occur; all balances should remain unchanged.
    """

    await automated_distribution_service.run_automated_savings_distribution()

    moneyboxes = await automated_distribution_service.db_manager.get_moneyboxes()

    expected_data = {
        "Overflow Moneybox": 0,
        "Test Box 1": 0,
        "Test Box 2": 0,
        "Test Box 3": 0,
    }

    for moneybox in moneyboxes:
        assert (
            moneybox["balance"] == expected_data[moneybox["name"]]
        ), f"{moneybox['name']} has unexpected balance for zero distribution"

    overflow_moneybox = (
        await automated_distribution_service.db_manager._get_overflow_moneybox()  # pylint: disable=protected-access
    )
    overflow_moneybox_transaction_logs = (
        await automated_distribution_service.db_manager.get_transaction_logs(
            moneybox_id=overflow_moneybox.id,
        )
    )

    assert len(overflow_moneybox_transaction_logs) == 0


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


def create_test_moneyboxes(overflow_balance: int) -> list[dict[str, Any]]:
    return [
        {  # overflow moneybox
            "id": 1,
            "priority": 0,
            "balance": overflow_balance,
            "savings_amount": 0,
            "savings_target": None,
        },
        {  # reached at init
            "id": 2,
            "priority": 1,
            "balance": 1000,
            "savings_amount": 500,
            "savings_target": 1000,
        },
        {  # will reach target over time: needs 3 × 1000 => last payment in month 2 (0-based)
            "id": 3,
            "priority": 2,
            "balance": 0,
            "savings_amount": 1000,
            "savings_target": 3000,
        },
        {  # no target
            "id": 4,
            "priority": 3,
            "balance": 0,
            "savings_amount": 1000,
            "savings_target": None,
        },
        {  # unreachable
            "id": 5,
            "priority": 4,
            "balance": 0,
            "savings_amount": 0,
            "savings_target": 1000,
        },
    ]


@pytest.mark.parametrize(
    "savings_amount, overflow_balance, mode, expected",
    [
        # COLLECT
        (1000, 0, OverflowMoneyboxAutomatedSavingsModeType.COLLECT, {2: 0, 3: 3, 4: None, 5: None}),
        (0, 0, OverflowMoneyboxAutomatedSavingsModeType.COLLECT, {2: 0, 3: None, 4: None, 5: None}),
        (
            0,
            250,
            OverflowMoneyboxAutomatedSavingsModeType.COLLECT,
            {2: 0, 3: None, 4: None, 5: None},
        ),
        (
            1000,
            3000,
            OverflowMoneyboxAutomatedSavingsModeType.COLLECT,
            {2: 0, 3: 3, 4: None, 5: None},
        ),
        # ADD
        (
            1000,
            0,
            OverflowMoneyboxAutomatedSavingsModeType.ADD_TO_AUTOMATED_SAVINGS_AMOUNT,
            {2: 0, 3: 3, 4: None, 5: None},
        ),
        (
            0,
            0,
            OverflowMoneyboxAutomatedSavingsModeType.ADD_TO_AUTOMATED_SAVINGS_AMOUNT,
            {2: 0, 3: None, 4: None, 5: None},
        ),
        (
            0,
            250,
            OverflowMoneyboxAutomatedSavingsModeType.ADD_TO_AUTOMATED_SAVINGS_AMOUNT,
            {2: 0, 3: None, 4: None, 5: None},
        ),
        (
            1000,
            3000,
            OverflowMoneyboxAutomatedSavingsModeType.ADD_TO_AUTOMATED_SAVINGS_AMOUNT,
            {2: 0, 3: 3, 4: None, 5: None},
        ),
        # FILL
        (
            1000,
            0,
            OverflowMoneyboxAutomatedSavingsModeType.FILL_UP_LIMITED_MONEYBOXES,
            {2: 0, 3: 3, 4: None, 5: None},
        ),
        (
            0,
            0,
            OverflowMoneyboxAutomatedSavingsModeType.FILL_UP_LIMITED_MONEYBOXES,
            {2: 0, 3: None, 4: None, 5: None},
        ),
        (
            0,
            250,
            OverflowMoneyboxAutomatedSavingsModeType.FILL_UP_LIMITED_MONEYBOXES,
            {2: 0, 3: None, 4: None, 5: None},
        ),
        (
            1000,
            3000,
            OverflowMoneyboxAutomatedSavingsModeType.FILL_UP_LIMITED_MONEYBOXES,
            {2: 0, 3: 1, 4: None, 5: 1},
        ),
    ],
)
async def test_calculate_savings_forecast__all_combinations(
    savings_amount: int,
    overflow_balance: int,
    mode: OverflowMoneyboxAutomatedSavingsModeType,
    expected: dict[int, int | None],
) -> None:
    result = await AutomatedSavingsDistributionService.calculate_savings_forecast(
        moneyboxes=create_test_moneyboxes(overflow_balance),
        app_settings={
            "is_automated_saving_active": True,
            "savings_amount": savings_amount,
        },
        overflow_moneybox_mode=mode,
    )

    assert 1 not in result  # overflow moneybox is excluded from result

    for moneybox_id, expected_month in expected.items():
        assert moneybox_id in result
        last_month = result[moneybox_id][-1].month
        if expected_month is None:
            assert (
                last_month == -1
            ), f"Moneybox {moneybox_id}: expected month {expected_month}, got {last_month}"
        else:
            assert (
                last_month == expected_month
            ), f"Moneybox {moneybox_id}: expected month {expected_month}, got {last_month}"
