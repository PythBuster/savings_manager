import pytest

from src.custom_types import OverflowMoneyboxAutomatedSavingsModeType
from src.utils import calculate_months_for_reaching_savings_targets

@pytest.mark.parametrize(
    "moneyboxes, app_settings, overflow_moneybox_mode, expected",
    [
        (
            [
                {"id": 0, "balance": 50, "savings_amount": 0, "savings_target": None, "priority": 0},
                {"id": 1, "balance": 0, "savings_amount": 50, "savings_target": 100, "priority": 1}
            ],
            {"is_automated_saving_active": True, "savings_amount": 50},
            OverflowMoneyboxAutomatedSavingsModeType.FILL_UP_LIMITED_MONEYBOXES,
            {1: 1}
        ),
        (
            [
                {"id": 0, "balance": 0, "savings_amount": 0, "savings_target": None, "priority": 0},
                {"id": 1, "balance": 0, "savings_amount": 0, "savings_target": 50, "priority": 1},
                {"id": 2, "balance": 0, "savings_amount": 0, "savings_target": 100, "priority": 2}
            ],
            {"is_automated_saving_active": True, "savings_amount": 50},
            OverflowMoneyboxAutomatedSavingsModeType.ADD_TO_AUTOMATED_SAVINGS_AMOUNT,
            {1: 1, 2: 2}
        ),
        (
            [
                {"id": 0, "balance": 100, "savings_amount": 0, "savings_target": None, "priority": 0},
                {"id": 1, "balance": 0, "savings_amount": 50, "savings_target": 100, "priority": 1},
                {"id": 2, "balance": 0, "savings_amount": 50, "savings_target": 100, "priority": 2}
            ],
            {"is_automated_saving_active": True, "savings_amount": 50},
            OverflowMoneyboxAutomatedSavingsModeType.COLLECT,
            {1: 2, 2: 4}
        ),
        (
            [
                {"id": 0, "balance": 50, "savings_amount": 0, "savings_target": None, "priority": 0},
                {"id": 1, "balance": 0, "savings_amount": 50, "savings_target": 100, "priority": 1},
                {"id": 2, "balance": 0, "savings_amount": 50, "savings_target": 100, "priority": 2},
                {"id": 3, "balance": 0, "savings_amount": 50, "savings_target": 100, "priority": 3}
            ],
            {"is_automated_saving_active": True, "savings_amount": 50},
            OverflowMoneyboxAutomatedSavingsModeType.FILL_UP_LIMITED_MONEYBOXES,
            {1: 1, 2: 3, 3: 5}
        ),
        (
            [
                {"id": 0, "balance": 100, "savings_amount": 0, "savings_target": None, "priority": 0},
                {"id": 1, "balance": 0, "savings_amount": 50, "savings_target": 100, "priority": 1},
                {"id": 2, "balance": 0, "savings_amount": 50, "savings_target": 100, "priority": 2}
            ],
            {"is_automated_saving_active": True, "savings_amount": 50},
            OverflowMoneyboxAutomatedSavingsModeType.ADD_TO_AUTOMATED_SAVINGS_AMOUNT,
            {1: 2, 2: 2}
        ),
        (
            [
                {"id": 0, "balance": 200, "savings_amount": 0, "savings_target": None, "priority": 0},
                {"id": 1, "balance": 0, "savings_amount": 50, "savings_target": 100, "priority": 1},
                {"id": 2, "balance": 0, "savings_amount": 50, "savings_target": 200, "priority": 2},
                {"id": 3, "balance": 0, "savings_amount": 50, "savings_target": 50, "priority": 3}
            ],
            {"is_automated_saving_active": True, "savings_amount": 50},
            OverflowMoneyboxAutomatedSavingsModeType.COLLECT,
            {1: 2, 2: 6, 3: 7}
        ),
        (
            [
                {"id": 0, "balance": 0, "savings_amount": 0, "savings_target": None, "priority": 0},
                {"id": 1, "balance": 0, "savings_amount": 50, "savings_target": 100, "priority": 1},
                {"id": 2, "balance": 0, "savings_amount": 0, "savings_target": 50, "priority": 2}
            ],
            {"is_automated_saving_active": True, "savings_amount": 50},
            OverflowMoneyboxAutomatedSavingsModeType.FILL_UP_LIMITED_MONEYBOXES,
            {1: 2, 2: -1}
        ),
        (
            [
                {"id": 0, "balance": 50, "savings_amount": 0, "savings_target": None, "priority": 0},
                {"id": 1, "balance": 0, "savings_amount": 50, "savings_target": 100, "priority": 1},
                {"id": 2, "balance": 0, "savings_amount": 50, "savings_target": 100, "priority": 2}
            ],
            {"is_automated_saving_active": True, "savings_amount": 50},
            OverflowMoneyboxAutomatedSavingsModeType.ADD_TO_AUTOMATED_SAVINGS_AMOUNT,
            {1: 2, 2: 3}
        ),
        (
                [
                    {"id": 0, "balance": 0, "savings_amount": 0, "savings_target": None, "priority": 0},
                    {"id": 1, "balance": 0, "savings_amount": 50, "savings_target": 100, "priority": 1},
                    {"id": 2, "balance": 0, "savings_amount": 50, "savings_target": None, "priority": 2},
                    {"id": 3, "balance": 0, "savings_amount": 50, "savings_target": 100, "priority": 3},
                ],
                {"is_automated_saving_active": True, "savings_amount": 50},
                OverflowMoneyboxAutomatedSavingsModeType.ADD_TO_AUTOMATED_SAVINGS_AMOUNT,
                {1: 2, 3: -1}
        ),
        (
            [
                {"id": 0, "balance": 200, "savings_amount": 0, "savings_target": None, "priority": 0},
                {"id": 1, "balance": 0, "savings_amount": 100, "savings_target": 100, "priority": 1},
                {"id": 2, "balance": 0, "savings_amount": 100, "savings_target": None, "priority": 2},
                {"id": 3, "balance": 0, "savings_amount": 50, "savings_target": 100, "priority": 3},
            ],
            {"is_automated_saving_active": True, "savings_amount": 100},
            OverflowMoneyboxAutomatedSavingsModeType.ADD_TO_AUTOMATED_SAVINGS_AMOUNT,
            {1: 1, 3: 2}
        ),
        (
                [
                    {"id": 0, "balance": 200, "savings_amount": 0, "savings_target": None, "priority": 0},
                    {"id": 1, "balance": 0, "savings_amount": 100, "savings_target": 100, "priority": 1},
                    {"id": 2, "balance": 0, "savings_amount": 100, "savings_target": None, "priority": 2},
                    {"id": 3, "balance": 0, "savings_amount": 50, "savings_target": 100, "priority": 3},
                ],
                {"is_automated_saving_active": True, "savings_amount": 100},
                OverflowMoneyboxAutomatedSavingsModeType.FILL_UP_LIMITED_MONEYBOXES,
                {1: 1, 3: 1}
        ),
        (
                [
                    {"id": 0, "balance": 0, "savings_amount": 0, "savings_target": None, "priority": 0},
                    {"id": 1, "balance": 0, "savings_amount": 50, "savings_target": 100, "priority": 1},
                    {"id": 2, "balance": 0, "savings_amount": 50, "savings_target": 100, "priority": 2},
                    {"id": 3, "balance": 0, "savings_amount": 50, "savings_target": None, "priority": 3},
                ],
                {"is_automated_saving_active": True, "savings_amount": 50},
                OverflowMoneyboxAutomatedSavingsModeType.ADD_TO_AUTOMATED_SAVINGS_AMOUNT,
                {1: 2, 2: 4}
        ),
        (
                [
                    {"id": 0, "balance": 0, "savings_amount": 0, "savings_target": None, "priority": 0},
                    {"id": 1, "balance": 0, "savings_amount": 50, "savings_target": None, "priority": 1},
                    {"id": 2, "balance": 0, "savings_amount": 50, "savings_target": 100, "priority": 2},
                    {"id": 3, "balance": 0, "savings_amount": 50, "savings_target": 100, "priority": 3},
                ],
                {"is_automated_saving_active": True, "savings_amount": 50},
                OverflowMoneyboxAutomatedSavingsModeType.ADD_TO_AUTOMATED_SAVINGS_AMOUNT,
                {2: -1, 3: -1}
        ),
        (
                [
                    {"id": 0, "balance": 0, "savings_amount": 0, "savings_target": None, "priority": 0},
                    {"id": 1, "balance": 0, "savings_amount": 50, "savings_target": None, "priority": 1},
                    {"id": 2, "balance": 0, "savings_amount": 50, "savings_target": 100, "priority": 2},
                    {"id": 3, "balance": 0, "savings_amount": 50, "savings_target": 100, "priority": 3},
                ],
                {"is_automated_saving_active": True, "savings_amount": 100},
                OverflowMoneyboxAutomatedSavingsModeType.ADD_TO_AUTOMATED_SAVINGS_AMOUNT,
                {2: 2, 3: 4}
        ),
    ]
)
def test_calculate_months_for_reaching_savings_targets(moneyboxes, app_settings, overflow_moneybox_mode, expected):
    result = calculate_months_for_reaching_savings_targets(moneyboxes, app_settings, overflow_moneybox_mode)
    for moneybox in moneyboxes[1:]:
        if moneybox["savings_target"] is not None:
            if moneybox["id"] in result and result[moneybox["id"]]:
                assert result[moneybox["id"]][-1].month == expected[moneybox["id"]]