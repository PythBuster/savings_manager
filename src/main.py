"""The start module of the savings manager app."""

import asyncio

from src.custom_types import EnvironmentTypes


async def main() -> None:
    """The entry point of the app."""


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
        load_dotenv(dotenv_path=dotenv_path)
        print(f"Loaded {dotenv_path}")

    asyncio.run(main())
