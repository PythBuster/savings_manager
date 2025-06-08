# pylint: disable=too-many-lines

"""The database test data initializer."""

from datetime import datetime, timedelta, timezone
from functools import partial
from typing import Any

from fastapi.encoders import jsonable_encoder
from sqlalchemy import insert

from src.custom_types import (
    ActionType,
    OverflowMoneyboxAutomatedSavingsModeType,
    TransactionTrigger,
    TransactionType,
)
from src.db.db_manager import DBManager
from src.db.models import AppSettings


class DBTestDataInitializer:  # pylint: disable=too-many-public-methods
    """The database test data initializer class."""

    def __init__(self, db_manager: DBManager, test_case: str) -> None:
        """Initialize the DBTestDataInitializer instance for ths specific
        test case.

        :param db_manager: The current database manager.
        :type db_manager: DBManager
        :param test_case: The current function name of test case.
        :type test_case: str
        """

        self.db_manager = db_manager
        """Current database connection and session maker hold in db_manager."""

        if "[" in test_case:
            test_case = test_case.split("[")[0]

        self.test_case = test_case
        """Current function name of test case."""

        self.TEST_CASES_DATA = {
            "test_overflow_moneybox_add_amount_success": partial(
                self.truncate_tables,
                exclude_table_names=["app_settings"],
            ),
            "test_get_overflow_moneybox": partial(
                self.truncate_tables,
                exclude_table_names=["app_settings"],
                create_overflow_moneybox=False,
            ),
            "test_endpoint_get_moneyboxes__status_200__total_6": self.dataset_test_endpoint_get_moneyboxes__status_200__total_6,
            "test_endpoint_get_moneyboxes__status_200__only_overflow_moneybox": self.truncate_tables,
            "test_endpoint_get_moneyboxes__fail__missing_overflow_moneybox": partial(
                self.truncate_tables,
                create_overflow_moneybox=False,
            ),
            "test_savings_forecast__status_200__with_savings_amount__overflow_balance_0__mode_collect": self.dataset_test_savings_forecast__status_200__with_savings_amount__overflow_balance_0__mode_collect,
            "test_savings_forecast__status_200__with_savings_amount__overflow_balance_0__mode_add": self.dataset_test_savings_forecast__status_200__with_savings_amount__overflow_balance_0__mode_add,
            "test_savings_forecast__status_200__with_savings_amount__overflow_balance_0__mode_fill": self.dataset_test_savings_forecast__status_200__with_savings_amount__overflow_balance_0__mode_fill,
            "test_savings_forecast__status_204__no_data": partial(
                self.truncate_tables,
                exclude_table_names=["app_settings"],
                create_overflow_moneybox=True,
            ),
            "test_savings_forecast__status_200__savings_amount_0__overflow_moneybox_0__mode_collect": self.dataset_test_savings_forecast__status_200__savings_amount_0__overflow_moneybox_0__mode_collect,
            "test_savings_forecast__status_200__savings_amount_0__overflow_moneybox_0__mode_add": self.dataset_test_savings_forecast__status_200__savings_amount_0__overflow_moneybox_0__mode_add,
            "test_savings_forecast__status_200__savings_amount_0__overflow_moneybox_0__mode_fill": self.dataset_test_savings_forecast__status_200__savings_amount_0__overflow_moneybox_0__mode_fill,
            "test_savings_forecast__status_200__savings_amount_0__overflow_moneybox_250__mode_collect": self.dataset_test_savings_forecast__status_200__savings_amount_0__overflow_moneybox_250__mode_collect,
            "test_savings_forecast__status_200__savings_amount_0__overflow_moneybox_250__mode_add": self.dataset_test_savings_forecast__status_200__savings_amount_0__overflow_moneybox_250__mode_add,
            "test_savings_forecast__status_200__savings_amount_0__overflow_moneybox_250__mode_fill": self.dataset_test_savings_forecast__status_200__savings_amount_0__overflow_moneybox_250__mode_fill,
            "test_savings_forecast__status_200__with_savings_amount__overflow_balance_3000__mode_collect": self.dataset_test_savings_forecast__status_200__with_savings_amount__overflow_balance_3000__mode_collect,
            "test_savings_forecast__status_200__with_savings_amount__overflow_balance_3000__mode_add": self.dataset_test_savings_forecast__status_200__with_savings_amount__overflow_balance_3000__mode_add,
            "test_savings_forecast__status_200__with_savings_amount__overflow_balance_3000__mode_fill": self.dataset_test_savings_forecast__status_200__with_savings_amount__overflow_balance_3000__mode_fill,
            "test_endpoint_get_moneybox__second_moneybox__status_200_existing": self.dataset_test_endpoint_get_moneybox__second_moneybox__status_200_existing,
            "test_endpoint_get_moneybox_status_404_non_existing": self.truncate_tables,
            "test_endpoint_get_moneybox__second_moneybox__status_200_existing__with_balance_100": self.dataset_test_endpoint_get_moneybox__second_moneybox__status_200_existing__with_balance_100,
            "test_endpoint_add_moneybox__invalid_with_priority_0": self.truncate_tables,
            "test_endpoint_add_moneybox__one__status_200": self.truncate_tables,
            "test_endpoint_add_moneybox__two__status_200": self.truncate_tables,
            "test_endpoint_add_moneybox__one__status_422__balance_postdata": self.truncate_tables,
            "test_endpoint_delete_overflow_moneybox__status_405": self.dataset_test_endpoint_delete_overflow_moneybox__status_405,
            "test_endpoint_update_overflow_moneybox__fail_409__modification_not_allowed": self.dataset_test_endpoint_update_overflow_moneybox__fail_409__modification_not_allowed,
            "test_endpoint_update_moneybox__status_422__invalid_priority_0": self.dataset_test_endpoint_update_moneybox__status_422__invalid_priority_0,
            "test_endpoint_update_moneybox__status_422__name_none": self.dataset_test_endpoint_update_moneybox__status_422__name_none,
            "test_endpoint_update_moneybox__status_422__name_empty": self.dataset_test_endpoint_update_moneybox__status_422__name_empty,
            "test_endpoint_update_moneybox__status_422__name_not_string_type": self.dataset_test_endpoint_update_moneybox__status_422__name_not_string_type,
            "test_endpoint_update_moneybox__last_moneybox__namechange": self.dataset_test_endpoint_update_moneybox__last_moneybox__namechange,
            "test_endpoint_update_moneybox__status_200__savings_amount_change": self.dataset_test_endpoint_update_moneybox__status_200__savings_amount_change,
            "test_endpoint_update_moneybox__status_422__savings_amount_none": self.dataset_test_endpoint_update_moneybox__status_422__savings_amount_none,
            "test_endpoint_update_moneybox__status_200__savings_target_none_change": self.dataset_test_endpoint_update_moneybox__status_200__savings_target_none_change,
            "test_endpoint_update_moneybox__status_200__savings_target_value_change": self.dataset_test_endpoint_update_moneybox__status_200__savings_target_value_change,
            "test_endpoint_update_moneybox__status_422_savings_target_non_int_type": self.dataset_test_endpoint_update_moneybox__status_422_savings_target_non_int_type,
            "test_endpoint_update_moneybox__status_422_savings_target_negative": self.dataset_test_endpoint_update_moneybox__status_422_savings_target_negative,
            "test_endpoint_update_moneybox__first_moneybox__status_422__fail_extra_fields": self.dataset_test_endpoint_update_moneybox__first_moneybox__status_422__fail_extra_fields,
            "test_endpoint_update_moneybox__status_200__description_change": self.dataset_test_endpoint_update_moneybox__status_200__description_change,
            "test_endpoint_update_moneybox__status_409__description_none": self.dataset_dataset_test_endpoint_update_moneybox__status_409__description_none,
            "test_endpoint_update_moneybox__status_422__description_not_string_type": self.dataset_test_endpoint_update_moneybox__status_422__description_not_string_type,
            "test_endpoint_update_moneybox__status_422__savings_amount_non_int_type": self.dataset_test_endpoint_update_moneybox__status_422__savings_amount_non_int_type,
            "test_endpoint_update_moneybox__status_422__savings_amount_negative": self.dataset_test_endpoint_update_moneybox__status_422__savings_amount_negative,
            "test_endpoint_first_moneybox__modified_at_checks": self.dataset_test_endpoint_first_moneybox__modified_at_checks,
            "test_endpoint_delete_second_moneybox__status_204": self.dataset_test_endpoint_delete_second_moneybox__status_204,
            "test_endpoint_deposit_first_moneybox__status_200": self.dataset_test_endpoint_deposit_first_moneybox__status_200,
            "test_endpoint_withdraw_first_moneybox__status_200": self.dataset_test_endpoint_withdraw_first_moneybox__status_200,
            "test_endpoint_withdraw_first_moneybox__status_409__balance_negative": self.dataset_test_endpoint_withdraw_first_moneybox__status_409__balance_negative,
            "test_endpoint_transfer_amount_moneybox_second_to_third__status_204": self.dataset_test_endpoint_transfer_amount_moneybox_second_to_third__status_204,
            "test_endpoint_transfer_amount_moneybox_second_to_third__status_204__missing_description_field": self.dataset_test_endpoint_transfer_amount_moneybox_second_to_third__status_204__missing_description_field,
            "test_endpoint_transfer_amount_moneybox_second_to_third__status_404__to_moneybox_third_not_found": self.dataset_test_endpoint_transfer_amount_moneybox_second_to_third__status_404__to_moneybox_third_not_found,
            "test_get_prioritylist": self.dataset_test_get_prioritylist,
            "test_get_empty_prioritylist": self.truncate_tables,
            "test_update_prioritylist": self.dataset_test_update_prioritylist,
            "test_create_instance": partial(
                self.truncate_tables, exclude_table_names=["app_settings"]
            ),
            "test_add_moneybox_success": partial(
                self.truncate_tables, exclude_table_names=["app_settings"]
            ),
            "test_get_app_settings_status_200": partial(
                self.truncate_tables, exclude_table_names=["app_settings"]
            ),
            "test_get_app_settings_invalid": self.truncate_tables,
            "test_automated_savings_overflow_moneybox_mode_collect": self.dataset_test_automated_savings_valid,
            "test_automated_savings_overflow_moneybox_mode_add_to_amount": self.dataset_test_automated_savings_overflow_moneybox_mode_add_to_amount,
            "test_automated_savings_overflow_moneybox_mode_fill_up": self.dataset_test_automated_savings_overflow_moneybox_mode_fill_up,
            "test_automated_savings_overflow_moneybox_mode_ratio": self.dataset_test_automated_savings_overflow_moneybox_mode_ratio,
            "test_automated_savings_overflow_moneybox_mode_ratio__only_overflow_moneybox": self.dataset_test_automated_savings_overflow_moneybox_mode_ratio__only_overflow_moneybox,
            "test_automated_savings_overflow_moneybox_mode_collect__only_overflow_moneybox": self.dataset_test_automated_savings_overflow_moneybox_mode_collect__only_overflow_moneybox,
            "test_automated_savings_overflow_moneybox_mode_add__only_overflow_moneybox": self.dataset_test_automated_savings_overflow_moneybox_mode_add__only_overflow_moneybox,
            "test_automated_savings_overflow_moneybox_mode_fill__only_overflow_moneybox": self.dataset_test_automated_savings_overflow_moneybox_mode_fill__only_overflow_moneybox,
            "test_task_automated_savings_schedule": self.dataset_test_task_automated_savings_schedule,
            "test_task_automated_savings_dont_schedule": self.dataset_test_task_automated_savings_dont_schedule,
            "test_task_automated_savings_no_email_send": self.dataset_test_task_automated_savings_no_email_send,
            "test_task_automated_savings_no_savings_active": self.dataset_test_task_automated_savings_no_savings_active,
            "test_send_testemail_success": self.dataset_test_send_testemail_success,
            "test_task_email_sending__one_of_one": self.dataset_test_task_email_sending__one_of_one,
            "test_task_email_sending__two_of_two": self.dataset_test_task_email_sending__two_of_two,
            "test_task_email_sending__two_of_three": self.dataset_test_task_email_sending__two_of_three,
            "test_reset_database_keep_app_settings": self.dataset_test_reset_database_keep_app_settings,
            "test_reset_database_delete_app_settings": self.dataset_test_reset_database_delete_app_settings,
            "test_reset_app_keep_app_settings": self.dataset_test_reset_app_keep_app_settings,
            "test_reset_app_delete_app_settings": self.dataset_test_reset_app_delete_app_settings,
            "test_export_sql_dump": self.dataset_test_export_sql_dump,
            "test_import_sql_dump": self.dataset_test_import_sql_dump,
            "test_get_users_empty": self.truncate_tables,
            "test_distribute_automated_savings_amount__amount_0": self.dataset_test_distribute_automated_savings_amount__amount_0,
            "test_distribute_automated_savings_amount__normal_mode__one_moneybox_with_savings_amount_0": (
                self.dataset_test_distribute_automated_savings_amount__normal_mode__one_moneybox_with_savings_amount_0
            ),
            "test_distribute_automated_savings_amount__fill_mode__one_moneybox_with_savings_target_none": (
                self.dataset_test_distribute_automated_savings_amount__fill_mode__one_moneybox_with_savings_target_none
            ),
        }
        """Map test case name witch related test data generation function"""

    async def run(
        self,
    ) -> None:
        """Call data generator function depending on test case name map."""

        await self.TEST_CASES_DATA[self.test_case]()  # type: ignore

    async def truncate_tables(
        self,
        exclude_table_names: list[str] | None = None,
        create_overflow_moneybox: bool = True,
    ) -> None:
        """Truncate tables."""

        print(
            f"Truncate tables ({self.test_case})",
            flush=True,
        )
        await self.db_manager.truncate_tables(exclude_table_names=exclude_table_names)  # type: ignore

        if create_overflow_moneybox:
            # re-add overflow moneybox after emptying database
            overflow_moneybox_data = {
                "name": "Overflow Moneybox",
                "savings_amount": 0,
                "savings_target": None,
                "priority": 0,
            }

            await self.db_manager._add_overflow_moneybox(  # noqa: ignore  # pylint: disable=line-too-long, protected-access
                moneybox_data=overflow_moneybox_data,
            )

    async def dataset_test_endpoint_get_moneyboxes__status_200__total_6(self) -> None:
        """The data generation function for test_case:
        `test_endpoint_get_moneyboxes__status_200__total_6`.
        """

        await self.truncate_tables()

        print(
            f"Create data for test ({self.test_case})",
            flush=True,
        )

        moneyboxes_data = [
            {
                "name": "Test Box 1",
                "savings_amount": 0,
                "savings_target": None,
                "priority": 1,
            },
            {
                "name": "Test Box 2",
                "savings_amount": 0,
                "savings_target": None,
                "priority": 2,
            },
            {
                "name": "Test Box 3",
                "savings_amount": 0,
                "savings_target": None,
                "priority": 3,
            },
            {
                "name": "Test Box 4",
                "savings_amount": 0,
                "savings_target": None,
                "priority": 4,
            },
            {
                "name": "Test Box 5",
                "savings_amount": 0,
                "savings_target": None,
                "priority": 5,
            },
        ]

        for moneybox_data in moneyboxes_data:
            await self.db_manager.add_moneybox(
                moneybox_data=moneybox_data,
            )

    async def dataset_test_savings_forecast__status_200__with_savings_amount__overflow_balance_0__mode_collect(
        self,
    ) -> None:
        """The data generation function for test_case:
        `test_savings_forecast__status_200__with_savings_amount__overflow_balance_0__mode_collect`.
        """

        await self.truncate_tables()

        # create app settings
        app_settings_data = {
            "send_reports_via_email": False,
            "user_email_address": None,
            "is_automated_saving_active": True,
            "savings_amount": 2000,
            "overflow_moneybox_automated_savings_mode": OverflowMoneyboxAutomatedSavingsModeType.COLLECT,
            "is_active": True,
            "note": "",
        }

        async with self.db_manager.async_sessionmaker.begin() as session:
            stmt = insert(AppSettings).values(**app_settings_data)
            await session.execute(stmt)

        print(
            f"Create data for test ({self.test_case})",
            flush=True,
        )

        moneyboxes_data = [
            # id: 25
            {  # expectation: reached savings target in 5 months
                "name": "Test Box 3",
                "priority": 1,
                "balance": 0,
                "savings_amount": 2500,
                "savings_target": 10000,
            },
            # id: 26
            {  # takes 1000 from month 6 upwards, reaching: -1 (never)
                "name": "Test Box 2",
                "priority": 2,
                "balance": 0,
                "savings_amount": 1000,
                "savings_target": None,
            },
            # id: 27
            {  # get 1000 from month 6 upwards, expectation: reached target in 15 months
                "name": "Test Box 4",
                "priority": 3,
                "balance": 1000,
                "savings_amount": 5000,
                "savings_target": 10500,
            },
            # id: 28
            {  # expectation: reached target directly (month 0)
                "name": "Test Box 5",
                "priority": 4,
                "balance": 0,
                "savings_amount": 0,
                "savings_target": 0,
            },
            # id: 29
            {  # get last 500 in month 15, then nothing because loop is finished. reaching: -1 (never)
                "name": "Test Box 6",
                "priority": 5,
                "balance": 0,
                "savings_amount": 600,
                "savings_target": None,
            },
        ]

        for moneybox_data in moneyboxes_data:
            await self.db_manager.add_moneybox(
                moneybox_data=moneybox_data,
            )

    async def dataset_test_savings_forecast__status_200__with_savings_amount__overflow_balance_0__mode_add(
        self,
    ) -> None:
        """The data generation function for test_case:
        `test_savings_forecast__status_200__with_savings_amount__overflow_balance_0__mode_add`.
        """

        await self.truncate_tables()

        # create app settings
        app_settings_data = {
            "send_reports_via_email": False,
            "user_email_address": None,
            "is_automated_saving_active": True,
            "savings_amount": 2000,
            "overflow_moneybox_automated_savings_mode": OverflowMoneyboxAutomatedSavingsModeType.ADD_TO_AUTOMATED_SAVINGS_AMOUNT,
            "is_active": True,
            "note": "",
        }

        async with self.db_manager.async_sessionmaker.begin() as session:
            stmt = insert(AppSettings).values(**app_settings_data)
            await session.execute(stmt)

        print(
            f"Create data for test ({self.test_case})",
            flush=True,
        )

        moneyboxes_data = [
            # id: 31
            {  # expectation: reached savings target in 5 months
                "name": "Test Box 3",
                "priority": 1,
                "balance": 0,
                "savings_amount": 2500,
                "savings_target": 10000,
            },
            # id: 32
            {  # takes 1000 from month 6 upwards, reaching: -1 (never)
                "name": "Test Box 2",
                "priority": 2,
                "balance": 0,
                "savings_amount": 1000,
                "savings_target": None,
            },
            # id: 33
            {  # get 1000 from month 6 upwards, expectation: reached target in 15 months
                "name": "Test Box 4",
                "priority": 3,
                "balance": 1000,
                "savings_amount": 5000,
                "savings_target": 10500,
            },
            # id: 34
            {  # expectation: reached target directly (month 0)
                "name": "Test Box 5",
                "priority": 4,
                "balance": 0,
                "savings_amount": 0,
                "savings_target": 0,
            },
            # id: 35
            {  # get last 500 in month 15, then nothing because loop is finished. reaching: -1 (never)
                "name": "Test Box 6",
                "priority": 5,
                "balance": 0,
                "savings_amount": 600,
                "savings_target": None,
            },
        ]

        for moneybox_data in moneyboxes_data:
            await self.db_manager.add_moneybox(
                moneybox_data=moneybox_data,
            )

    async def dataset_test_savings_forecast__status_200__with_savings_amount__overflow_balance_0__mode_fill(
        self,
    ) -> None:
        """The data generation function for test_case:
        `test_savings_forecast__status_200__with_savings_amount__overflow_balance_0__mode_fill`.
        """

        await self.truncate_tables()

        # create app settings
        app_settings_data = {
            "send_reports_via_email": False,
            "user_email_address": None,
            "is_automated_saving_active": True,
            "savings_amount": 2000,
            "overflow_moneybox_automated_savings_mode": OverflowMoneyboxAutomatedSavingsModeType.ADD_TO_AUTOMATED_SAVINGS_AMOUNT,
            "is_active": True,
            "note": "",
        }

        async with self.db_manager.async_sessionmaker.begin() as session:
            stmt = insert(AppSettings).values(**app_settings_data)
            await session.execute(stmt)

        print(
            f"Create data for test ({self.test_case})",
            flush=True,
        )

        moneyboxes_data = [
            # id: 37
            {  # expectation: reached savings target in 5 months
                "name": "Test Box 3",
                "priority": 1,
                "balance": 0,
                "savings_amount": 2500,
                "savings_target": 10000,
            },
            # id: 38
            {  # takes 1000 from month 6 upwards, reaching: -1 (never)
                "name": "Test Box 2",
                "priority": 2,
                "balance": 0,
                "savings_amount": 1000,
                "savings_target": None,
            },
            # id: 39
            {  # get 1000 from month 6 upwards, expectation: reached target in 15 months
                "name": "Test Box 4",
                "priority": 3,
                "balance": 1000,
                "savings_amount": 5000,
                "savings_target": 10500,
            },
            # id: 40
            {  # expectation: reached target directly (month 0)
                "name": "Test Box 5",
                "priority": 4,
                "balance": 0,
                "savings_amount": 0,
                "savings_target": 0,
            },
            # id: 41
            {  # get last 500 in month 15, then nothing because loop is finished. reaching: -1 (never)
                "name": "Test Box 6",
                "priority": 5,
                "balance": 0,
                "savings_amount": 600,
                "savings_target": None,
            },
        ]

        for moneybox_data in moneyboxes_data:
            await self.db_manager.add_moneybox(
                moneybox_data=moneybox_data,
            )

    async def dataset_test_savings_forecast__status_200__savings_amount_0__overflow_moneybox_0__mode_collect(
        self,
    ) -> None:
        """The data generation function for test_case:
        `test_savings_forecast__status_200__savings_amount_0__overflow_moneybox_0__mode_collect`.
        """

        await self.truncate_tables()

        # create app settings
        app_settings_data = {
            "send_reports_via_email": False,
            "user_email_address": None,
            "is_automated_saving_active": True,
            "savings_amount": 0,
            "overflow_moneybox_automated_savings_mode": OverflowMoneyboxAutomatedSavingsModeType.COLLECT,
            "is_active": True,
            "note": "",
        }

        async with self.db_manager.async_sessionmaker.begin() as session:
            stmt = insert(AppSettings).values(**app_settings_data)
            await session.execute(stmt)

        print(
            f"Create data for test ({self.test_case})",
            flush=True,
        )

        moneyboxes_data = [
            # id: 44
            {  # reaching: -1 (never)
                "name": "Test Box 3",
                "priority": 1,
                "balance": 0,
                "savings_amount": 2500,
                "savings_target": 10000,
            },
            # id: 45
            {  # reaching: -1 (never)
                "name": "Test Box 2",
                "priority": 2,
                "balance": 0,
                "savings_amount": 1000,
                "savings_target": None,
            },
            # id: 46
            {  # reaching: -1 (never)
                "name": "Test Box 4",
                "priority": 3,
                "balance": 1000,
                "savings_amount": 5000,
                "savings_target": 10500,
            },
            # id: 47
            {  # reached target directly (month 0)
                "name": "Test Box 5",
                "priority": 4,
                "balance": 0,
                "savings_amount": 0,
                "savings_target": 0,
            },
        ]

        for moneybox_data in moneyboxes_data:
            await self.db_manager.add_moneybox(
                moneybox_data=moneybox_data,
            )

    async def dataset_test_savings_forecast__status_200__savings_amount_0__overflow_moneybox_0__mode_add(
        self,
    ) -> None:
        """The data generation function for test_case:
        `test_savings_forecast__status_200__savings_amount_0__overflow_moneybox_0__mode_add`.
        """

        await self.truncate_tables()

        # create app settings
        app_settings_data = {
            "send_reports_via_email": False,
            "user_email_address": None,
            "is_automated_saving_active": True,
            "savings_amount": 0,
            "overflow_moneybox_automated_savings_mode": OverflowMoneyboxAutomatedSavingsModeType.ADD_TO_AUTOMATED_SAVINGS_AMOUNT,
            "is_active": True,
            "note": "",
        }

        async with self.db_manager.async_sessionmaker.begin() as session:
            stmt = insert(AppSettings).values(**app_settings_data)
            await session.execute(stmt)

        print(
            f"Create data for test ({self.test_case})",
            flush=True,
        )

        moneyboxes_data = [
            # id: 49
            {  # reaching: -1 (never)
                "name": "Test Box 3",
                "priority": 1,
                "balance": 0,
                "savings_amount": 2500,
                "savings_target": 10000,
            },
            # id: 50
            {  # reaching: -1 (never)
                "name": "Test Box 2",
                "priority": 2,
                "balance": 0,
                "savings_amount": 1000,
                "savings_target": None,
            },
            # id: 51
            {  # reaching: -1 (never)
                "name": "Test Box 4",
                "priority": 3,
                "balance": 1000,
                "savings_amount": 5000,
                "savings_target": 10500,
            },
            # id: 52
            {  # reached target directly (month 0)
                "name": "Test Box 5",
                "priority": 4,
                "balance": 0,
                "savings_amount": 0,
                "savings_target": 0,
            },
        ]

        for moneybox_data in moneyboxes_data:
            await self.db_manager.add_moneybox(
                moneybox_data=moneybox_data,
            )

    async def dataset_test_savings_forecast__status_200__savings_amount_0__overflow_moneybox_0__mode_fill(
        self,
    ) -> None:
        """The data generation function for test_case:
        `test_savings_forecast__status_200__savings_amount_0__overflow_moneybox_0__mode_fill`.
        """

        await self.truncate_tables()

        # create app settings
        app_settings_data = {
            "send_reports_via_email": False,
            "user_email_address": None,
            "is_automated_saving_active": True,
            "savings_amount": 0,
            "overflow_moneybox_automated_savings_mode": OverflowMoneyboxAutomatedSavingsModeType.FILL_UP_LIMITED_MONEYBOXES,
            "is_active": True,
            "note": "",
        }

        async with self.db_manager.async_sessionmaker.begin() as session:
            stmt = insert(AppSettings).values(**app_settings_data)
            await session.execute(stmt)

        print(
            f"Create data for test ({self.test_case})",
            flush=True,
        )

        moneyboxes_data = [
            # id: 54
            {  # reaching: -1 (never)
                "name": "Test Box 3",
                "priority": 1,
                "balance": 0,
                "savings_amount": 2500,
                "savings_target": 10000,
            },
            # id: 55
            {  # reaching: -1 (never)
                "name": "Test Box 2",
                "priority": 2,
                "balance": 0,
                "savings_amount": 1000,
                "savings_target": None,
            },
            # id: 56
            {  # reaching: -1 (never)
                "name": "Test Box 4",
                "priority": 3,
                "balance": 1000,
                "savings_amount": 5000,
                "savings_target": 10500,
            },
            # id: 57
            {  # reached target directly (month 0)
                "name": "Test Box 5",
                "priority": 4,
                "balance": 0,
                "savings_amount": 0,
                "savings_target": 0,
            },
        ]

        for moneybox_data in moneyboxes_data:
            await self.db_manager.add_moneybox(
                moneybox_data=moneybox_data,
            )

    async def dataset_test_savings_forecast__status_200__savings_amount_0__overflow_moneybox_250__mode_collect(
        self,
    ) -> None:
        """The data generation function for test_case:
        `test_savings_forecast__status_200__savings_amount_0__overflow_moneybox_250__mode_collect`.
        """

        await self.truncate_tables()

        # create app settings
        app_settings_data = {
            "send_reports_via_email": False,
            "user_email_address": None,
            "is_automated_saving_active": True,
            "savings_amount": 0,
            "overflow_moneybox_automated_savings_mode": OverflowMoneyboxAutomatedSavingsModeType.COLLECT,
            "is_active": True,
            "note": "",
        }

        async with self.db_manager.async_sessionmaker.begin() as session:
            stmt = insert(AppSettings).values(**app_settings_data)
            await session.execute(stmt)

        overflow_moneybox = (
            await self.db_manager._get_overflow_moneybox()  # pylint: disable=protected-access
        )
        await self.db_manager.add_amount(
            moneybox_id=overflow_moneybox.id,
            deposit_transaction_data={
                "amount": 250,
                "description": "Test Case",
            },
            transaction_type=TransactionType.DIRECT,
            transaction_trigger=TransactionTrigger.MANUALLY,
        )

        print(
            f"Create data for test ({self.test_case})",
            flush=True,
        )

        moneyboxes_data = [
            # id: 59
            {  # reaching: -1 (never)
                "name": "Test Box 3",
                "priority": 1,
                "balance": 0,
                "savings_amount": 2500,
                "savings_target": 10000,
            },
            # id: 60
            {  # reaching: -1 (never)
                "name": "Test Box 2",
                "priority": 2,
                "balance": 0,
                "savings_amount": 1000,
                "savings_target": None,
            },
            # id: 61
            {  # reaching: -1 (never)
                "name": "Test Box 4",
                "priority": 3,
                "balance": 1000,
                "savings_amount": 5000,
                "savings_target": 10500,
            },
            # id: 62
            {  # reached target directly (month 0)
                "name": "Test Box 5",
                "priority": 4,
                "balance": 0,
                "savings_amount": 0,
                "savings_target": 0,
            },
        ]

        for moneybox_data in moneyboxes_data:
            await self.db_manager.add_moneybox(
                moneybox_data=moneybox_data,
            )

    async def dataset_test_savings_forecast__status_200__savings_amount_0__overflow_moneybox_250__mode_add(
        self,
    ) -> None:
        """The data generation function for test_case:
        `test_savings_forecast__status_200__savings_amount_0__overflow_moneybox_250__mode_add`.
        """

        await self.truncate_tables()

        # create app settings
        app_settings_data = {
            "send_reports_via_email": False,
            "user_email_address": None,
            "is_automated_saving_active": True,
            "savings_amount": 0,
            "overflow_moneybox_automated_savings_mode": OverflowMoneyboxAutomatedSavingsModeType.ADD_TO_AUTOMATED_SAVINGS_AMOUNT,
            "is_active": True,
            "note": "",
        }

        async with self.db_manager.async_sessionmaker.begin() as session:
            stmt = insert(AppSettings).values(**app_settings_data)
            await session.execute(stmt)

        overflow_moneybox = (
            await self.db_manager._get_overflow_moneybox()  # pylint: disable=protected-access
        )
        await self.db_manager.add_amount(
            moneybox_id=overflow_moneybox.id,
            deposit_transaction_data={
                "amount": 250,
                "description": "Test Case",
            },
            transaction_type=TransactionType.DIRECT,
            transaction_trigger=TransactionTrigger.MANUALLY,
        )

        print(
            f"Create data for test ({self.test_case})",
            flush=True,
        )

        moneyboxes_data = [
            # id: 64
            {  # reaching: 1 month
                "name": "Test Box 3",
                "priority": 1,
                "balance": 0,
                "savings_amount": 200,
                "savings_target": 200,
            },
            # id: 65
            {  # reaching: -1 (never)
                "name": "Test Box 2",
                "priority": 2,
                "balance": 0,
                "savings_amount": 10,
                "savings_target": None,
            },
            # id: 66
            {  # reaching: 1 month
                "name": "Test Box 4",
                "priority": 3,
                "balance": 0,
                "savings_amount": 40,
                "savings_target": 40,
            },
            # id: 67
            {  # reached target directly (month 0)
                "name": "Test Box 5",
                "priority": 4,
                "balance": 0,
                "savings_amount": 0,
                "savings_target": 0,
            },
            # id: 68
            {  # reaching: -1 (never)
                "name": "Test Box 6",
                "priority": 5,
                "balance": 1,
                "savings_amount": 1,
                "savings_target": 2,
            },
        ]

        for moneybox_data in moneyboxes_data:
            await self.db_manager.add_moneybox(
                moneybox_data=moneybox_data,
            )

    async def dataset_test_savings_forecast__status_200__savings_amount_0__overflow_moneybox_250__mode_fill(
        self,
    ) -> None:
        """The data generation function for test_case:
        `test_savings_forecast__status_200__savings_amount_0__overflow_moneybox_250__mode_fill`.
        """

        await self.truncate_tables()

        # create app settings
        app_settings_data = {
            "send_reports_via_email": False,
            "user_email_address": None,
            "is_automated_saving_active": True,
            "savings_amount": 0,
            "overflow_moneybox_automated_savings_mode": OverflowMoneyboxAutomatedSavingsModeType.FILL_UP_LIMITED_MONEYBOXES,
            "is_active": True,
            "note": "",
        }

        async with self.db_manager.async_sessionmaker.begin() as session:
            stmt = insert(AppSettings).values(**app_settings_data)
            await session.execute(stmt)

        overflow_moneybox = (
            await self.db_manager._get_overflow_moneybox()  # pylint: disable=protected-access
        )
        await self.db_manager.add_amount(
            moneybox_id=overflow_moneybox.id,
            deposit_transaction_data={
                "amount": 250,
                "description": "Test Case",
            },
            transaction_type=TransactionType.DIRECT,
            transaction_trigger=TransactionTrigger.MANUALLY,
        )

        print(
            f"Create data for test ({self.test_case})",
            flush=True,
        )

        moneyboxes_data = [
            # id: 70
            {  # reaching: 1 month
                "name": "Test Box 3",
                "priority": 1,
                "balance": 0,
                "savings_amount": 50,
                "savings_target": 210,
            },
            # id: 71
            {  # reaching: -1 (never)
                "name": "Test Box 2",
                "priority": 2,
                "balance": 0,
                "savings_amount": 10,
                "savings_target": None,
            },
            # id: 72
            {  # reaching: 1 month
                "name": "Test Box 4",
                "priority": 3,
                "balance": 0,
                "savings_amount": 40,
                "savings_target": 40,
            },
            # id: 73
            {  # reached target directly (month 0)
                "name": "Test Box 5",
                "priority": 4,
                "balance": 0,
                "savings_amount": 0,
                "savings_target": 0,
            },
            # id: 74
            {  # reaching: -1 (never)
                "name": "Test Box 6",
                "priority": 5,
                "balance": 1,
                "savings_amount": 1,
                "savings_target": 2,
            },
        ]

        for moneybox_data in moneyboxes_data:
            await self.db_manager.add_moneybox(
                moneybox_data=moneybox_data,
            )

    async def dataset_test_savings_forecast__status_200__with_savings_amount__overflow_balance_3000__mode_collect(
        self,
    ) -> None:
        """The data generation function for test_case:
        `test_savings_forecast__status_200__with_savings_amount__overflow_balance_3000__mode_collect`.
        """

        await self.truncate_tables()

        # create app settings
        app_settings_data = {
            "send_reports_via_email": False,
            "user_email_address": None,
            "is_automated_saving_active": True,
            "savings_amount": 2000,
            "overflow_moneybox_automated_savings_mode": OverflowMoneyboxAutomatedSavingsModeType.COLLECT,
            "is_active": True,
            "note": "",
        }

        async with self.db_manager.async_sessionmaker.begin() as session:
            stmt = insert(AppSettings).values(**app_settings_data)
            await session.execute(stmt)

        overflow_moneybox = (
            await self.db_manager._get_overflow_moneybox()  # pylint: disable=protected-access
        )
        await self.db_manager.add_amount(
            moneybox_id=overflow_moneybox.id,
            deposit_transaction_data={
                "amount": 3000,
                "description": "Test Case",
            },
            transaction_type=TransactionType.DIRECT,
            transaction_trigger=TransactionTrigger.MANUALLY,
        )

        print(
            f"Create data for test ({self.test_case})",
            flush=True,
        )

        moneyboxes_data = [
            # id: 76
            {  # expectation: reached savings target in 5 months
                "name": "Test Box 3",
                "priority": 1,
                "balance": 0,
                "savings_amount": 2500,
                "savings_target": 10000,
            },
            # id: 77
            {  # takes 1000 from month 6 upwards, reaching: -1 (never)
                "name": "Test Box 2",
                "priority": 2,
                "balance": 0,
                "savings_amount": 1000,
                "savings_target": None,
            },
            # id: 78
            {  # get 1000 from month 6 upwards, expectation: reached target in 15 months
                "name": "Test Box 4",
                "priority": 3,
                "balance": 1000,
                "savings_amount": 5000,
                "savings_target": 10500,
            },
            # id: 79
            {  # expectation: reached target directly (month 0)
                "name": "Test Box 5",
                "priority": 4,
                "balance": 0,
                "savings_amount": 0,
                "savings_target": 0,
            },
            # id: 80
            {  # reaching: -1 (never)
                "name": "Test Box 6",
                "priority": 5,
                "balance": 0,
                "savings_amount": 0,
                "savings_target": 1000,
            },
        ]

        for moneybox_data in moneyboxes_data:
            await self.db_manager.add_moneybox(
                moneybox_data=moneybox_data,
            )

    async def dataset_test_savings_forecast__status_200__with_savings_amount__overflow_balance_3000__mode_add(
        self,
    ) -> None:
        """The data generation function for test_case:
        `test_savings_forecast__status_200__with_savings_amount__overflow_balance_3000__mode_add`.
        """

        await self.truncate_tables()

        # create app settings
        app_settings_data = {
            "send_reports_via_email": False,
            "user_email_address": None,
            "is_automated_saving_active": True,
            "savings_amount": 2000,
            "overflow_moneybox_automated_savings_mode": OverflowMoneyboxAutomatedSavingsModeType.ADD_TO_AUTOMATED_SAVINGS_AMOUNT,
            "is_active": True,
            "note": "",
        }

        async with self.db_manager.async_sessionmaker.begin() as session:
            stmt = insert(AppSettings).values(**app_settings_data)
            await session.execute(stmt)

        overflow_moneybox = (
            await self.db_manager._get_overflow_moneybox()  # pylint: disable=protected-access
        )
        await self.db_manager.add_amount(
            moneybox_id=overflow_moneybox.id,
            deposit_transaction_data={
                "amount": 3000,
                "description": "Test Case",
            },
            transaction_type=TransactionType.DIRECT,
            transaction_trigger=TransactionTrigger.MANUALLY,
        )

        print(
            f"Create data for test ({self.test_case})",
            flush=True,
        )

        moneyboxes_data = [
            # id: 82
            {  # reached savings target in 4 months
                "name": "Test Box 3",
                "priority": 1,
                "balance": 0,
                "savings_amount": 2500,
                "savings_target": 8500,
            },
            # id: 83
            {  # takes 100 in month 1, then from month 5 upwards, reaching: -1 (never)
                "name": "Test Box 2",
                "priority": 2,
                "balance": 0,
                "savings_amount": 1000,
                "savings_target": None,
            },
            # id: 84
            {  # takes 1500 in month 1 (rest from overflow moneybox added amount), then gets 1000 from month 5 upwards
                # reached target in 12 months
                "name": "Test Box 4",
                "priority": 3,
                "balance": 0,
                "savings_amount": 5000,
                "savings_target": 9500,
            },
            # id: 85
            {  # expectation: reached target directly (month 0)
                "name": "Test Box 5",
                "priority": 4,
                "balance": 0,
                "savings_amount": 0,
                "savings_target": 0,
            },
            # id: 86
            {  # reaching: -1 (never)
                "name": "Test Box 6",
                "priority": 5,
                "balance": 0,
                "savings_amount": 0,
                "savings_target": 1000,
            },
        ]

        for moneybox_data in moneyboxes_data:
            await self.db_manager.add_moneybox(
                moneybox_data=moneybox_data,
            )

    async def dataset_test_savings_forecast__status_200__with_savings_amount__overflow_balance_3000__mode_fill(
        self,
    ) -> None:
        """The data generation function for test_case:
        `test_savings_forecast__status_200__with_savings_amount__overflow_balance_3000__mode_fill`.
        """

        await self.truncate_tables()

        # create app settings
        app_settings_data = {
            "send_reports_via_email": False,
            "user_email_address": None,
            "is_automated_saving_active": True,
            "savings_amount": 2000,
            "overflow_moneybox_automated_savings_mode": OverflowMoneyboxAutomatedSavingsModeType.FILL_UP_LIMITED_MONEYBOXES,
            "is_active": True,
            "note": "",
        }

        async with self.db_manager.async_sessionmaker.begin() as session:
            stmt = insert(AppSettings).values(**app_settings_data)
            await session.execute(stmt)

        overflow_moneybox = (
            await self.db_manager._get_overflow_moneybox()  # pylint: disable=protected-access
        )
        await self.db_manager.add_amount(
            moneybox_id=overflow_moneybox.id,
            deposit_transaction_data={
                "amount": 3000,
                "description": "Test Case",
            },
            transaction_type=TransactionType.DIRECT,
            transaction_trigger=TransactionTrigger.MANUALLY,
        )

        print(
            f"Create data for test ({self.test_case})",
            flush=True,
        )

        moneyboxes_data = [
            # id: 88
            {  # expectation: reached savings target in 4 months
                "name": "Test Box 3",
                "priority": 1,
                "balance": 0,
                "savings_amount": 2500,
                "savings_target": 10000,
            },
            # id: 89
            {  # takes 1000 from month 4 upwards, reaching: -1 (never)
                "name": "Test Box 2",
                "priority": 2,
                "balance": 0,
                "savings_amount": 1000,
                "savings_target": None,
            },
            # id: 90
            {  # get 1000 from month 5 upwards, expectation: reached target in 10 months
                "name": "Test Box 4",
                "priority": 3,
                "balance": 0,
                "savings_amount": 5000,
                "savings_target": 6000,
            },
            # id: 91
            {  # expectation: reached target directly (month 0)
                "name": "Test Box 5",
                "priority": 4,
                "balance": 0,
                "savings_amount": 0,
                "savings_target": 0,
            },
            # id: 92
            {  # reaching: -1 (never)
                "name": "Test Box 6",
                "priority": 5,
                "balance": 0,
                "savings_amount": 0,
                "savings_target": 1000,
            },
        ]

        for moneybox_data in moneyboxes_data:
            await self.db_manager.add_moneybox(
                moneybox_data=moneybox_data,
            )

    async def dataset_test_endpoint_get_moneybox__second_moneybox__status_200_existing(
        self,
    ) -> None:
        """The data generation function for test_case:
        `test_endpoint_get_moneybox__second_moneybox__status_200_existing`.
        """

        await self.truncate_tables()

        print(
            f"Create data for test ({self.test_case})",
            flush=True,
        )

        # create moneybox with id 1
        moneyboxes_data = [
            {
                "name": "Test Box 1",
                "savings_amount": 0,
                "savings_target": None,
                "priority": 1,
            },
        ]

        for moneybox_data in moneyboxes_data:
            await self.db_manager.add_moneybox(
                moneybox_data=moneybox_data,
            )

    async def dataset_test_endpoint_get_moneybox__second_moneybox__status_200_existing__with_balance_100(
        self,
    ) -> None:
        """The data generation function for test_case:
        `test_endpoint_get_moneybox__second_moneybox__status_200_existing__with_balance_100`.
        """

        await self.truncate_tables()

        print(
            f"Create data for test ({self.test_case})",
            flush=True,
        )

        # create 2 moneyboxes
        moneyboxes_data = [
            {
                "name": "Test Box 1",
                "savings_amount": 0,
                "savings_target": None,
                "priority": 1,
            },
            {
                "name": "Test Box 2",
                "savings_amount": 0,
                "savings_target": None,
                "priority": 2,
            },
        ]

        added_moneyboxes = []
        for moneybox_data in moneyboxes_data:
            moneybox = await self.db_manager.add_moneybox(
                moneybox_data=moneybox_data,
            )
            added_moneyboxes.append(moneybox)

        # sleep to get higher modified_at datetime (simulate time passing before modifying data)
        # time.sleep(1)

        # add some amount to second moneybox
        await self.db_manager.add_amount(
            moneybox_id=added_moneyboxes[1]["id"],
            deposit_transaction_data={
                "amount": 100,
                "description": "Unit Test.",
            },
            transaction_type=TransactionType.DIRECT,
            transaction_trigger=TransactionTrigger.MANUALLY,
        )

    async def dataset_test_endpoint_update_moneybox__status_422__invalid_priority_0(self) -> None:
        """The data generation function for test_case:
        `test_endpoint_update_moneybox__status_422__invalid_priority_0`.
        """

        await self.truncate_tables()

        print(
            f"Create data for test ({self.test_case})",
            flush=True,
        )

        # create 1 moneybox
        moneyboxes_data = [
            {
                "name": "Test Box 1",
                "savings_amount": 0,
                "savings_target": None,
                "priority": 1,
            },
        ]

        for moneybox_data in moneyboxes_data:
            await self.db_manager.add_moneybox(
                moneybox_data=moneybox_data,
            )

    async def dataset_test_endpoint_update_moneybox__status_422__name_none(self) -> None:
        """The data generation function for test_case:
        `test_endpoint_update_moneybox__status_422__description_none`.
        """

        await self.truncate_tables()

        print(
            f"Create data for test ({self.test_case})",
            flush=True,
        )

        # create 1 moneybox
        moneyboxes_data = [
            {
                "name": "Test Box 1",
                "savings_amount": 0,
                "savings_target": None,
                "priority": 1,
            },
        ]

        for moneybox_data in moneyboxes_data:
            await self.db_manager.add_moneybox(
                moneybox_data=moneybox_data,
            )

    async def dataset_test_endpoint_update_moneybox__status_422__name_empty(self) -> None:
        """The data generation function for test_case:
        `test_endpoint_update_moneybox__status_422__name_empty`.
        """

        await self.truncate_tables()

        print(
            f"Create data for test ({self.test_case})",
            flush=True,
        )

        # create 1 moneybox
        moneyboxes_data = [
            {
                "name": "Test Box 1",
                "savings_amount": 0,
                "savings_target": None,
                "priority": 1,
            },
        ]

        for moneybox_data in moneyboxes_data:
            await self.db_manager.add_moneybox(
                moneybox_data=moneybox_data,
            )

    async def dataset_test_endpoint_update_moneybox__status_422__name_not_string_type(self) -> None:
        """The data generation function for test_case:
        `test_endpoint_update_moneybox__status_422__name_not_string_type`.
        """

        await self.truncate_tables()

        print(
            f"Create data for test ({self.test_case})",
            flush=True,
        )

        # create 1 moneybox
        moneyboxes_data = [
            {
                "name": "Test Box 1",
                "savings_amount": 0,
                "savings_target": None,
                "priority": 1,
            },
        ]

        for moneybox_data in moneyboxes_data:
            await self.db_manager.add_moneybox(
                moneybox_data=moneybox_data,
            )

    async def dataset_test_endpoint_update_moneybox__last_moneybox__namechange(
        self,
    ) -> None:
        """The data generation function for test_case:
        `test_endpoint_update_moneybox__last_moneybox__namechange`.
        """

        await self.truncate_tables()

        print(
            f"Create data for test ({self.test_case})",
            flush=True,
        )

        # create 3 moneyboxes
        moneyboxes_data = [
            {
                "name": "Test Box 1",
                "savings_amount": 0,
                "savings_target": None,
                "priority": 1,
            },
            {
                "name": "Test Box 2",
                "savings_amount": 0,
                "savings_target": None,
                "priority": 2,
            },
            {
                "name": "Test Box 3",
                "savings_amount": 0,
                "savings_target": None,
                "priority": 3,
            },
        ]

        for moneybox_data in moneyboxes_data:
            await self.db_manager.add_moneybox(
                moneybox_data=moneybox_data,
            )

    async def dataset_test_endpoint_update_moneybox__status_200__description_change(self) -> None:
        """The data generation function for test_case:
        `test_endpoint_update_moneybox__status_200__description_change`.
        """

        await self.truncate_tables()

        print(
            f"Create data for test ({self.test_case})",
            flush=True,
        )

        # create 1 moneybox
        moneyboxes_data = [
            {
                "name": "Test Box 1",
                "savings_amount": 0,
                "savings_target": None,
                "priority": 1,
            },
        ]

        for moneybox_data in moneyboxes_data:
            await self.db_manager.add_moneybox(
                moneybox_data=moneybox_data,
            )

    async def dataset_dataset_test_endpoint_update_moneybox__status_409__description_none(
        self,
    ) -> None:
        """The data generation function for test_case:
        `test_endpoint_update_moneybox__status_422__description_none`.
        """

        await self.truncate_tables()

        print(
            f"Create data for test ({self.test_case})",
            flush=True,
        )

        # create 1 moneybox
        moneyboxes_data = [
            {
                "name": "Test Box 1",
                "savings_amount": 0,
                "savings_target": None,
                "priority": 1,
            },
        ]

        for moneybox_data in moneyboxes_data:
            await self.db_manager.add_moneybox(
                moneybox_data=moneybox_data,
            )

    async def dataset_test_endpoint_update_moneybox__status_422__description_not_string_type(
        self,
    ) -> None:
        """The data generation function for test_case:
        `test_endpoint_update_moneybox__status_422__description_not_string_type`.
        """

        await self.truncate_tables()

        print(
            f"Create data for test ({self.test_case})",
            flush=True,
        )

        # create 1 moneybox
        moneyboxes_data = [
            {
                "name": "Test Box 1",
                "savings_amount": 0,
                "savings_target": None,
                "priority": 1,
            },
        ]

        for moneybox_data in moneyboxes_data:
            await self.db_manager.add_moneybox(
                moneybox_data=moneybox_data,
            )

    async def dataset_test_endpoint_update_moneybox__status_422__savings_amount_non_int_type(
        self,
    ) -> None:
        """The data generation function for test_case:
        `test_endpoint_update_moneybox__status_422__savings_amount_non_int_type`.
        """

        await self.truncate_tables()

        print(
            f"Create data for test ({self.test_case})",
            flush=True,
        )

        # create 1 moneybox
        moneyboxes_data = [
            {
                "name": "Test Box 1",
                "savings_amount": 0,
                "savings_target": None,
                "priority": 1,
            },
        ]

        for moneybox_data in moneyboxes_data:
            await self.db_manager.add_moneybox(
                moneybox_data=moneybox_data,
            )

    async def dataset_test_endpoint_update_moneybox__status_422__savings_amount_negative(
        self,
    ) -> None:
        """The data generation function for test_case:
        `test_endpoint_update_moneybox__status_422__savings_amount_negative`.
        """

        await self.truncate_tables()

        print(
            f"Create data for test ({self.test_case})",
            flush=True,
        )

        # create 1 moneybox
        moneyboxes_data = [
            {
                "name": "Test Box 1",
                "savings_amount": 0,
                "savings_target": None,
                "priority": 1,
            },
        ]

        for moneybox_data in moneyboxes_data:
            await self.db_manager.add_moneybox(
                moneybox_data=moneybox_data,
            )

    async def dataset_test_endpoint_update_moneybox__status_200__savings_amount_change(
        self,
    ) -> None:
        """The data generation function for test_case:
        `test_endpoint_update_moneybox__status_200__savings_amount_change`.
        """

        await self.truncate_tables()

        print(
            f"Create data for test ({self.test_case})",
            flush=True,
        )

        # create 1 moneybox
        moneyboxes_data = [
            {
                "name": "Test Box 1",
                "savings_amount": 0,
                "savings_target": None,
                "priority": 1,
            },
        ]

        for moneybox_data in moneyboxes_data:
            await self.db_manager.add_moneybox(
                moneybox_data=moneybox_data,
            )

    async def dataset_test_endpoint_update_moneybox__status_422__savings_amount_none(
        self,
    ) -> None:
        """The data generation function for test_case:
        `test_endpoint_update_moneybox__status_422__savings_amount_none`.
        """

        await self.truncate_tables()

        print(
            f"Create data for test ({self.test_case})",
            flush=True,
        )

        # create 1 moneybox
        moneyboxes_data = [
            {
                "name": "Test Box 1",
                "savings_amount": 0,
                "savings_target": None,
                "priority": 1,
            },
        ]

        for moneybox_data in moneyboxes_data:
            await self.db_manager.add_moneybox(
                moneybox_data=moneybox_data,
            )

    async def dataset_test_endpoint_update_moneybox__status_200__savings_target_none_change(
        self,
    ) -> None:
        """The data generation function for test_case:
        `test_endpoint_update_moneybox__status_200__savings_target_none_change`.
        """

        await self.truncate_tables()

        print(
            f"Create data for test ({self.test_case})",
            flush=True,
        )

        # create 1 moneybox
        moneyboxes_data = [
            {
                "name": "Test Box 1",
                "savings_amount": 0,
                "savings_target": 123,
                "priority": 1,
            },
        ]

        for moneybox_data in moneyboxes_data:
            await self.db_manager.add_moneybox(
                moneybox_data=moneybox_data,
            )

    async def dataset_test_endpoint_update_moneybox__status_200__savings_target_value_change(
        self,
    ) -> None:
        """The data generation function for test_case:
        `test_endpoint_update_moneybox__status_200__savings_target_none_change`.
        """

        await self.truncate_tables()

        print(
            f"Create data for test ({self.test_case})",
            flush=True,
        )

        # create 1 moneybox
        moneyboxes_data = [
            {
                "name": "Test Box 1",
                "savings_amount": 0,
                "savings_target": 123,
                "priority": 1,
            },
        ]

        for moneybox_data in moneyboxes_data:
            await self.db_manager.add_moneybox(
                moneybox_data=moneybox_data,
            )

    async def dataset_test_endpoint_update_moneybox__status_422_savings_target_non_int_type(
        self,
    ) -> None:
        """The data generation function for test_case:
        `test_endpoint_update_moneybox__status_422_savings_target_non_int_type`.
        """

        await self.truncate_tables()

        print(
            f"Create data for test ({self.test_case})",
            flush=True,
        )

        # create 1 moneybox
        moneyboxes_data = [
            {
                "name": "Test Box 1",
                "savings_amount": 0,
                "savings_target": 123,
                "priority": 1,
            },
        ]

        for moneybox_data in moneyboxes_data:
            await self.db_manager.add_moneybox(
                moneybox_data=moneybox_data,
            )

    async def dataset_test_endpoint_update_moneybox__status_422_savings_target_negative(
        self,
    ) -> None:
        """The data generation function for test_case:
        `test_endpoint_update_moneybox__status_422_savings_target_negative`.
        """

        await self.truncate_tables()

        print(
            f"Create data for test ({self.test_case})",
            flush=True,
        )

        # create 1 moneybox
        moneyboxes_data = [
            {
                "name": "Test Box 1",
                "savings_amount": 0,
                "savings_target": 123,
                "priority": 1,
            },
        ]

        for moneybox_data in moneyboxes_data:
            await self.db_manager.add_moneybox(
                moneybox_data=moneybox_data,
            )

    async def dataset_test_endpoint_delete_overflow_moneybox__status_405(self) -> None:
        """The data generation function for test_case:
        `test_endpoint_delete_overflow_moneybox__status_405`.
        """

        await self.truncate_tables()

    async def dataset_test_endpoint_update_overflow_moneybox__fail_409__modification_not_allowed(
        self,
    ) -> None:
        """The data generation function for test_case:
        `test_endpoint_update_overflow_moneybox__fail_409__modification_not_allowed`.
        """

        await self.truncate_tables()

        print(
            f"Create data for test ({self.test_case})",
            flush=True,
        )

        # create 3 moneyboxes
        moneyboxes_data = [
            {
                "name": "Test Box 1",
                "savings_amount": 0,
                "savings_target": None,
                "priority": 1,
            },
            {
                "name": "Test Box 2",
                "savings_amount": 0,
                "savings_target": None,
                "priority": 2,
            },
            {
                "name": "Test Box 3",
                "savings_amount": 0,
                "savings_target": None,
                "priority": 3,
            },
        ]

        for moneybox_data in moneyboxes_data:
            await self.db_manager.add_moneybox(
                moneybox_data=moneybox_data,
            )

    async def dataset_test_endpoint_update_moneybox__first_moneybox__status_422__fail_extra_fields(
        self,
    ) -> None:
        """The data generation function for test_case:
        `test_endpoint_update_moneybox__first_moneybox__status_422__fail_extra_fields`.
        """

        await self.truncate_tables()

        print(
            f"Create data for test ({self.test_case})",
            flush=True,
        )

        # create 2 moneyboxes
        moneyboxes_data = [
            {
                "name": "Test Box 1",
                "savings_amount": 0,
                "savings_target": None,
                "priority": 1,
            },
            {
                "name": "Test Box 2",
                "savings_amount": 0,
                "savings_target": None,
                "priority": 2,
            },
        ]

        for moneybox_data in moneyboxes_data:
            await self.db_manager.add_moneybox(
                moneybox_data=moneybox_data,
            )

    async def dataset_test_endpoint_first_moneybox__modified_at_checks(self) -> None:
        """The data generation function for test_case:
        `test_endpoint_first_moneybox__modified_at_checks`.
        """

        await self.truncate_tables()

        print(
            f"Create data for test ({self.test_case})",
            flush=True,
        )

        # create 1 moneybox
        moneyboxes_data = [
            {"name": "Test Box 1", "priority": 1},
        ]

        for moneybox_data in moneyboxes_data:
            await self.db_manager.add_moneybox(
                moneybox_data=moneybox_data,
            )

    async def dataset_test_endpoint_delete_second_moneybox__status_204(self) -> None:
        """The data generation function for test_case:
        `test_endpoint_delete_second_moneybox__status_204`.
        """

        await self.truncate_tables()

        # create 2 moneyboxes
        moneyboxes_data = [
            {
                "name": "Test Box 1",
                "savings_amount": 0,
                "savings_target": None,
                "priority": 1,
            },
            {
                "name": "Test Box 2",
                "savings_amount": 0,
                "savings_target": None,
                "priority": 2,
            },
        ]

        for moneybox_data in moneyboxes_data:
            await self.db_manager.add_moneybox(
                moneybox_data=moneybox_data,
            )

    async def dataset_test_endpoint_deposit_first_moneybox__status_200(
        self,
    ) -> None:
        """The data generation function for test_case:
        `test_endpoint_deposit_first_moneybox__status_200`.
        """

        await self.truncate_tables()

        # create 1 moneybox
        moneyboxes_data = [
            {
                "name": "Test Box 1",
                "savings_amount": 0,
                "savings_target": None,
                "priority": 1,
            },
        ]

        for moneybox_data in moneyboxes_data:
            await self.db_manager.add_moneybox(
                moneybox_data=moneybox_data,
            )

    async def dataset_test_endpoint_withdraw_first_moneybox__status_200(
        self,
    ) -> None:
        """The data generation function for test_case:
        `test_endpoint_withdraw_first_moneybox__status_200`.
        """

        await self.truncate_tables()

        # create 1 moneybox
        moneybox_data = {
            "name": "Test Box 1",
            "savings_amount": 0,
            "savings_target": None,
            "priority": 1,
        }

        moneybox = await self.db_manager.add_moneybox(
            moneybox_data=moneybox_data,
        )

        # add some amount to moneybox 1
        deposit_transaction_data = {
            "amount": 100,
            "description": "Bonus.",
        }

        await self.db_manager.add_amount(
            moneybox_id=moneybox["id"],
            deposit_transaction_data=deposit_transaction_data,
            transaction_type=TransactionType.DIRECT,
            transaction_trigger=TransactionTrigger.MANUALLY,
        )

    async def dataset_test_endpoint_withdraw_first_moneybox__status_409__balance_negative(
        self,
    ) -> None:
        """The data generation function for test_case:
        `test_endpoint_withdraw_first_moneybox__status_409__balance_negative`.
        """

        await self.truncate_tables()

        # create 1 moneybox
        moneyboxes_data = [
            {
                "name": "Test Box 1",
                "savings_amount": 0,
                "savings_target": None,
                "priority": 1,
            },
        ]

        for moneybox_data in moneyboxes_data:
            await self.db_manager.add_moneybox(
                moneybox_data=moneybox_data,
            )

    async def dataset_test_endpoint_transfer_amount_moneybox_second_to_third__status_204(
        self,
    ) -> None:
        """The data generation function for test_case:
        `test_endpoint_transfer_amount_moneybox_second_to_third__status_204`.
        """

        await self.truncate_tables()

        print(
            f"Create data for test ({self.test_case})",
            flush=True,
        )

        # create 3 moneyboxes
        moneyboxes_data = [
            {
                "name": "Test Box 1",
                "savings_amount": 0,
                "savings_target": None,
                "priority": 1,
            },
            {
                "name": "Test Box 2",
                "savings_amount": 0,
                "savings_target": None,
                "priority": 2,
            },
            {
                "name": "Test Box 3",
                "savings_amount": 0,
                "savings_target": None,
                "priority": 3,
            },
        ]

        moneyboxes = []
        for moneybox_data in moneyboxes_data:
            moneybox = await self.db_manager.add_moneybox(
                moneybox_data=moneybox_data,
            )
            moneyboxes.append(moneybox)

        # add some amount to second moneybox
        await self.db_manager.add_amount(
            moneybox_id=moneyboxes[1]["id"],
            deposit_transaction_data={
                "amount": 1000,
                "description": "Unit Test.",
            },
            transaction_type=TransactionType.DIRECT,
            transaction_trigger=TransactionTrigger.MANUALLY,
        )

    async def dataset_test_endpoint_transfer_amount_moneybox_second_to_third__status_204__missing_description_field(
        self,
    ) -> None:
        """The data generation function for test_case:
        `test_endpoint_transfer_amount_moneybox_second_to_third__status_204__missing_description_field`.
        """

        await self.truncate_tables()

        print(
            f"Create data for test ({self.test_case})",
            flush=True,
        )

        # create 3 moneyboxes
        moneyboxes_data = [
            {
                "name": "Test Box 1",
                "savings_amount": 0,
                "savings_target": None,
                "priority": 1,
            },
            {
                "name": "Test Box 2",
                "savings_amount": 0,
                "savings_target": None,
                "priority": 2,
            },
            {
                "name": "Test Box 3",
                "savings_amount": 0,
                "savings_target": None,
                "priority": 3,
            },
        ]

        moneyboxes = []
        for moneybox_data in moneyboxes_data:
            moneybox = await self.db_manager.add_moneybox(
                moneybox_data=moneybox_data,
            )
            moneyboxes.append(moneybox)

        # add some amount to moneybox with id 2
        await self.db_manager.add_amount(
            moneybox_id=moneyboxes[1]["id"],
            deposit_transaction_data={
                "amount": 1000,
                "description": "Unit Test.",
            },
            transaction_type=TransactionType.DIRECT,
            transaction_trigger=TransactionTrigger.MANUALLY,
        )

    async def dataset_test_endpoint_transfer_amount_moneybox_second_to_third__status_404__to_moneybox_third_not_found(
        self,
    ) -> None:
        """The data generation function for test_case:
        `test_endpoint_transfer_amount_moneybox_second_to_third__status_404__to_moneybox_third_not_found`.
        """

        await self.truncate_tables()

        # create 2 moneyboxes
        moneyboxes_data = [
            {
                "name": "Test Box 1",
                "savings_amount": 0,
                "savings_target": None,
                "priority": 1,
            },
            {
                "name": "Test Box 2",
                "savings_amount": 0,
                "savings_target": None,
                "priority": 2,
            },
        ]

        for moneybox_data in moneyboxes_data:
            await self.db_manager.add_moneybox(
                moneybox_data=moneybox_data,
            )

    async def dataset_test_get_prioritylist(
        self,
    ) -> None:
        """The data generation function for test_case:
        `test_get_priority_list`.
        """

        await self.truncate_tables()

        # create 2 moneyboxes
        moneyboxes_data = [
            {
                "name": "Test Box 1",
                "savings_amount": 0,
                "savings_target": None,
                "priority": 1,
            },
            {
                "name": "Test Box 2",
                "savings_amount": 0,
                "savings_target": None,
                "priority": 2,
            },
        ]

        for moneybox_data in moneyboxes_data:
            await self.db_manager.add_moneybox(
                moneybox_data=moneybox_data,
            )

    async def dataset_test_update_prioritylist(
        self,
    ) -> None:
        """The data generation function for test_case:
        `test_update_priority_list`.
        """

        await self.truncate_tables()

        # create 2 moneyboxes
        moneyboxes_data = [
            {
                "name": "Test Box 1",
                "savings_amount": 0,
                "savings_target": None,
                "priority": 1,
            },
            {
                "name": "Test Box 2",
                "savings_amount": 0,
                "savings_target": None,
                "priority": 2,
            },
        ]

        for moneybox_data in moneyboxes_data:
            await self.db_manager.add_moneybox(
                moneybox_data=moneybox_data,
            )

    async def dataset_test_automated_savings_valid(self) -> None:
        """The data generation function for test_case:
        `test_automated_savings_valid`.
        """

        await self.truncate_tables()

        # create app settings
        app_settings_data = {
            "send_reports_via_email": False,
            "user_email_address": None,
            "is_automated_saving_active": True,
            "savings_amount": 150,
            "overflow_moneybox_automated_savings_mode": OverflowMoneyboxAutomatedSavingsModeType.COLLECT,
            "is_active": True,
            "note": "",
        }

        async with self.db_manager.async_sessionmaker.begin() as session:
            stmt = insert(AppSettings).values(**app_settings_data)
            await session.execute(stmt)

        moneyboxes_data = [
            {
                "name": "Test Box 1",
                "savings_amount": 5,
                "savings_target": 5,
                "priority": 1,
            },
            {
                "name": "Test Box 2",
                "savings_amount": 10,
                "savings_target": 5,
                "priority": 2,
            },
            {
                "name": "Test Box 3",
                "savings_amount": 15,
                "savings_target": None,
                "priority": 3,
            },
            {
                "name": "Test Box 4",
                "savings_amount": 20,
                "savings_target": 50,
                "priority": 4,
            },
            {
                "name": "Test Box 5",
                "savings_amount": 0,
                "savings_target": 0,
                "priority": 5,
            },
            {
                "name": "Test Box 6",
                "savings_amount": 25,
                "savings_target": 0,
                "priority": 6,
            },
        ]

        for moneybox_data in moneyboxes_data:
            await self.db_manager.add_moneybox(
                moneybox_data=moneybox_data,
            )

    async def dataset_test_automated_savings_overflow_moneybox_mode_add_to_amount(
        self,
    ) -> None:
        """The data generation function for test_case:
        `test_automated_savings_overflow_moneybox_mode_add_to_amount`.
        """

        await self.truncate_tables()

        # create app settings
        app_settings_data = {
            "send_reports_via_email": False,
            "user_email_address": None,
            "is_automated_saving_active": True,
            "savings_amount": 50,
            "overflow_moneybox_automated_savings_mode": OverflowMoneyboxAutomatedSavingsModeType.ADD_TO_AUTOMATED_SAVINGS_AMOUNT,
            "is_active": True,
            "note": "",
        }

        async with self.db_manager.async_sessionmaker.begin() as session:
            stmt = insert(AppSettings).values(**app_settings_data)
            await session.execute(stmt)

        overflow_moneybox = (
            await self.db_manager._get_overflow_moneybox()  # pylint: disable=protected-access
        )
        await self.db_manager.add_amount(
            moneybox_id=overflow_moneybox.id,
            deposit_transaction_data={
                "amount": 100,
                "description": "Test Case",
            },
            transaction_type=TransactionType.DIRECT,
            transaction_trigger=TransactionTrigger.MANUALLY,
        )

        moneyboxes_data = [
            {
                "name": "Test Box 1",
                "savings_amount": 5,
                "savings_target": 5,
                "priority": 1,
            },
            {
                "name": "Test Box 2",
                "savings_amount": 10,
                "savings_target": 5,
                "priority": 2,
            },
            {
                "name": "Test Box 3",
                "savings_amount": 15,
                "savings_target": None,
                "priority": 3,
            },
            {
                "name": "Test Box 4",
                "savings_amount": 20,
                "savings_target": 50,
                "priority": 4,
            },
            {
                "name": "Test Box 5",
                "savings_amount": 0,
                "savings_target": 0,
                "priority": 5,
            },
            {
                "name": "Test Box 6",
                "savings_amount": 25,
                "savings_target": 0,
                "priority": 6,
            },
        ]

        for moneybox_data in moneyboxes_data:
            await self.db_manager.add_moneybox(
                moneybox_data=moneybox_data,
            )

    async def dataset_test_automated_savings_overflow_moneybox_mode_fill_up(
        self,
    ) -> None:
        """The data generation function for test_case:
        `test_automated_savings_overflow_moneybox_mode_fill_up`.
        """

        await self.truncate_tables()

        # create app settings
        app_settings_data = {
            "send_reports_via_email": False,
            "user_email_address": None,
            "is_automated_saving_active": True,
            "savings_amount": 150,
            "overflow_moneybox_automated_savings_mode": OverflowMoneyboxAutomatedSavingsModeType.FILL_UP_LIMITED_MONEYBOXES,
            "is_active": True,
            "note": "",
        }

        async with self.db_manager.async_sessionmaker.begin() as session:
            stmt = insert(AppSettings).values(**app_settings_data)
            await session.execute(stmt)

        moneyboxes_data = [
            {
                "name": "Test Box 1",
                "savings_amount": 5,
                "savings_target": 5,
                "priority": 1,
            },
            {
                "name": "Test Box 2",
                "savings_amount": 10,
                "savings_target": 5,
                "priority": 2,
            },
            {
                "name": "Test Box 3",
                "savings_amount": 15,
                "savings_target": None,
                "priority": 3,
            },
            {
                "name": "Test Box 4",
                "savings_amount": 20,
                "savings_target": 50,
                "priority": 4,
            },
            {
                "name": "Test Box 5",
                "savings_amount": 0,
                "savings_target": 0,
                "priority": 5,
            },
            {
                "name": "Test Box 6",
                "savings_amount": 25,
                "savings_target": 0,
                "priority": 6,
            },
        ]

        for moneybox_data in moneyboxes_data:
            await self.db_manager.add_moneybox(
                moneybox_data=moneybox_data,
            )

    async def dataset_test_automated_savings_overflow_moneybox_mode_ratio(
        self,
    ) -> None:
        """The data generation function for test_case:
        `test_automated_savings_overflow_moneybox_mode_ratio`.
        """

        await self.truncate_tables()

        # create app settings
        app_settings_data = {
            "send_reports_via_email": False,
            "user_email_address": None,
            "is_automated_saving_active": True,
            "savings_amount": 150,
            "overflow_moneybox_automated_savings_mode": OverflowMoneyboxAutomatedSavingsModeType.RATIO,
            "is_active": True,
            "note": "",
        }

        async with self.db_manager.async_sessionmaker.begin() as session:
            stmt = insert(AppSettings).values(**app_settings_data)
            await session.execute(stmt)

        moneyboxes_data = [
            {
                "name": "Test Box 1",
                "savings_amount": 5,  # ratio: 6 -> 6 extra BUT REFUSED (-> in overflow), result 5
                "savings_target": 5,
                "priority": 1,
            },
            {
                "name": "Test Box 2",
                "savings_amount": 10,  # ratio: 13 -> 13 extra BUT REFUSED (-> in overflow), result 5
                "savings_target": 5,
                "priority": 2,
            },
            {
                "name": "Test Box 3",
                "savings_amount": 15,  # ratio: 20 -> 21 extra, result 36
                "savings_target": None,
                "priority": 3,
            },
            {
                "name": "Test Box 4",
                "savings_amount": 20,  # ratio: 26 -> 27 extra, result 47
                "savings_target": 50,
                "priority": 4,
            },
            {
                "name": "Test Box 5",
                "savings_amount": 0,  # ratio: 0 -> no extra
                "savings_target": 0,
                "priority": 5,
            },
            {
                "name": "Test Box 6",
                "savings_amount": 25,  # ratio: 33 -> 34 extra BUT REFUSED (-> in overflow), result 0
                "savings_target": 0,
                "priority": 6,
            },
            # rest: 105 for Overflow Moneybox RATIO distribution available
            # total savings amount: 75
            # Overflow Moneybox: 105 ratio distribution
            # -> 105 - (21+27) = 57 rest in overflow moneybox
        ]

        for moneybox_data in moneyboxes_data:
            await self.db_manager.add_moneybox(
                moneybox_data=moneybox_data,
            )

    async def dataset_test_automated_savings_overflow_moneybox_mode_ratio__only_overflow_moneybox(
        self,
    ) -> None:
        """The data generation function for test_case:
        `test_automated_savings_overflow_moneybox_mode_ratio__only_overflow_moneybox`.
        """

        await self.truncate_tables()

        # create app settings
        app_settings_data = {
            "send_reports_via_email": False,
            "user_email_address": None,
            "is_automated_saving_active": True,
            "savings_amount": 150,
            "overflow_moneybox_automated_savings_mode": OverflowMoneyboxAutomatedSavingsModeType.RATIO,
            "is_active": True,
            "note": "",
        }

        async with self.db_manager.async_sessionmaker.begin() as session:
            stmt = insert(AppSettings).values(**app_settings_data)
            await session.execute(stmt)

    async def dataset_test_automated_savings_overflow_moneybox_mode_collect__only_overflow_moneybox(
        self,
    ) -> None:
        """The data generation function for test_case:
        `test_automated_savings_overflow_moneybox_mode_collect__only_overflow_moneybox`.
        """

        await self.truncate_tables()

        # create app settings
        app_settings_data = {
            "send_reports_via_email": False,
            "user_email_address": None,
            "is_automated_saving_active": True,
            "savings_amount": 150,
            "overflow_moneybox_automated_savings_mode": OverflowMoneyboxAutomatedSavingsModeType.COLLECT,
            "is_active": True,
            "note": "",
        }

        async with self.db_manager.async_sessionmaker.begin() as session:
            stmt = insert(AppSettings).values(**app_settings_data)
            await session.execute(stmt)

    async def dataset_test_automated_savings_overflow_moneybox_mode_add__only_overflow_moneybox(
        self,
    ) -> None:
        """The data generation function for test_case:
        `test_automated_savings_overflow_moneybox_mode_add__only_overflow_moneybox`.
        """

        await self.truncate_tables()

        # create app settings
        app_settings_data = {
            "send_reports_via_email": False,
            "user_email_address": None,
            "is_automated_saving_active": True,
            "savings_amount": 150,
            "overflow_moneybox_automated_savings_mode": OverflowMoneyboxAutomatedSavingsModeType.ADD_TO_AUTOMATED_SAVINGS_AMOUNT,
            "is_active": True,
            "note": "",
        }

        async with self.db_manager.async_sessionmaker.begin() as session:
            stmt = insert(AppSettings).values(**app_settings_data)
            await session.execute(stmt)

    async def dataset_test_automated_savings_overflow_moneybox_mode_fill__only_overflow_moneybox(
        self,
    ) -> None:
        """The data generation function for test_case:
        `test_automated_savings_overflow_moneybox_mode_fill__only_overflow_moneybox`.
        """

        await self.truncate_tables()

        # create app settings
        app_settings_data = {
            "send_reports_via_email": False,
            "user_email_address": None,
            "is_automated_saving_active": True,
            "savings_amount": 150,
            "overflow_moneybox_automated_savings_mode": OverflowMoneyboxAutomatedSavingsModeType.FILL_UP_LIMITED_MONEYBOXES,
            "is_active": True,
            "note": "",
        }

        async with self.db_manager.async_sessionmaker.begin() as session:
            stmt = insert(AppSettings).values(**app_settings_data)
            await session.execute(stmt)

    async def dataset_test_task_automated_savings_schedule(self) -> None:
        """The data generation function for test_case:
        `test_task_automated_savings_schedule`.
        """

        await self.truncate_tables()

        # create app settings
        app_settings_data = {
            "send_reports_via_email": True,
            "user_email_address": "pythbuster@gmail.com",
            "is_automated_saving_active": True,
            "savings_amount": 150,
            "overflow_moneybox_automated_savings_mode": OverflowMoneyboxAutomatedSavingsModeType.FILL_UP_LIMITED_MONEYBOXES,
            "is_active": True,
            "note": "",
        }

        async with self.db_manager.async_sessionmaker.begin() as session:
            stmt = insert(AppSettings).values(**app_settings_data)
            await session.execute(stmt)

        moneyboxes_data = [
            {
                "name": "Test Box 1",
                "savings_amount": 5,
                "savings_target": 5,
                "priority": 1,
            },
            {
                "name": "Test Box 2",
                "savings_amount": 10,
                "savings_target": 5,
                "priority": 2,
            },
            {
                "name": "Test Box 3",
                "savings_amount": 15,
                "savings_target": None,
                "priority": 3,
            },
            {
                "name": "Test Box 4",
                "savings_amount": 20,
                "savings_target": 50,
                "priority": 4,
            },
            {
                "name": "Test Box 5",
                "savings_amount": 0,
                "savings_target": 0,
                "priority": 5,
            },
            {
                "name": "Test Box 6",
                "savings_amount": 25,
                "savings_target": 0,
                "priority": 6,
            },
        ]

        for moneybox_data in moneyboxes_data:
            await self.db_manager.add_moneybox(
                moneybox_data=moneybox_data,
            )

    async def dataset_test_task_automated_savings_dont_schedule(self) -> None:
        """The data generation function for test_case:
        `test_task_automated_savings_dont_schedule`.
        """

        await self.truncate_tables()

        # create app settings
        app_settings_data = {
            "send_reports_via_email": True,
            "user_email_address": "pythbuster@gmail.com",
            "is_automated_saving_active": True,
            "savings_amount": 150,
            "overflow_moneybox_automated_savings_mode": OverflowMoneyboxAutomatedSavingsModeType.FILL_UP_LIMITED_MONEYBOXES,
            "is_active": True,
            "note": "",
        }

        async with self.db_manager.async_sessionmaker.begin() as session:
            stmt = insert(AppSettings).values(**app_settings_data)
            await session.execute(stmt)

        moneyboxes_data = [
            {
                "name": "Test Box 1",
                "savings_amount": 5,
                "savings_target": 5,
                "priority": 1,
            },
            {
                "name": "Test Box 2",
                "savings_amount": 10,
                "savings_target": 5,
                "priority": 2,
            },
            {
                "name": "Test Box 3",
                "savings_amount": 15,
                "savings_target": None,
                "priority": 3,
            },
            {
                "name": "Test Box 4",
                "savings_amount": 20,
                "savings_target": 50,
                "priority": 4,
            },
            {
                "name": "Test Box 5",
                "savings_amount": 0,
                "savings_target": 0,
                "priority": 5,
            },
            {
                "name": "Test Box 6",
                "savings_amount": 25,
                "savings_target": 0,
                "priority": 6,
            },
        ]

        for moneybox_data in moneyboxes_data:
            await self.db_manager.add_moneybox(
                moneybox_data=moneybox_data,
            )

    async def dataset_test_task_automated_savings_no_email_send(self) -> None:
        """The data generation function for test_case:
        `test_task_automated_savings_no_email_send`.
        """

        await self.truncate_tables()

        # create app settings
        app_settings_data = {
            "send_reports_via_email": False,
            "user_email_address": "pythbuster@gmail.com",
            "is_automated_saving_active": True,
            "savings_amount": 150,
            "overflow_moneybox_automated_savings_mode": OverflowMoneyboxAutomatedSavingsModeType.FILL_UP_LIMITED_MONEYBOXES,
            "is_active": True,
            "note": "",
        }

        async with self.db_manager.async_sessionmaker.begin() as session:
            stmt = insert(AppSettings).values(**app_settings_data)
            await session.execute(stmt)

        moneyboxes_data = [
            {
                "name": "Test Box 1",
                "savings_amount": 5,
                "savings_target": 5,
                "priority": 1,
            },
            {
                "name": "Test Box 2",
                "savings_amount": 10,
                "savings_target": 5,
                "priority": 2,
            },
            {
                "name": "Test Box 3",
                "savings_amount": 15,
                "savings_target": None,
                "priority": 3,
            },
            {
                "name": "Test Box 4",
                "savings_amount": 20,
                "savings_target": 50,
                "priority": 4,
            },
            {
                "name": "Test Box 5",
                "savings_amount": 0,
                "savings_target": 0,
                "priority": 5,
            },
            {
                "name": "Test Box 6",
                "savings_amount": 25,
                "savings_target": 0,
                "priority": 6,
            },
        ]

        for moneybox_data in moneyboxes_data:
            await self.db_manager.add_moneybox(
                moneybox_data=moneybox_data,
            )

    async def dataset_test_task_automated_savings_no_savings_active(self) -> None:
        """The data generation function for test_case:
        `test_task_automated_savings_no_savings_active`.
        """

        await self.truncate_tables()

        # create app settings
        app_settings_data = {
            "send_reports_via_email": False,
            "user_email_address": "pythbuster@gmail.com",
            "is_automated_saving_active": False,
            "savings_amount": 150,
            "overflow_moneybox_automated_savings_mode": OverflowMoneyboxAutomatedSavingsModeType.FILL_UP_LIMITED_MONEYBOXES,
            "is_active": True,
            "note": "",
        }

        async with self.db_manager.async_sessionmaker.begin() as session:
            stmt = insert(AppSettings).values(**app_settings_data)
            await session.execute(stmt)

        moneyboxes_data = [
            {
                "name": "Test Box 1",
                "savings_amount": 5,
                "savings_target": 5,
                "priority": 1,
            },
            {
                "name": "Test Box 2",
                "savings_amount": 10,
                "savings_target": 5,
                "priority": 2,
            },
            {
                "name": "Test Box 3",
                "savings_amount": 15,
                "savings_target": None,
                "priority": 3,
            },
            {
                "name": "Test Box 4",
                "savings_amount": 20,
                "savings_target": 50,
                "priority": 4,
            },
            {
                "name": "Test Box 5",
                "savings_amount": 0,
                "savings_target": 0,
                "priority": 5,
            },
            {
                "name": "Test Box 6",
                "savings_amount": 25,
                "savings_target": 0,
                "priority": 6,
            },
        ]

        for moneybox_data in moneyboxes_data:
            await self.db_manager.add_moneybox(
                moneybox_data=moneybox_data,
            )

    async def dataset_test_send_testemail_success(self) -> None:
        """The data generation function for test_case:
        `test_send_testemail_success`.
        """

        await self.truncate_tables()

        # create app settings
        distribution_amount = 150
        app_settings_data = {
            "send_reports_via_email": True,
            "user_email_address": "pythbuster@gmail.com",
            "is_automated_saving_active": False,
            "savings_amount": distribution_amount,
            "overflow_moneybox_automated_savings_mode": OverflowMoneyboxAutomatedSavingsModeType.FILL_UP_LIMITED_MONEYBOXES,
            "is_active": True,
            "note": "",
        }

        async with self.db_manager.async_sessionmaker.begin() as session:
            stmt = insert(AppSettings).values(**app_settings_data)
            await session.execute(stmt)

    async def dataset_test_task_email_sending__one_of_one(self) -> None:
        """The data generation function for test_case:
        `test_task_email_sending__one_of_one`.
        """

        await self.truncate_tables()

        # create app settings
        distribution_amount = 150
        app_settings_data = {
            "send_reports_via_email": True,
            "user_email_address": "pythbuster@gmail.com",
            "is_automated_saving_active": False,
            "savings_amount": distribution_amount,
            "overflow_moneybox_automated_savings_mode": OverflowMoneyboxAutomatedSavingsModeType.FILL_UP_LIMITED_MONEYBOXES,
            "is_active": True,
            "note": "",
        }

        async with self.db_manager.async_sessionmaker.begin() as session:
            stmt = insert(AppSettings).values(**app_settings_data)
            await session.execute(stmt)

        moneyboxes_data = [
            {
                "name": "Test Box 1",
                "savings_amount": 5,
                "savings_target": 5,
                "priority": 1,
            },
            {
                "name": "Test Box 2",
                "savings_amount": 10,
                "savings_target": 5,
                "priority": 2,
            },
            {
                "name": "Test Box 3",
                "savings_amount": 15,
                "savings_target": None,
                "priority": 3,
            },
            {
                "name": "Test Box 4",
                "savings_amount": 20,
                "savings_target": 50,
                "priority": 4,
            },
            {
                "name": "Test Box 5",
                "savings_amount": 0,
                "savings_target": 0,
                "priority": 5,
            },
            {
                "name": "Test Box 6",
                "savings_amount": 25,
                "savings_target": 0,
                "priority": 6,
            },
        ]

        for moneybox_data in moneyboxes_data:
            await self.db_manager.add_moneybox(
                moneybox_data=moneybox_data,
            )

        # log automated saving
        action_logs_data: list[dict[str, Any]] = [
            {
                "action": ActionType.APPLIED_AUTOMATED_SAVING,
                "action_at": datetime.now(tz=timezone.utc) - timedelta(days=5),
                "details": jsonable_encoder(
                    app_settings_data | {"distribution_amount": distribution_amount}
                ),
            }
        ]

        async with self.db_manager.async_sessionmaker.begin() as session:
            for action_log_data in action_logs_data:
                await self.db_manager.add_action_log(
                    session=session,
                    automated_savings_log_data=action_log_data,
                )

    async def dataset_test_task_email_sending__two_of_two(self) -> None:
        """The data generation function for test_case:
        `test_task_email_sending__two_of_two`.
        """

        await self.truncate_tables()

        # create app settings
        distribution_amount = 150
        app_settings_data = {
            "send_reports_via_email": True,
            "user_email_address": "pythbuster@gmail.com",
            "is_automated_saving_active": False,
            "savings_amount": distribution_amount,
            "overflow_moneybox_automated_savings_mode": OverflowMoneyboxAutomatedSavingsModeType.FILL_UP_LIMITED_MONEYBOXES,
            "is_active": True,
            "note": "",
        }

        async with self.db_manager.async_sessionmaker.begin() as session:
            stmt = insert(AppSettings).values(**app_settings_data)
            await session.execute(stmt)

        moneyboxes_data = [
            {
                "name": "Test Box 1",
                "savings_amount": 5,
                "savings_target": 5,
                "priority": 1,
            },
            {
                "name": "Test Box 2",
                "savings_amount": 10,
                "savings_target": 5,
                "priority": 2,
            },
            {
                "name": "Test Box 3",
                "savings_amount": 15,
                "savings_target": None,
                "priority": 3,
            },
            {
                "name": "Test Box 4",
                "savings_amount": 20,
                "savings_target": 50,
                "priority": 4,
            },
            {
                "name": "Test Box 5",
                "savings_amount": 0,
                "savings_target": 0,
                "priority": 5,
            },
            {
                "name": "Test Box 6",
                "savings_amount": 25,
                "savings_target": 0,
                "priority": 6,
            },
        ]

        for moneybox_data in moneyboxes_data:
            await self.db_manager.add_moneybox(
                moneybox_data=moneybox_data,
            )

        # log automated saving
        action_logs_data: list[dict[str, Any]] = [
            {
                "action": ActionType.APPLIED_AUTOMATED_SAVING,
                "action_at": datetime.now(tz=timezone.utc) - timedelta(days=62),
                "details": jsonable_encoder(
                    app_settings_data | {"distribution_amount": distribution_amount}
                ),
            },
            {
                "action": ActionType.APPLIED_AUTOMATED_SAVING,
                "action_at": datetime.now(tz=timezone.utc) - timedelta(days=31),
                "details": jsonable_encoder(
                    app_settings_data | {"distribution_amount": distribution_amount}
                ),
            },
        ]

        async with self.db_manager.async_sessionmaker.begin() as session:
            for action_log_data in action_logs_data:
                await self.db_manager.add_action_log(
                    session=session,
                    automated_savings_log_data=action_log_data,
                )

    async def dataset_test_task_email_sending__two_of_three(self) -> None:
        """The data generation function for test_case:
        `test_task_email_sending__two_of_three`.
        """

        await self.truncate_tables()

        # create app settings
        distribution_amount = 150
        app_settings_data = {
            "send_reports_via_email": True,
            "user_email_address": "pythbuster@gmail.com",
            "is_automated_saving_active": False,
            "savings_amount": distribution_amount,
            "overflow_moneybox_automated_savings_mode": OverflowMoneyboxAutomatedSavingsModeType.FILL_UP_LIMITED_MONEYBOXES,
            "is_active": True,
            "note": "",
        }

        async with self.db_manager.async_sessionmaker.begin() as session:
            stmt = insert(AppSettings).values(**app_settings_data)
            await session.execute(stmt)

        moneyboxes_data = [
            {
                "name": "Test Box 1",
                "savings_amount": 5,
                "savings_target": 5,
                "priority": 1,
            },
            {
                "name": "Test Box 2",
                "savings_amount": 10,
                "savings_target": 5,
                "priority": 2,
            },
            {
                "name": "Test Box 3",
                "savings_amount": 15,
                "savings_target": None,
                "priority": 3,
            },
            {
                "name": "Test Box 4",
                "savings_amount": 20,
                "savings_target": 50,
                "priority": 4,
            },
            {
                "name": "Test Box 5",
                "savings_amount": 0,
                "savings_target": 0,
                "priority": 5,
            },
            {
                "name": "Test Box 6",
                "savings_amount": 25,
                "savings_target": 0,
                "priority": 6,
            },
        ]

        for moneybox_data in moneyboxes_data:
            await self.db_manager.add_moneybox(
                moneybox_data=moneybox_data,
            )

        # log automated saving
        action_logs_data: list[dict[str, Any]] = [
            {
                "action": ActionType.APPLIED_AUTOMATED_SAVING,
                "action_at": datetime.now(tz=timezone.utc) - timedelta(days=93),
                "details": jsonable_encoder(
                    app_settings_data | {"distribution_amount": distribution_amount}
                ),
            },
            {
                "action": ActionType.APPLIED_AUTOMATED_SAVING,
                "action_at": datetime.now(tz=timezone.utc) - timedelta(days=62),
                "details": jsonable_encoder(
                    app_settings_data
                    | {"distribution_amount": distribution_amount, "report_sent": True}
                ),
            },
            {
                "action": ActionType.APPLIED_AUTOMATED_SAVING,
                "action_at": datetime.now(tz=timezone.utc) - timedelta(days=31),
                "details": jsonable_encoder(
                    app_settings_data | {"distribution_amount": distribution_amount}
                ),
            },
        ]

        async with self.db_manager.async_sessionmaker.begin() as session:
            for action_log_data in action_logs_data:
                await self.db_manager.add_action_log(
                    session=session,
                    automated_savings_log_data=action_log_data,
                )

    async def dataset_test_reset_database_keep_app_settings(self) -> None:
        """The data generation function for test_case:
        `test_reset_database_keep_app_settings`.
        """

        await self.truncate_tables()

        # create app settings
        app_settings_data = {
            "send_reports_via_email": False,
            "user_email_address": "pythbuster@gmail.com",
            "is_automated_saving_active": False,
            "savings_amount": 150,
            "overflow_moneybox_automated_savings_mode": OverflowMoneyboxAutomatedSavingsModeType.FILL_UP_LIMITED_MONEYBOXES,
            "is_active": True,
            "note": "",
        }

        async with self.db_manager.async_sessionmaker.begin() as session:
            stmt = insert(AppSettings).values(**app_settings_data)
            await session.execute(stmt)

        moneyboxes_data = [
            {
                "name": "Test Box 1",
                "savings_amount": 5,
                "savings_target": 5,
                "priority": 1,
            },
        ]

        for moneybox_data in moneyboxes_data:
            await self.db_manager.add_moneybox(
                moneybox_data=moneybox_data,
            )

    async def dataset_test_reset_database_delete_app_settings(self) -> None:
        """The data generation function for test_case:
        `test_reset_database_delete_app_settings`.
        """

        await self.truncate_tables()

        # create app settings
        app_settings_data = {
            "send_reports_via_email": False,
            "user_email_address": "pythbuster@gmail.com",
            "is_automated_saving_active": False,
            "savings_amount": 150,
            "overflow_moneybox_automated_savings_mode": OverflowMoneyboxAutomatedSavingsModeType.FILL_UP_LIMITED_MONEYBOXES,
            "is_active": True,
            "note": "",
        }

        async with self.db_manager.async_sessionmaker.begin() as session:
            stmt = insert(AppSettings).values(**app_settings_data)
            await session.execute(stmt)

        moneyboxes_data = [
            {
                "name": "Test Box 1",
                "savings_amount": 5,
                "savings_target": 5,
                "priority": 1,
            },
            {
                "name": "Test Box 2",
                "savings_amount": 10,
                "savings_target": 5,
                "priority": 2,
            },
            {
                "name": "Test Box 3",
                "savings_amount": 15,
                "savings_target": None,
                "priority": 3,
            },
            {
                "name": "Test Box 4",
                "savings_amount": 20,
                "savings_target": 50,
                "priority": 4,
            },
            {
                "name": "Test Box 5",
                "savings_amount": 0,
                "savings_target": 0,
                "priority": 5,
            },
            {
                "name": "Test Box 6",
                "savings_amount": 25,
                "savings_target": 0,
                "priority": 6,
            },
        ]

        for moneybox_data in moneyboxes_data:
            await self.db_manager.add_moneybox(
                moneybox_data=moneybox_data,
            )

    async def dataset_test_reset_app_keep_app_settings(self) -> None:
        """The data generation function for test_case:
        `test_reset_database_keep_app_settings`.
        """

        await self.truncate_tables()

        # create app settings
        app_settings_data = {
            "send_reports_via_email": False,
            "user_email_address": "pythbuster@gmail.com",
            "is_automated_saving_active": False,
            "savings_amount": 150,
            "overflow_moneybox_automated_savings_mode": OverflowMoneyboxAutomatedSavingsModeType.FILL_UP_LIMITED_MONEYBOXES,
            "is_active": True,
            "note": "",
        }

        async with self.db_manager.async_sessionmaker.begin() as session:
            stmt = insert(AppSettings).values(**app_settings_data)
            await session.execute(stmt)

        moneyboxes_data = [
            {
                "name": "Test Box 1",
                "savings_amount": 5,
                "savings_target": 5,
                "priority": 1,
            },
        ]

        for moneybox_data in moneyboxes_data:
            await self.db_manager.add_moneybox(
                moneybox_data=moneybox_data,
            )

    async def dataset_test_reset_app_delete_app_settings(self) -> None:
        """The data generation function for test_case:
        `test_reset_app_delete_app_settings`.
        """

        await self.truncate_tables()

        # create app settings
        app_settings_data = {
            "send_reports_via_email": False,
            "user_email_address": "pythbuster@gmail.com",
            "is_automated_saving_active": False,
            "savings_amount": 150,
            "overflow_moneybox_automated_savings_mode": OverflowMoneyboxAutomatedSavingsModeType.FILL_UP_LIMITED_MONEYBOXES,
            "is_active": True,
            "note": "",
        }

        async with self.db_manager.async_sessionmaker.begin() as session:
            stmt = insert(AppSettings).values(**app_settings_data)
            await session.execute(stmt)

        moneyboxes_data = [
            {
                "name": "Test Box 1",
                "savings_amount": 5,
                "savings_target": 5,
                "priority": 1,
            },
        ]

        for moneybox_data in moneyboxes_data:
            await self.db_manager.add_moneybox(
                moneybox_data=moneybox_data,
            )

    async def dataset_test_export_sql_dump(self) -> None:
        """The data generation function for test_case:
        `test_export_sql_dump`.
        """

        await self.truncate_tables()

        # create app settings
        app_settings_data = {
            "send_reports_via_email": False,
            "user_email_address": "pythbuster@gmail.com",
            "is_automated_saving_active": False,
            "savings_amount": 150,
            "overflow_moneybox_automated_savings_mode": OverflowMoneyboxAutomatedSavingsModeType.FILL_UP_LIMITED_MONEYBOXES,
            "is_active": True,
            "note": "",
        }

        async with self.db_manager.async_sessionmaker.begin() as session:
            stmt = insert(AppSettings).values(**app_settings_data)
            await session.execute(stmt)

        moneyboxes_data = [
            {
                "name": "Test Box 1",
            },
        ]

        for moneybox_data in moneyboxes_data:
            await self.db_manager.add_moneybox(
                moneybox_data=moneybox_data,
            )

    async def dataset_test_import_sql_dump(self) -> None:
        """The data generation function for test_case:
        `test_import_sql_dump`.
        """

        await self.truncate_tables()

        # create app settings
        app_settings_data = {
            "send_reports_via_email": True,
            "user_email_address": "pythbuster@gmail.com",
            "is_automated_saving_active": True,
            "savings_amount": 0,
            "overflow_moneybox_automated_savings_mode": OverflowMoneyboxAutomatedSavingsModeType.FILL_UP_LIMITED_MONEYBOXES,
            "is_active": False,
            "note": "",
        }

        async with self.db_manager.async_sessionmaker.begin() as session:
            stmt = insert(AppSettings).values(**app_settings_data)
            await session.execute(stmt)

        moneyboxes_data = [
            {
                "name": "Test Box 2.0",
            },
            {
                "name": "Test Box 3.0",
            },
            {
                "name": "Test Box 4.0",
            },
        ]

        for moneybox_data in moneyboxes_data:
            await self.db_manager.add_moneybox(
                moneybox_data=moneybox_data,
            )

    async def dataset_test_distribute_automated_savings_amount__amount_0(self) -> None:
        """The data generation function for test_case:
        `test_distribute_automated_savings_amount__amount_0`.
        """

        await self.truncate_tables()

        # create app settings
        app_settings_data = {
            "send_reports_via_email": False,
            "user_email_address": None,
            "is_automated_saving_active": True,
            "savings_amount": 150,
            "overflow_moneybox_automated_savings_mode": OverflowMoneyboxAutomatedSavingsModeType.COLLECT,
            "is_active": True,
            "note": "",
        }

        async with self.db_manager.async_sessionmaker.begin() as session:
            stmt = insert(AppSettings).values(**app_settings_data)
            await session.execute(stmt)

        moneyboxes_data = [
            {
                "name": "Test Box 1",
                "savings_amount": 5,
                "savings_target": 5,
                "priority": 1,
            },
            {
                "name": "Test Box 2",
                "savings_amount": 10,
                "savings_target": 5,
                "priority": 2,
            },
        ]

        for moneybox_data in moneyboxes_data:
            await self.db_manager.add_moneybox(
                moneybox_data=moneybox_data,
            )

    async def dataset_test_distribute_automated_savings_amount__normal_mode__one_moneybox_with_savings_amount_0(
        self,
    ) -> None:
        """The data generation function for test_case:
        `test_distribute_automated_savings_amount__normal_mode__one_moneybox_with_savings_amount_0`.
        """

        await self.truncate_tables()

        # create app settings
        app_settings_data = {
            "send_reports_via_email": False,
            "user_email_address": None,
            "is_automated_saving_active": True,
            "savings_amount": 150,
            "overflow_moneybox_automated_savings_mode": OverflowMoneyboxAutomatedSavingsModeType.COLLECT,
            "is_active": True,
            "note": "",
        }

        async with self.db_manager.async_sessionmaker.begin() as session:
            stmt = insert(AppSettings).values(**app_settings_data)
            await session.execute(stmt)

        moneyboxes_data = [
            {
                "name": "Test Box 1",
                "savings_amount": 100,
                "savings_target": 5,
                "priority": 1,
            },
            {
                "name": "Test Box 2",
                "savings_amount": 0,
                "savings_target": 5,
                "priority": 2,
            },
            {
                "name": "Test Box 3",
                "savings_amount": 10,
                "savings_target": None,
                "priority": 3,
            },
        ]

        for moneybox_data in moneyboxes_data:
            await self.db_manager.add_moneybox(
                moneybox_data=moneybox_data,
            )

    async def dataset_test_distribute_automated_savings_amount__fill_mode__one_moneybox_with_savings_target_none(
        self,
    ) -> None:
        """The data generation function for test_case:
        `test_distribute_automated_savings_amount__fill_mode__one_moneybox_with_savings_target_none`.
        """

        await self.truncate_tables()

        # create app settings
        app_settings_data = {
            "send_reports_via_email": False,
            "user_email_address": None,
            "is_automated_saving_active": True,
            "savings_amount": 150,
            "overflow_moneybox_automated_savings_mode": OverflowMoneyboxAutomatedSavingsModeType.COLLECT,
            "is_active": True,
            "note": "",
        }

        async with self.db_manager.async_sessionmaker.begin() as session:
            stmt = insert(AppSettings).values(**app_settings_data)
            await session.execute(stmt)

        moneyboxes_data = [
            {
                "name": "Test Box 1",
                "savings_amount": 100,
                "savings_target": 5,
                "priority": 1,
            },
            {
                "name": "Test Box 2",
                "savings_amount": 0,
                "savings_target": 5,
                "priority": 2,
            },
            {
                "name": "Test Box 3",
                "savings_amount": 10,
                "savings_target": None,
                "priority": 3,
            },
        ]

        for moneybox_data in moneyboxes_data:
            await self.db_manager.add_moneybox(
                moneybox_data=moneybox_data,
            )
