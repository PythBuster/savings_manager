"""All tests specific to calculate_months_for_reaching_savings_targets are located here.
This is because the function is essential and has caused numerous issues."""

from typing import Any

import pytest

from src.custom_types import OverflowMoneyboxAutomatedSavingsModeType
from src.savings_distribution.automated_savings_distribution import (
    AutomatedSavingsDistributionService,
)


@pytest.mark.parametrize(
    "moneyboxes, app_settings, overflow_moneybox_mode, expected",
    [
        (  # 1
            [
                {
                    "id": 0,
                    "balance": 50,
                    "savings_amount": 0,
                    "savings_target": None,
                    "priority": 0,
                },
                {"id": 1, "balance": 0, "savings_amount": 50, "savings_target": 100, "priority": 1},
            ],
            {"is_automated_saving_active": True, "savings_amount": 50},
            OverflowMoneyboxAutomatedSavingsModeType.FILL_UP_LIMITED_MONEYBOXES,
            {1: 1},
        ),
        (  # 2
            [
                {"id": 0, "balance": 0, "savings_amount": 0, "savings_target": None, "priority": 0},
                {"id": 1, "balance": 0, "savings_amount": 50, "savings_target": 50, "priority": 1},
                {"id": 2, "balance": 0, "savings_amount": 50, "savings_target": 100, "priority": 2},
            ],
            {"is_automated_saving_active": True, "savings_amount": 50},
            OverflowMoneyboxAutomatedSavingsModeType.ADD_TO_AUTOMATED_SAVINGS_AMOUNT,
            {1: 1, 2: 3},
        ),
        (  # 3
            [
                {
                    "id": 0,
                    "balance": 100,
                    "savings_amount": 0,
                    "savings_target": None,
                    "priority": 0,
                },
                {"id": 1, "balance": 0, "savings_amount": 50, "savings_target": 100, "priority": 1},
                {"id": 2, "balance": 0, "savings_amount": 50, "savings_target": 100, "priority": 2},
            ],
            {"is_automated_saving_active": True, "savings_amount": 50},
            OverflowMoneyboxAutomatedSavingsModeType.COLLECT,
            {1: 2, 2: 4},
        ),
        (  # 4
            [
                {
                    "id": 0,
                    "balance": 50,
                    "savings_amount": 0,
                    "savings_target": None,
                    "priority": 0,
                },
                {"id": 1, "balance": 0, "savings_amount": 50, "savings_target": 100, "priority": 1},
                {"id": 2, "balance": 0, "savings_amount": 50, "savings_target": 100, "priority": 2},
                {"id": 3, "balance": 0, "savings_amount": 50, "savings_target": 100, "priority": 3},
            ],
            {"is_automated_saving_active": True, "savings_amount": 50},
            OverflowMoneyboxAutomatedSavingsModeType.FILL_UP_LIMITED_MONEYBOXES,
            {1: 1, 2: 3, 3: 5},
        ),
        (  # 5
            [
                {
                    "id": 0,
                    "balance": 100,
                    "savings_amount": 0,
                    "savings_target": None,
                    "priority": 0,
                },
                {"id": 1, "balance": 0, "savings_amount": 50, "savings_target": 100, "priority": 1},
                {"id": 2, "balance": 0, "savings_amount": 50, "savings_target": 100, "priority": 2},
            ],
            {"is_automated_saving_active": True, "savings_amount": 50},
            OverflowMoneyboxAutomatedSavingsModeType.ADD_TO_AUTOMATED_SAVINGS_AMOUNT,
            {1: 2, 2: 2},
        ),
        (  # 6
            [
                {
                    "id": 0,
                    "balance": 200,
                    "savings_amount": 0,
                    "savings_target": None,
                    "priority": 0,
                },
                {"id": 1, "balance": 0, "savings_amount": 50, "savings_target": 100, "priority": 1},
                {"id": 2, "balance": 0, "savings_amount": 50, "savings_target": 200, "priority": 2},
                {"id": 3, "balance": 0, "savings_amount": 50, "savings_target": 50, "priority": 3},
            ],
            {"is_automated_saving_active": True, "savings_amount": 50},
            OverflowMoneyboxAutomatedSavingsModeType.COLLECT,
            {1: 2, 2: 6, 3: 7},
        ),
        (  # 7
            [
                {"id": 0, "balance": 0, "savings_amount": 0, "savings_target": None, "priority": 0},
                {"id": 1, "balance": 0, "savings_amount": 50, "savings_target": 100, "priority": 1},
                {"id": 2, "balance": 0, "savings_amount": 0, "savings_target": 50, "priority": 2},
            ],
            {"is_automated_saving_active": True, "savings_amount": 50},
            OverflowMoneyboxAutomatedSavingsModeType.FILL_UP_LIMITED_MONEYBOXES,
            {1: 2, 2: -1},
        ),
        (  # 8
            [
                {
                    "id": 0,
                    "balance": 50,
                    "savings_amount": 0,
                    "savings_target": None,
                    "priority": 0,
                },
                {"id": 1, "balance": 0, "savings_amount": 50, "savings_target": 100, "priority": 1},
                {"id": 2, "balance": 0, "savings_amount": 50, "savings_target": 100, "priority": 2},
            ],
            {"is_automated_saving_active": True, "savings_amount": 50},
            OverflowMoneyboxAutomatedSavingsModeType.ADD_TO_AUTOMATED_SAVINGS_AMOUNT,
            {1: 2, 2: 3},
        ),
        (  # 9
            [
                {"id": 0, "balance": 0, "savings_amount": 0, "savings_target": None, "priority": 0},
                {"id": 1, "balance": 0, "savings_amount": 50, "savings_target": 100, "priority": 1},
                {
                    "id": 2,
                    "balance": 0,
                    "savings_amount": 50,
                    "savings_target": None,
                    "priority": 2,
                },
                {"id": 3, "balance": 0, "savings_amount": 50, "savings_target": 100, "priority": 3},
            ],
            {"is_automated_saving_active": True, "savings_amount": 50},
            OverflowMoneyboxAutomatedSavingsModeType.ADD_TO_AUTOMATED_SAVINGS_AMOUNT,
            {1: 2, 3: -1},
        ),
        (  # 10
            [
                {
                    "id": 0,
                    "balance": 200,
                    "savings_amount": 0,
                    "savings_target": None,
                    "priority": 0,
                },
                {
                    "id": 1,
                    "balance": 0,
                    "savings_amount": 100,
                    "savings_target": 100,
                    "priority": 1,
                },
                {
                    "id": 2,
                    "balance": 0,
                    "savings_amount": 100,
                    "savings_target": None,
                    "priority": 2,
                },
                {"id": 3, "balance": 0, "savings_amount": 50, "savings_target": 100, "priority": 3},
            ],
            {"is_automated_saving_active": True, "savings_amount": 100},
            OverflowMoneyboxAutomatedSavingsModeType.ADD_TO_AUTOMATED_SAVINGS_AMOUNT,
            {1: 1, 3: 2},
        ),
        (  # 11
            [
                {
                    "id": 0,
                    "balance": 200,
                    "savings_amount": 0,
                    "savings_target": None,
                    "priority": 0,
                },
                {
                    "id": 1,
                    "balance": 0,
                    "savings_amount": 100,
                    "savings_target": 100,
                    "priority": 1,
                },
                {
                    "id": 2,
                    "balance": 0,
                    "savings_amount": 100,
                    "savings_target": None,
                    "priority": 2,
                },
                {"id": 3, "balance": 0, "savings_amount": 50, "savings_target": 100, "priority": 3},
            ],
            {"is_automated_saving_active": True, "savings_amount": 100},
            OverflowMoneyboxAutomatedSavingsModeType.FILL_UP_LIMITED_MONEYBOXES,
            {1: 1, 3: 1},
        ),
        (  # 12
            [
                {"id": 0, "balance": 0, "savings_amount": 0, "savings_target": None, "priority": 0},
                {"id": 1, "balance": 0, "savings_amount": 50, "savings_target": 100, "priority": 1},
                {"id": 2, "balance": 0, "savings_amount": 50, "savings_target": 100, "priority": 2},
                {
                    "id": 3,
                    "balance": 0,
                    "savings_amount": 50,
                    "savings_target": None,
                    "priority": 3,
                },
                {
                    "id": 4,
                    "balance": 0,
                    "savings_amount": 50,
                    "savings_target": None,
                    "priority": 4,
                },
            ],
            {"is_automated_saving_active": True, "savings_amount": 200},
            OverflowMoneyboxAutomatedSavingsModeType.ADD_TO_AUTOMATED_SAVINGS_AMOUNT,
            {1: 2, 2: 2},
        ),
        (  # 13
            [
                {"id": 0, "balance": 0, "savings_amount": 0, "savings_target": None, "priority": 0},
                {
                    "id": 1,
                    "balance": 0,
                    "savings_amount": 10000,
                    "savings_target": None,
                    "priority": 1,
                },
                {"id": 2, "balance": 0, "savings_amount": 1, "savings_target": 100, "priority": 2},
                {
                    "id": 3,
                    "balance": 0,
                    "savings_amount": 100,
                    "savings_target": None,
                    "priority": 3,
                },
                {
                    "id": 4,
                    "balance": 0,
                    "savings_amount": 100,
                    "savings_target": 100,
                    "priority": 4,
                },
            ],
            {"is_automated_saving_active": True, "savings_amount": 10100},
            OverflowMoneyboxAutomatedSavingsModeType.COLLECT,
            {2: 100, 4: -1},
        ),
        (  # 14
            [
                {"id": 0, "balance": 0, "savings_amount": 0, "savings_target": None, "priority": 0},
                {
                    "id": 1,
                    "balance": 0,
                    "savings_amount": 10000,
                    "savings_target": None,
                    "priority": 1,
                },
                {"id": 2, "balance": 0, "savings_amount": 1, "savings_target": 100, "priority": 2},
                {
                    "id": 3,
                    "balance": 0,
                    "savings_amount": 100,
                    "savings_target": None,
                    "priority": 3,
                },
                {
                    "id": 4,
                    "balance": 0,
                    "savings_amount": 100,
                    "savings_target": 100,
                    "priority": 4,
                },
            ],
            {"is_automated_saving_active": True, "savings_amount": 10101},
            OverflowMoneyboxAutomatedSavingsModeType.COLLECT,
            {2: 100, 4: 200},
        ),
        (  # 15
            [
                {"id": 0, "balance": 0, "savings_amount": 0, "savings_target": None, "priority": 0},
                {"id": 1, "balance": 0, "savings_amount": 0, "savings_target": 50, "priority": 1},
                {"id": 2, "balance": 0, "savings_amount": 0, "savings_target": 100, "priority": 2},
            ],
            {"is_automated_saving_active": True, "savings_amount": 50},
            OverflowMoneyboxAutomatedSavingsModeType.ADD_TO_AUTOMATED_SAVINGS_AMOUNT,
            {1: -1, 2: -1},
        ),
    ],
)
async def test_calculate_months_for_reaching_savings_targets(
    moneyboxes: list[dict[str, Any]],
    app_settings: dict[str, Any],
    overflow_moneybox_mode: OverflowMoneyboxAutomatedSavingsModeType,
    expected: dict[str, Any],
) -> None:
    result = await AutomatedSavingsDistributionService.calculate_savings_forecast(
        moneyboxes, app_settings, overflow_moneybox_mode
    )
    for moneybox in moneyboxes[1:]:
        if moneybox["savings_target"] is not None:
            if moneybox["id"] in result and result[moneybox["id"]]:
                assert result[moneybox["id"]][-1].month == expected[moneybox["id"]]
