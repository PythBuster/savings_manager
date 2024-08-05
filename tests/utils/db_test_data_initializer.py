"""The database test data initializer."""
import time

from src.custom_types import TransactionTrigger, TransactionType
from src.db.db_manager import DBManager


class DBTestDataInitializer:
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

        self.test_case = test_case
        """Current function name of test case."""

        self.TEST_CASES_DATA = {
            "test_endpoint_get_moneyboxes__status_200__total_5": self.dataset_test_endpoint_get_moneyboxes__status_200__total_5,
            "test_endpoint_get_moneyboxes__status_204__no_content": self.truncate_tables,  # no data needed
            "test_endpoint_get_moneybox__moneybox_id_1__status_200_existing": self.dataset_test_endpoint_get_moneybox__moneybox_id_1__status_200_existing,
            "test_endpoint_get_moneybox_status_404_non_existing": self.truncate_tables,  # no data needed,
            "test_endpoint_get_moneybox__moneybox_id_2__status_200_existing__with_balance_100": self.dataset_test_endpoint_get_moneybox__moneybox_id_2__status_200_existing__with_balance_100,
            "test_endpoint_add_moneybox__one__status_200": self.truncate_tables,  # no data needed,
            "test_endpoint_add_moneybox__two__status_200": self.truncate_tables,  # no data needed,
            "test_endpoint_add_moneybox__one__status_422__balance_postdata": self.truncate_tables,  # no data needed,
            "test_endpoint_update_moneybox__moneybox_id_1__namechange": self.dataset_endpoint_update_moneybox__moneybox_id_1__namechange,
            "test_endpoint_update_moneybox__moneybox_id_1__status_422__fail_extra_fields": self.dataset_test_endpoint_update_moneybox__moneybox_id_1__status_422__fail_extra_fields,
            "test_endpoint_moneybox_id_1__modified_at_checks": self.dataset_test_endpoint_moneybox_id_1__modified_at_checks,
            "test_endpoint_delete_moneybox_1__status_204": self.dataset_test_endpoint_delete_moneybox_1__status_204,
            "test_endpoint_delete_moneybox_1__non_existing__status_404": self.truncate_tables,  # no data needed,
            "test_endpoint_delete_moneybox_1__non_existing_after_success_deletion__status_204_and_404": self.dataset_test_endpoint_delete_moneybox_1__non_existing_after_success_deletion__status_204_and_404,
            "test_endpoint_deposit_moneybox_1__status_200": self.dataset_test_endpoint_deposit_moneybox_1__status_200,
            "test_endpoint_withdraw_moneybox_1__status_200": self.dataset_test_endpoint_withdraw_moneybox_1__status_200,
            "test_endpoint_withdraw_moneybox_1__status_405__balance_negative": self.dataset_test_endpoint_withdraw_moneybox_1__status_405__balance_negative,
            "test_endpoint_transfer_amount_moneybox_1_to_moneybox_2__status_204": self.dataset_test_endpoint_transfer_amount_moneybox_1_to_moneybox_2__status_204,
            "test_endpoint_transfer_amount_moneybox_1_to_moneybox_2__status_204__missing_description_field": self.dataset_test_endpoint_transfer_amount_moneybox_1_to_moneybox_2__status_204__missing_description_field,
            "test_endpoint_transfer_amount_moneybox_1_to_moneybox_2__status_404__to_moneybox_id_2_not_found": self.dataset_test_endpoint_transfer_amount_moneybox_1_to_moneybox_2__status_404__to_moneybox_id_2_not_found,
        }
        """Map test case name witch related test data generation function"""

    async def run(
        self,
    ) -> None:
        """Call data generator function depending on test case name map."""

        await self.TEST_CASES_DATA[self.test_case]()  # type: ignore

        # sleep to get higher modified_at datetime (simulate time passing before modifying data)
        time.sleep(1)

    async def truncate_tables(self) -> None:
        """Truncate tables."""

        print(
            f"Truncate tables ({self.test_case})",
            flush=True,
        )
        await self.db_manager.truncate_tables()  # type: ignore

    async def dataset_test_endpoint_get_moneyboxes__status_200__total_5(self) -> None:
        """The data generation function for test_case:
        `test_endpoint_get_moneyboxes__status_200__total_5`.
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

    async def dataset_test_endpoint_get_moneybox__moneybox_id_1__status_200_existing(self) -> None:
        """The data generation function for test_case:
        `test_endpoint_get_moneybox__moneybox_id_1__status_200_existing`.
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

    async def dataset_test_endpoint_get_moneybox__moneybox_id_2__status_200_existing__with_balance_100(
        self,
    ) -> None:
        """The data generation function for test_case:
        `test_endpoint_get_moneybox__moneybox_id_2__status_200_existing__with_balance_100`.
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

        # sleep to get higher modified_at datetime (simulate time passing before modifying data)
        time.sleep(1)

        # add some amount to moneybox with id 2
        await self.db_manager.add_amount(
            moneybox_id=2,
            deposit_transaction_data={
                "amount": 100,
                "description": "Unit Test.",
            },
            transaction_type=TransactionType.DIRECT,
            transaction_trigger=TransactionTrigger.MANUALLY,
        )

    async def dataset_endpoint_update_moneybox__moneybox_id_1__namechange(self) -> None:
        """The data generation function for test_case:
        `test_endpoint_update_moneybox__moneybox_id_1__namechange`.
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

    async def dataset_test_endpoint_update_moneybox__moneybox_id_1__status_422__fail_extra_fields(
        self,
    ) -> None:
        """The data generation function for test_case:
        `test_endpoint_update_moneybox__moneybox_id_1__status_422__fail_extra_fields`.
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

    async def dataset_test_endpoint_moneybox_id_1__modified_at_checks(self) -> None:
        """The data generation function for test_case:
        `test_endpoint_moneybox_id_1__modified_at_checks`.
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

    async def dataset_test_endpoint_delete_moneybox_1__status_204(self) -> None:
        """The data generation function for test_case:
        `test_endpoint_delete_moneybox_1__status_204`.
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

    async def dataset_test_endpoint_delete_moneybox_1__non_existing_after_success_deletion__status_204_and_404(
        self,
    ) -> None:
        """The data generation function for test_case:
        `test_endpoint_delete_moneybox_1__non_existing_after_success_deletion__status_200_and_404`.
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

    async def dataset_test_endpoint_deposit_moneybox_1__status_200(
        self,
    ) -> None:
        """The data generation function for test_case:
        `test_endpoint_deposit_moneybox_1__status_200`.
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

    async def dataset_test_endpoint_withdraw_moneybox_1__status_200(
        self,
    ) -> None:
        """The data generation function for test_case:
        `test_endpoint_withdraw_moneybox_1__status_200`.
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

        # sleep to get higher modified_at datetime (simulate time passing before modifying data)
        time.sleep(1)

        # add some amount to moneybox 1
        deposit_transaction_data = {
            "amount": 100,
            "description": "Bonus.",
        }

        await self.db_manager.add_amount(
            moneybox_id=1,
            deposit_transaction_data=deposit_transaction_data,
            transaction_type=TransactionType.DIRECT,
            transaction_trigger=TransactionTrigger.MANUALLY,
        )

    async def dataset_test_endpoint_withdraw_moneybox_1__status_405__balance_negative(
        self,
    ) -> None:
        """The data generation function for test_case:
        `test_endpoint_withdraw_moneybox_1__status_405__balance_negative`.
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

    async def dataset_test_endpoint_transfer_amount_moneybox_1_to_moneybox_2__status_204(
        self,
    ) -> None:
        """The data generation function for test_case:
        `test_endpoint_transfer_amount_moneybox_1_to_moneybox_2__status_204`.
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

        # sleep to get higher modified_at datetime (simulate time passing before modifying data)
        time.sleep(1)

        # add some amount to moneybox with id 2
        await self.db_manager.add_amount(
            moneybox_id=1,
            deposit_transaction_data={
                "amount": 1000,
                "description": "Unit Test.",
            },
            transaction_type=TransactionType.DIRECT,
            transaction_trigger=TransactionTrigger.MANUALLY,
        )

    async def dataset_test_endpoint_transfer_amount_moneybox_1_to_moneybox_2__status_204__missing_description_field(
        self,
    ) -> None:
        """The data generation function for test_case:
        `test_endpoint_transfer_amount_moneybox_1_to_moneybox_2__status_204__missing_description_field`.
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

        # sleep to get higher modified_at datetime (simulate time passing before modifying data)
        time.sleep(1)

        # add some amount to moneybox with id 2
        await self.db_manager.add_amount(
            moneybox_id=1,
            deposit_transaction_data={
                "amount": 1000,
                "description": "Unit Test.",
            },
            transaction_type=TransactionType.DIRECT,
            transaction_trigger=TransactionTrigger.MANUALLY,
        )

    async def dataset_test_endpoint_transfer_amount_moneybox_1_to_moneybox_2__status_404__to_moneybox_id_2_not_found(
        self,
    ) -> None:
        """The data generation function for test_case:
        `test_endpoint_transfer_amount_moneybox_1_to_moneybox_2__status_404__to_moneybox_id_2_not_found`.
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
