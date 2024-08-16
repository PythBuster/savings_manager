"""The database test data initializer."""

import time
from functools import partial

from src.custom_types import TransactionTrigger, TransactionType
from src.db.db_manager import DBManager


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
            "test_endpoint_get_moneyboxes__status_200__total_6": self.dataset_test_endpoint_get_moneyboxes__status_200__total_6,
            "test_endpoint_get_moneyboxes__status_204__no_content": self.truncate_tables,  # no data needed
            "test_endpoint_get_moneybox__second_moneybox__status_200_existing": self.dataset_test_endpoint_get_moneybox__second_moneybox__status_200_existing,
            "test_endpoint_get_moneybox_status_404_non_existing": self.truncate_tables,  # no data needed,
            "test_endpoint_get_moneybox__second_moneybox__status_200_existing__with_balance_100": self.dataset_test_endpoint_get_moneybox__second_moneybox__status_200_existing__with_balance_100,
            "test_endpoint_add_moneybox__invalid_with_priority_0": self.truncate_tables,
            "test_endpoint_add_moneybox__one__status_200": self.truncate_tables,  # no data needed,
            "test_endpoint_add_moneybox__two__status_200": self.truncate_tables,  # no data needed,
            "test_endpoint_add_moneybox__one__status_422__balance_postdata": self.truncate_tables,  # no data needed,
            "test_endpoint_delete_overflow_moneybox__status_405": self.dataset_test_endpoint_delete_overflow_moneybox__status_405,
            "test_endpoint_update_overflow_moneybox": self.dataset_test_endpoint_update_overflow_moneybox,
            "test_endpoint_update_moneybox__invalid_priority_0": self.dataset_test_endpoint_update_moneybox__invalid_priority_0,
            "test_endpoint_update_moneybox__last_moneybox__namechange": self.dataset_test_endpoint_update_moneybox__last_moneybox__namechange,
            "test_endpoint_update_moneybox__first_moneybox__status_422__fail_extra_fields": self.dataset_test_endpoint_update_moneybox__first_moneybox__status_422__fail_extra_fields,
            "test_endpoint_first_moneybox__modified_at_checks": self.dataset_test_endpoint_first_moneybox__modified_at_checks,
            "test_endpoint_delete_second_moneybox__status_204": self.dataset_test_endpoint_delete_second_moneybox__status_204,
            "test_endpoint_deposit_first_moneybox__status_200": self.dataset_test_endpoint_deposit_first_moneybox__status_200,
            "test_endpoint_withdraw_first_moneybox__status_200": self.dataset_test_endpoint_withdraw_first_moneybox__status_200,
            "test_endpoint_withdraw_first_moneybox__status_405__balance_negative": self.dataset_test_endpoint_withdraw_first_moneybox__status_405__balance_negative,
            "test_endpoint_transfer_amount_moneybox_second_to_third__status_204": self.dataset_test_endpoint_transfer_amount_moneybox_second_to_third__status_204,
            "test_endpoint_transfer_amount_moneybox_second_to_third__status_204__missing_description_field": self.dataset_test_endpoint_transfer_amount_moneybox_second_to_third__status_204__missing_description_field,
            "test_endpoint_transfer_amount_moneybox_second_to_third__status_404__to_moneybox_third_not_found": self.dataset_test_endpoint_transfer_amount_moneybox_second_to_third__status_404__to_moneybox_third_not_found,
            "test_get_priority_list": self.dataset_test_get_priority_list,
            "test_update_priority_list": self.dataset_test_update_priority_list,
            "test_create_instance": self.truncate_tables,
            "test_add_moneybox": self.truncate_tables,
            "test_get_app_settings_status_200": partial(
                self.truncate_tables, exclude_table_names=["app_settings"]
            ),
        }
        """Map test case name witch related test data generation function"""

    async def run(
        self,
    ) -> None:
        """Call data generator function depending on test case name map."""

        await self.TEST_CASES_DATA[self.test_case]()  # type: ignore

        # sleep to get higher modified_at datetime (simulate time passing before modifying data)
        time.sleep(1)

    async def truncate_tables(self, exclude_table_names: list[str] | None = None) -> None:
        """Truncate tables."""

        print(
            f"Truncate tables ({self.test_case})",
            flush=True,
        )
        await self.db_manager.truncate_tables(exclude_table_names=exclude_table_names)  # type: ignore

        # re-add overflow moneybox after emptying database
        overflow_moneybox_data = {
            "name": "1bd2a9ee-26a1-4630-a068-19865cf2ca62",
            "savings_amount": 0,
            "savings_target": None,
            "priority": 0,
        }

        await self.db_manager.add_moneybox(
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
            {"name": "Test Box 1", "savings_amount": 0, "savings_target": None, "priority": 1},
            {"name": "Test Box 2", "savings_amount": 0, "savings_target": None, "priority": 2},
            {"name": "Test Box 3", "savings_amount": 0, "savings_target": None, "priority": 3},
            {"name": "Test Box 4", "savings_amount": 0, "savings_target": None, "priority": 4},
            {"name": "Test Box 5", "savings_amount": 0, "savings_target": None, "priority": 5},
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
            {"name": "Test Box 1", "savings_amount": 0, "savings_target": None, "priority": 1},
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
            {"name": "Test Box 1", "savings_amount": 0, "savings_target": None, "priority": 1},
            {"name": "Test Box 2", "savings_amount": 0, "savings_target": None, "priority": 2},
        ]

        added_moneyboxes = []
        for moneybox_data in moneyboxes_data:
            moneybox = await self.db_manager.add_moneybox(
                moneybox_data=moneybox_data,
            )
            added_moneyboxes.append(moneybox)

        # sleep to get higher modified_at datetime (simulate time passing before modifying data)
        time.sleep(1)

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

    async def dataset_test_endpoint_update_moneybox__invalid_priority_0(self) -> None:
        """The data generation function for test_case:
        `test_endpoint_update_moneybox__invalid_priority_0`.
        """

        await self.truncate_tables()

        print(
            f"Create data for test ({self.test_case})",
            flush=True,
        )

        # create 1 moneybox
        moneyboxes_data = [
            {"name": "Test Box 1", "savings_amount": 0, "savings_target": None, "priority": 1},
        ]

        for moneybox_data in moneyboxes_data:
            await self.db_manager.add_moneybox(
                moneybox_data=moneybox_data,
            )

    async def dataset_test_endpoint_update_moneybox__last_moneybox__namechange(self) -> None:
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
            {"name": "Test Box 1", "savings_amount": 0, "savings_target": None, "priority": 1},
            {"name": "Test Box 2", "savings_amount": 0, "savings_target": None, "priority": 2},
            {"name": "Test Box 3", "savings_amount": 0, "savings_target": None, "priority": 3},
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

    async def dataset_test_endpoint_update_overflow_moneybox(self) -> None:
        """The data generation function for test_case:
        `test_endpoint_update_overflow_moneybox`.
        """

        await self.truncate_tables()

        print(
            f"Create data for test ({self.test_case})",
            flush=True,
        )

        # create 3 moneyboxes
        moneyboxes_data = [
            {"name": "Test Box 1", "savings_amount": 0, "savings_target": None, "priority": 1},
            {"name": "Test Box 2", "savings_amount": 0, "savings_target": None, "priority": 2},
            {"name": "Test Box 3", "savings_amount": 0, "savings_target": None, "priority": 3},
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
            {"name": "Test Box 1", "savings_amount": 0, "savings_target": None, "priority": 1},
            {"name": "Test Box 2", "savings_amount": 0, "savings_target": None, "priority": 2},
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
            {"name": "Test Box 1", "savings_amount": 0, "savings_target": None, "priority": 1},
            {"name": "Test Box 2", "savings_amount": 0, "savings_target": None, "priority": 2},
        ]

        for moneybox_data in moneyboxes_data:
            await self.db_manager.add_moneybox(
                moneybox_data=moneybox_data,
            )

    async def dataset_test_endpoint_delete_moneybox_2__non_existing_after_success_deletion__status_204_and_404(
        self,
    ) -> None:
        """The data generation function for test_case:
        `test_endpoint_delete_moneybox_2__non_existing_after_success_deletion__status_200_and_404`.
        """

        await self.truncate_tables()

        # create 1 moneybox
        moneyboxes_data = [
            {"name": "Test Box 1", "priority": 1},
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
            {"name": "Test Box 1", "savings_amount": 0, "savings_target": None, "priority": 1},
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

        # sleep to get higher modified_at datetime (simulate time passing before modifying data)
        time.sleep(1)

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

    async def dataset_test_endpoint_withdraw_first_moneybox__status_405__balance_negative(
        self,
    ) -> None:
        """The data generation function for test_case:
        `test_endpoint_withdraw_first_moneybox__status_405__balance_negative`.
        """

        await self.truncate_tables()

        # create 1 moneybox
        moneyboxes_data = [
            {"name": "Test Box 1", "savings_amount": 0, "savings_target": None, "priority": 1},
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
            {"name": "Test Box 1", "savings_amount": 0, "savings_target": None, "priority": 1},
            {"name": "Test Box 2", "savings_amount": 0, "savings_target": None, "priority": 2},
            {"name": "Test Box 3", "savings_amount": 0, "savings_target": None, "priority": 3},
        ]

        moneyboxes = []
        for moneybox_data in moneyboxes_data:
            moneybox = await self.db_manager.add_moneybox(
                moneybox_data=moneybox_data,
            )
            moneyboxes.append(moneybox)

        # sleep to get higher modified_at datetime (simulate time passing before modifying data)
        time.sleep(1)

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
            {"name": "Test Box 1", "savings_amount": 0, "savings_target": None, "priority": 1},
            {"name": "Test Box 2", "savings_amount": 0, "savings_target": None, "priority": 2},
            {"name": "Test Box 3", "savings_amount": 0, "savings_target": None, "priority": 3},
        ]

        moneyboxes = []
        for moneybox_data in moneyboxes_data:
            moneybox = await self.db_manager.add_moneybox(
                moneybox_data=moneybox_data,
            )
            moneyboxes.append(moneybox)

        # sleep to get higher modified_at datetime (simulate time passing before modifying data)
        time.sleep(1)

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
            {"name": "Test Box 1", "savings_amount": 0, "savings_target": None, "priority": 1},
            {"name": "Test Box 2", "savings_amount": 0, "savings_target": None, "priority": 2},
        ]

        for moneybox_data in moneyboxes_data:
            await self.db_manager.add_moneybox(
                moneybox_data=moneybox_data,
            )

    async def dataset_test_get_priority_list(
        self,
    ) -> None:
        """The data generation function for test_case:
        `test_get_priority_list`.
        """

        await self.truncate_tables()

        # create 2 moneyboxes
        moneyboxes_data = [
            {"name": "Test Box 1", "savings_amount": 0, "savings_target": None, "priority": 1},
            {"name": "Test Box 2", "savings_amount": 0, "savings_target": None, "priority": 2},
        ]

        for moneybox_data in moneyboxes_data:
            await self.db_manager.add_moneybox(
                moneybox_data=moneybox_data,
            )

    async def dataset_test_update_priority_list(
        self,
    ) -> None:
        """The data generation function for test_case:
        `test_update_priority_list`.
        """

        await self.truncate_tables()

        # create 2 moneyboxes
        moneyboxes_data = [
            {"name": "Test Box 1", "savings_amount": 0, "savings_target": None, "priority": 1},
            {"name": "Test Box 2", "savings_amount": 0, "savings_target": None, "priority": 2},
        ]

        for moneybox_data in moneyboxes_data:
            await self.db_manager.add_moneybox(
                moneybox_data=moneybox_data,
            )
