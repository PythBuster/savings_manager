# pylint: disable=too-many-lines

"""The database test data initializer."""

from functools import partial

from sqlalchemy import insert

from src.custom_types import (
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
            "test_get_months_for_reaching_savings_targets__status_200__total_3": self.dataset_test_get_months_for_reaching_savings_targets__status_200__total_3,
            "test_get_months_for_reaching_savings_targets__status_204__no_data": partial(
                self.truncate_tables,
                exclude_table_names=["app_settings"],
                create_overflow_moneybox=True,
            ),
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
            "test_endpoint_update_moneybox__status_422__savings_amount_non_int_type":self.dataset_test_endpoint_update_moneybox__status_422__savings_amount_non_int_type,
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
            "test_task_automated_savings_schedule": self.dataset_test_task_automated_savings_schedule,
            "test_task_automated_savings_dont_schedule": self.dataset_test_task_automated_savings_dont_schedule,
            "test_task_automated_savings_no_email_send": self.dataset_test_task_automated_savings_no_email_send,
            "test_task_automated_savings_no_savings_active": self.dataset_test_task_automated_savings_no_savings_active,
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

    async def dataset_test_get_months_for_reaching_savings_targets__status_200__total_3(
        self,
    ) -> None:
        """The data generation function for test_case:
        `test_get_months_for_reaching_savings_targets__status_200__total_4`.
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
            {  # expectation: reached savings target in 5 months
                "name": "Test Box 3",
                "priority": 1,
                "balance": 0,
                "savings_amount": 2500,
                "savings_target": 10000,
            },
            {  # takes 1000 from month 6 upwards
                "name": "Test Box 2",
                "priority": 2,
                "balance": 0,
                "savings_amount": 1000,
                "savings_target": None,
            },
            {  # get 1000 from month 6 upwards, expectation: reached target in month 16
                "name": "Test Box 4",
                "priority": 3,
                "balance": 1000,
                "savings_amount": 5000,
                "savings_target": 10500,
            },
            {  # expectation: reached target directly (month 0)
                "name": "Test Box 5",
                "priority": 4,
                "balance": 0,
                "savings_amount": 0,
                "savings_target": 0,
            },
            {  # expectation: not part of result, will never reach savings target
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
        `dataset_test_automated_savings_overflow_moneybox_mode_fill_up`.
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
