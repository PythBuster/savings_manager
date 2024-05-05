"""The database test data initializer."""

from src.db.db_manager import DBManager


class DBTestDataInitializer:
    """The database test data initializer class."""

    def __init__(self, db_manager: DBManager) -> None:
        self.db_manager = db_manager
        """Current database connection and session maker hold in db_manager."""

        self.TEST_CASES_DATA = {
            "test_endpoint_get_moneyboxes_exist_5": self.dataset_test_endpoint_get_moneyboxes_exist_5,
        }
        """Map test case ame witch related test data generation function"""

    async def run(
        self,
        test_case: str,
    ) -> None:
        """Call data generator function depending on test case name map.

        :param test_case: Name of the test case function.
        :type test_case: str
        """

        await self.TEST_CASES_DATA[test_case]()

    async def dataset_test_endpoint_get_moneyboxes_exist_5(self) -> None:
        """The data generation function for test_case:
        `test_endpoint_get_moneyboxes_exist_5`.
        """

        print(
            "Truncate tables and create data for 'test_endpoint_get_moneyboxes_exist_5'",
            flush=True,
        )

        await self.db_manager.truncate_tables()  # type: ignore

        moneyboxes_data = [
            {"name": "Test Box 1"},
            {"name": "Test Box 2"},
            {"name": "Test Box 3"},
            {"name": "Test Box 4"},
            {"name": "Test Box 5"},
        ]

        for moneybox_data in moneyboxes_data:
            await self.db_manager.add_moneybox(
                moneybox_data=moneybox_data,
            )
