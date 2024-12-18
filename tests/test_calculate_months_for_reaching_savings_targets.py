import pytest

from src.custom_types import OverflowMoneyboxAutomatedSavingsModeType
from src.utils import calculate_months_for_reaching_savings_targets

@pytest.mark.parametrize(
    "moneyboxes, app_settings, overflow_moneybox_mode, expected",
    [

        (
                [
                    {"id": 0, "balance": 0, "savings_amount": 0, "savings_target": None, "priority": 0},
                    {"id": 1, "balance": 0, "savings_amount": 50, "savings_target": 100, "priority": 1},
                    {"id": 2, "balance": 0, "savings_amount": 50, "savings_target": 100, "priority": 2},
                    {"id": 3, "balance": 0, "savings_amount": 50, "savings_target": None, "priority": 3},
                    {"id": 4, "balance": 0, "savings_amount": 50, "savings_target": None, "priority": 4},
                ],
                {"is_automated_saving_active": True, "savings_amount": 200},
                OverflowMoneyboxAutomatedSavingsModeType.ADD_TO_AUTOMATED_SAVINGS_AMOUNT,
                {1: 2, 2: 2}
        ),
    ]
)
def test_calculate_months_for_reaching_savings_targets(moneyboxes, app_settings, overflow_moneybox_mode, expected):
    result = calculate_months_for_reaching_savings_targets(moneyboxes, app_settings, overflow_moneybox_mode)
    for moneybox in moneyboxes[1:]:
        if moneybox["savings_target"] is not None:
            if moneybox["id"] in result and result[moneybox["id"]]:
                assert result[moneybox["id"]][-1].month == expected[moneybox["id"]]