"""The start module of the savings manager app."""

import asyncio

from src.custom_types import EnvironmentTypes
from src.db.db_manager import DBManager
from src.utils import get_db_settings


async def main() -> None:
    """The entry point of the app."""

    moneybox_data = {"name": "test 12312123123"}

    db_manager = DBManager(
        db_settings=get_db_settings(),
    )
    await db_manager.add_moneybox(moneybox_data=moneybox_data)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--environment",
        required=True,
        help="Loads environment variables depending on this flag",
        type=EnvironmentTypes,
    )
    args = parser.parse_args()

    if args.environment == EnvironmentTypes.DEV:
        from pathlib import Path

        from dotenv import load_dotenv

        dotenv_path = Path(__file__).resolve().parent.parent / "envs" / ".env"
        print(dotenv_path)
        load_dotenv(dotenv_path=dotenv_path)
        print(f"Loaded {dotenv_path}")

    asyncio.run(main())
