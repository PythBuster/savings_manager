"""The automated Savings distribution logic is located here."""

import math
from collections import defaultdict
from datetime import datetime, timezone
from functools import partial
from typing import Any, Callable

from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from src.custom_types import (
    ActionType,
    OverflowMoneyboxAutomatedSavingsModeType,
    TransactionTrigger,
    TransactionType,
    MoneyboxSavingsMonthData,
)
from src.db.db_manager import DBManager
from src.db.models import AppSettings

MODE_TO_LOG_DESCRIPTION: dict[OverflowMoneyboxAutomatedSavingsModeType, str] = {
    OverflowMoneyboxAutomatedSavingsModeType.COLLECT: "Automated Savings.",
    OverflowMoneyboxAutomatedSavingsModeType.ADD_TO_AUTOMATED_SAVINGS_AMOUNT: (
        "Automated Savings with Add-Mode."
    ),
    OverflowMoneyboxAutomatedSavingsModeType.FILL_UP_LIMITED_MONEYBOXES: (
        "Fill-Mode: Automated Savings."
    ),
    OverflowMoneyboxAutomatedSavingsModeType.RATIO: "Ratio-Mode: Automated Savings.",
}

POST_DISTRIBUTION_MODES: tuple[OverflowMoneyboxAutomatedSavingsModeType, ...] = (
    OverflowMoneyboxAutomatedSavingsModeType.FILL_UP_LIMITED_MONEYBOXES,
    OverflowMoneyboxAutomatedSavingsModeType.RATIO,
)


class AutomatedSavingsDistributionService:
    """Modes that define how the overflow moneybox balance is distributed
    after automated savings."""

    def __init__(self, db_manager: DBManager):
        self.db_manager = db_manager

    async def run_automated_savings_distribution(self) -> bool:  # pylint:disable=too-many-locals
        """Run the automated savings distribution algorithm.

        App savings amount will be distributed to moneyboxes in priority order (excepted the
        Overflow Moneybox). If there is a leftover that could not be distributed,
        the overflow moneybox will get the leftover.

        :return: True, if savings_distribution is done, false, if automated savings is deactivated.
        :rtype: :class:`bool`

        :raises: :class:`AutomatedSavingsError`: is something went wrong while session
            transactions.
        """

        app_settings: AppSettings = (
            await self.db_manager._get_app_settings()  # pylint: disable=protected-access
        )
        action: OverflowMoneyboxAutomatedSavingsModeType = (
            app_settings.overflow_moneybox_automated_savings_mode
        )
        transaction_description: str = MODE_TO_LOG_DESCRIPTION[action]

        if not app_settings.is_automated_saving_active:
            return False

        moneyboxes: list[dict[str, Any]] = await self.db_manager.get_moneyboxes()
        sorted_moneyboxes: list[dict[str, Any]] = sorted(
            moneyboxes,
            key=lambda item: item["priority"],
        )

        async with self.db_manager.async_sessionmaker.begin() as session:
            # Mode 1: COLLECT and Mode 2: ADD_TO_AUTOMATED_SAVINGS_AMOUNT
            distribution_amount: int = app_settings.savings_amount

            # for MODE 2: ADD
            if (
                action is OverflowMoneyboxAutomatedSavingsModeType.ADD_TO_AUTOMATED_SAVINGS_AMOUNT
                and (overflow_moneybox_amount := sorted_moneyboxes[0]["balance"]) > 0
            ):
                withdraw_transaction_data: dict[str, int | str] = {
                    "amount": overflow_moneybox_amount,
                    "description": transaction_description,
                }
                sorted_moneyboxes[0] = await self.db_manager.sub_amount(
                    moneybox_id=sorted_moneyboxes[0]["id"],
                    withdraw_transaction_data=withdraw_transaction_data,
                    transaction_type=TransactionType.DISTRIBUTION,
                    transaction_trigger=TransactionTrigger.AUTOMATICALLY,
                    session=session,
                )

                # add overflow moneybox balance to savings_distribution amount
                distribution_amount += overflow_moneybox_amount

            # calculate savings_distribution amounts for "normal" savings_distribution case
            distribution_amounts: dict[int, int] = (
                await AutomatedSavingsDistributionService.calculate_moneybox_amounts_normal_distribution(
                    sorted_by_priority_moneyboxes=sorted_moneyboxes,
                    distribute_amount=distribution_amount,
                )
            )

            updated_moneyboxes: list[dict[str, Any]] = (
                await self._distribute_automated_savings_amount(  # type: ignore  # noqa: ignore  # pylint:disable=line-too-long
                    session=session,
                    sorted_by_priority_moneyboxes=sorted_moneyboxes,
                    distribution_amounts=distribution_amounts,
                    distribution_description=transaction_description,
                )
            )

            del sorted_moneyboxes

            # POST-distributions
            # Mode 3: FILL and Mode 4: RATIO
            # -> if overflow moneybox has balance to distribute
            # -> empty overflow moneybox balance and distribute it
            if (
                action in POST_DISTRIBUTION_MODES
                and (overflow_moneybox_amount := updated_moneyboxes[0]["balance"]) > 0
            ):
                withdraw_transaction_data = {
                    "amount": overflow_moneybox_amount,
                    "description": transaction_description,
                }
                updated_moneyboxes[0] = await self.db_manager.sub_amount(
                    moneybox_id=updated_moneyboxes[0]["id"],
                    withdraw_transaction_data=withdraw_transaction_data,
                    transaction_type=TransactionType.DISTRIBUTION,
                    transaction_trigger=TransactionTrigger.AUTOMATICALLY,
                    session=session,
                )

                # calculate savings_distribution amounts for modes 3 and 4
                # FILL:
                if action is OverflowMoneyboxAutomatedSavingsModeType.FILL_UP_LIMITED_MONEYBOXES:
                    distribution_amounts = await AutomatedSavingsDistributionService.calculate_moneybox_amounts_fill_distribution(
                        sorted_by_priority_moneyboxes=updated_moneyboxes,
                        distribute_amount=overflow_moneybox_amount,
                    )
                # RATIO:
                else:
                    distribution_amounts = await AutomatedSavingsDistributionService.calculate_moneybox_amounts_ratio_distribution(
                        sorted_by_priority_moneyboxes=updated_moneyboxes,
                        distribute_amount=overflow_moneybox_amount,
                    )

                _ = await self._distribute_automated_savings_amount(
                    session=session,
                    sorted_by_priority_moneyboxes=updated_moneyboxes,
                    distribution_amounts=distribution_amounts,
                    distribution_description=transaction_description,
                )

            # log automated saving
            automated_savings_log_data: dict[str, Any] = {
                "action": ActionType.APPLIED_AUTOMATED_SAVING,
                "action_at": datetime.now(tz=timezone.utc),
                "details": jsonable_encoder(
                    app_settings.asdict()
                    | {
                        "distribution_amount": distribution_amount,
                    }
                ),
            }

            await self.db_manager.add_action_log(
                session=session,
                automated_savings_log_data=automated_savings_log_data,
            )

        return True

    async def _distribute_automated_savings_amount(  # noqa: ignore  # pylint:disable=too-many-locals, too-many-arguments, too-many-positional-arguments
        self,
        session: AsyncSession,
        sorted_by_priority_moneyboxes: list[dict[str, Any]],
        distribution_amounts: dict[int, int],
        distribution_description: str,
    ) -> list[dict[str, Any]]:
        """A separate helper function to distribute amount to given moneyboxes.

        :param session: Database session.
        :type session: :class:`AsyncSession`
        :param sorted_by_priority_moneyboxes: A list of moneyboxes ASC sorted by priority (the
            overflow moneybox included).
        :type sorted_by_priority_moneyboxes: :class:`list[dict[str, Any]]`
        :param distribution_amounts: The amounts to distribute. A dict of moneybox_id and
            distributing amount.
        :type distribution_amounts: :class:`dict[int, int]`
        :param distribution_description: A description of the amount to distribute
            for the transaction log.
        :type distribution_description: :class:`str`
        :return: Returns an updated moneyboxes list (sorted by priority,
            overflow moneybox included).
        :rtype: :class:`list[dict[str, Any]]`

        :raises: :class:`AutomatedSavingsError`: when something went wrong while
            session transactions.
        """

        updated_moneyboxes: list[dict[str, Any]] = []

        for moneybox in sorted_by_priority_moneyboxes:
            if moneybox["id"] not in distribution_amounts:
                updated_moneyboxes.append(moneybox)
                continue

            amount_to_distribute: int = distribution_amounts[moneybox["id"]]

            if amount_to_distribute > 0:
                deposit_transaction_data: dict[str, str | int] = {
                    "amount": amount_to_distribute,
                    "description": distribution_description,
                }
                updated_moneybox = await self.db_manager.add_amount(
                    session=session,
                    moneybox_id=moneybox["id"],
                    deposit_transaction_data=deposit_transaction_data,
                    transaction_type=TransactionType.DISTRIBUTION,
                    transaction_trigger=TransactionTrigger.AUTOMATICALLY,
                )
                updated_moneyboxes.append(updated_moneybox)
            else:
                updated_moneyboxes.append(moneybox)

        return sorted(updated_moneyboxes, key=lambda mb: mb["priority"])

    @staticmethod
    async def _calculate_distribution_by_mode(
        sorted_by_priority_moneyboxes: list[dict[str, Any]],
        distribute_amount: int,
        calculate_amount_fn: Callable[[dict[str, Any], int], int],
    ) -> dict[int, int]:
        """Internal helper function to calculate moneybox savings_distribution amounts
        based on a strategy function.

        :param sorted_by_priority_moneyboxes: The moneyboxes, sorted by
            priority (overflow moneybox first).
        :type sorted_by_priority_moneyboxes: :class:`list[dict[str, Any]]`
        :param distribute_amount: The amount to distribute.
        :type distribute_amount: :class:`int`
        :param calculate_amount_fn: Function that returns the amount to
            allocate for a given moneybox.
        :type calculate_amount_fn: :class:`Callable[[dict[str, Any], int], int]`
        :return: A dictionary mapping moneybox IDs to their allocated amounts in this
            savings_distribution cycle. Moneyboxes that receive no savings in this cycle are
            not included in the result.
        :rtype: :class:`dict[int, int]`
        """

        if distribute_amount <= 0:
            return {}

        if not sorted_by_priority_moneyboxes:
            raise ValueError("At least one moneybox (overflow) is required.")

        moneybox_amount_distributions: dict[int, int] = {}
        overflow_moneybox: dict[str, Any] = sorted_by_priority_moneyboxes[0]
        normal_moneyboxes: list[dict[str, Any]] = sorted_by_priority_moneyboxes[1:]

        for moneybox in normal_moneyboxes:
            moneybox_savings_amount: int = calculate_amount_fn(moneybox, distribute_amount)

            if moneybox_savings_amount <= 0:
                continue

            moneybox_amount_distributions[moneybox["id"]] = moneybox_savings_amount
            distribute_amount -= moneybox_savings_amount

            if distribute_amount == 0:
                break

        if distribute_amount > 0:
            moneybox_amount_distributions[overflow_moneybox["id"]] = distribute_amount

        return moneybox_amount_distributions

    @staticmethod
    async def calculate_moneybox_amounts_normal_distribution(
        sorted_by_priority_moneyboxes: list[dict[str, Any]],
        distribute_amount: int,
    ) -> dict[int, int]:
        """Helper function to calculate the general savings_distribution moneybox amounts
        in the current savings_distribution cycle using COLLECT or ADD mode.

        :param sorted_by_priority_moneyboxes: The moneyboxes.
        :type sorted_by_priority_moneyboxes: :class:`list[dict[str, Any]]`
        :param distribute_amount: The amount to distribute.
        :type distribute_amount: :class:`int`
        :return: A dictionary mapping moneybox IDs to their allocated amounts in this
            savings_distribution cycle. Moneyboxes that receive no savings in this cycle are
            not included in the result.
        :rtype: :class:`dict[int, int]`
        """

        def normal_mode_fn(moneybox: dict[str, Any], available_amount: int) -> int:
            if moneybox["savings_amount"] <= 0:
                return 0

            if (
                moneybox["savings_target"] is not None
                and moneybox["balance"] >= moneybox["savings_target"]
            ):
                return 0

            max_possible = moneybox["savings_amount"]

            if moneybox["savings_target"] is not None:
                missing_amount = moneybox["savings_target"] - moneybox["balance"]
                max_possible = min(max_possible, missing_amount)

            return min(max_possible, available_amount)

        return await AutomatedSavingsDistributionService._calculate_distribution_by_mode(
            sorted_by_priority_moneyboxes,
            distribute_amount,
            normal_mode_fn,
        )

    @staticmethod
    async def calculate_moneybox_amounts_fill_distribution(
        sorted_by_priority_moneyboxes: list[dict[str, Any]],
        distribute_amount: int,
    ) -> dict[int, int]:
        """Helper function to calculate the moneybox amounts in the current savings_distribution
        cycle using FILL mode.

        :param sorted_by_priority_moneyboxes: The moneyboxes.
        :type sorted_by_priority_moneyboxes: :class:`list[dict[str, Any]]`
        :param distribute_amount: The amount to distribute.
        :type distribute_amount: :class:`int`
        :return: A dictionary mapping moneybox IDs to their allocated amounts in this
            savings_distribution cycle. Only moneyboxes that are not full will be filled up
            until their target. Remaining funds go to the overflow moneybox.
        :rtype: :class:`dict[int, int]`
        """

        def fill_mode_fn(moneybox: dict[str, Any], available_amount: int) -> int:
            if moneybox["savings_target"] is None:
                return 0

            if moneybox["balance"] >= moneybox["savings_target"]:
                return 0

            missing_amount = moneybox["savings_target"] - moneybox["balance"]
            return min(missing_amount, available_amount)

        return await AutomatedSavingsDistributionService._calculate_distribution_by_mode(
            sorted_by_priority_moneyboxes,
            distribute_amount,
            fill_mode_fn,
        )

    @staticmethod
    async def calculate_moneybox_amounts_ratio_distribution(
        sorted_by_priority_moneyboxes: list[dict[str, Any]],
        distribute_amount: int,
    ) -> dict[int, int]:
        """Helper function to calculate the moneybox amounts in the current savings_distribution
        cycle based on the RATIO overflow moneybox mode.

        :param sorted_by_priority_moneyboxes: The moneyboxes.
        :type sorted_by_priority_moneyboxes: :class:`list[dict[str, Any]]`
        :param distribute_amount: The amount to distribute.
        :type distribute_amount: :class:`int`
        :return: A dictionary mapping moneybox IDs to their allocated amounts in
            this savings_distribution cycle using the RATIO strategy. Moneyboxes that receive
            no savings are excluded.
        :rtype: :class:`dict[int, int]`
        """

        overflow_moneybox_id: int = sorted_by_priority_moneyboxes[0]["id"]
        total_savings_amount: int = sum(
            item["savings_amount"] for item in sorted_by_priority_moneyboxes
        )

        if total_savings_amount <= 0:  # at least, only overflow moneybox can get something
            return {overflow_moneybox_id: distribute_amount}

        first_calculation_done: bool = False
        moneybox_distribute_amounts: dict[int, int] = {}

        def ratio_mode_fn(
            reversed_sorted_by_priority_moneyboxes: list[dict[str, Any]],
            moneybox: dict[str, Any],
            _: int,
        ) -> int:
            nonlocal first_calculation_done
            nonlocal moneybox_distribute_amounts

            # calculate the ratio amount for all moneyboxes on first call
            if not first_calculation_done:

                def _ratio_calculation(savings_amount: int) -> int:
                    """Calculates the proportion amount for the moneybox as integer to the
                        total_savings_amount.
                    :param savings_amount: The savings amount of the current moneybox.
                    :type savings_amount: :class:`int`
                    :return: The proportion amount.
                    :rtype: :class:`int`
                    """

                    moneybox_ratio = math.trunc(savings_amount * 100 / total_savings_amount)
                    return math.trunc(distribute_amount / 100 * moneybox_ratio)

                moneybox_distribute_amounts = {
                    moneybox["id"]: _ratio_calculation(savings_amount=moneybox["savings_amount"])
                    for moneybox in reversed_sorted_by_priority_moneyboxes[:-1]
                }
                moneybox_distribute_amounts[overflow_moneybox_id] = distribute_amount
                first_calculation_done = True

            ratio_amount: int = moneybox_distribute_amounts[moneybox["id"]]

            if moneybox["id"] == overflow_moneybox_id or moneybox["savings_target"] is None:
                moneybox_distribute_amounts[overflow_moneybox_id] -= ratio_amount
                return ratio_amount

            real_ratio_amount = min(
                ratio_amount, max(0, moneybox["savings_target"] - moneybox["balance"])
            )
            moneybox_distribute_amounts[overflow_moneybox_id] -= real_ratio_amount
            return real_ratio_amount

        return await AutomatedSavingsDistributionService._calculate_distribution_by_mode(
            sorted_by_priority_moneyboxes,
            distribute_amount,
            partial(ratio_mode_fn, list(reversed(sorted_by_priority_moneyboxes))),
            # for ratio mode, overflow moneybox has to be the latest one, pass reversed list
        )

    @staticmethod
    async def calculate_savings_forecast(
        # noqa: E501  # pylint: disable=line-too-long, too-many-locals, too-many-branches, too-many-statements
        moneyboxes: list[dict[str, Any]],
        app_settings: dict[str, Any],
        overflow_moneybox_mode: OverflowMoneyboxAutomatedSavingsModeType,
    ) -> dict[int, list[MoneyboxSavingsMonthData]]:
        """Calculates a forecast for each moneybox, including the estimated month the savings target
        will be reached and the monthly allocated amounts over the next months.

        :param moneyboxes: The moneyboxes the calculation will be work with.
        :param app_settings: The settings data of the app.
        :param overflow_moneybox_mode: The current overflow moneybox mode.
        :return: The calculated months for reaching savings amount. The Overflow Moneybox
            is not a part of the results.
        :raises: ValueError: if overflow mode is unknown.
        """

        if not moneyboxes or not app_settings["is_automated_saving_active"]:
            return {}

        def _distribute_amount(mb: dict[str, Any], amount: int, month: int) -> None:
            mb["balance"] += amount
            history = moneybox_with_savings_target_distribution_data[mb["id"]]

            if history and history[-1].month == month:
                prev_amount = history[-1].amount or 0
                history[-1] = MoneyboxSavingsMonthData(
                    moneybox_id=mb["id"], month=month, amount=prev_amount + amount
                )
            else:
                history.append(
                    MoneyboxSavingsMonthData(moneybox_id=mb["id"], month=month, amount=amount)
                )

        post_distributions: set[OverflowMoneyboxAutomatedSavingsModeType] = {
            OverflowMoneyboxAutomatedSavingsModeType.FILL_UP_LIMITED_MONEYBOXES,
            OverflowMoneyboxAutomatedSavingsModeType.RATIO,
        }
        moneybox_with_savings_target_distribution_data: dict[
            int, list[MoneyboxSavingsMonthData]
        ] = defaultdict(list)
        moneyboxes_sorted_by_priority = sorted(moneyboxes, key=lambda item: item["priority"])
        overflow_moneybox_id: int = moneyboxes_sorted_by_priority[0]["id"]
        distributed_moneybox_ids: set[int] = set()
        last_total_balances_of_moneyboxes_with_target: int = -1

        def _total_balances_with_targets(_moneyboxes: list[dict[str, Any]]) -> int:
            return sum(mb["balance"] for mb in _moneyboxes if mb["savings_target"] is not None)

        for mb in moneyboxes_sorted_by_priority[1:]:
            if mb["savings_target"] is not None and mb["balance"] >= mb["savings_target"]:
                moneybox_with_savings_target_distribution_data[mb["id"]].append(
                    MoneyboxSavingsMonthData(moneybox_id=mb["id"], amount=None, month=0)
                )
                distributed_moneybox_ids.add(mb["id"])

        simulated_month: int = 1

        while True:
            match overflow_moneybox_mode:
                case OverflowMoneyboxAutomatedSavingsModeType.COLLECT:
                    current_savings_amount: int = app_settings["savings_amount"]
                case OverflowMoneyboxAutomatedSavingsModeType.ADD_TO_AUTOMATED_SAVINGS_AMOUNT:
                    current_savings_amount = (
                        app_settings["savings_amount"] + moneyboxes_sorted_by_priority[0]["balance"]
                    )
                    moneyboxes_sorted_by_priority[0]["balance"] = 0
                case OverflowMoneyboxAutomatedSavingsModeType.FILL_UP_LIMITED_MONEYBOXES:
                    current_savings_amount = app_settings["savings_amount"]
                case OverflowMoneyboxAutomatedSavingsModeType.RATIO:
                    current_savings_amount = app_settings["savings_amount"]
                case _:
                    raise ValueError(
                        f"Unsupported overflow moneybox mode {overflow_moneybox_mode=}"
                    )

            moneybox_distribution_amounts: dict[int, int] = (
                await AutomatedSavingsDistributionService.calculate_moneybox_amounts_normal_distribution(
                    sorted_by_priority_moneyboxes=moneyboxes_sorted_by_priority,
                    distribute_amount=current_savings_amount,
                )
            )

            for mb in moneyboxes_sorted_by_priority:
                dist_amount: int = moneybox_distribution_amounts.get(mb["id"], 0)

                if dist_amount > 0:
                    _distribute_amount(mb, dist_amount, simulated_month)
                    distributed_moneybox_ids.add(mb["id"])

            if overflow_moneybox_mode in post_distributions:
                match overflow_moneybox_mode:
                    case OverflowMoneyboxAutomatedSavingsModeType.FILL_UP_LIMITED_MONEYBOXES:
                        moneybox_distribution_amounts = await AutomatedSavingsDistributionService.calculate_moneybox_amounts_fill_distribution(
                            sorted_by_priority_moneyboxes=moneyboxes_sorted_by_priority,
                            distribute_amount=moneyboxes_sorted_by_priority[0]["balance"],
                        )
                        moneyboxes_sorted_by_priority[0]["balance"] = 0
                    case OverflowMoneyboxAutomatedSavingsModeType.RATIO:
                        moneybox_distribution_amounts = await AutomatedSavingsDistributionService.calculate_moneybox_amounts_ratio_distribution(
                            sorted_by_priority_moneyboxes=moneyboxes_sorted_by_priority,
                            distribute_amount=current_savings_amount,
                        )
                        moneyboxes_sorted_by_priority[0]["balance"] = 0

                # post distribution
                for mb in moneyboxes_sorted_by_priority:
                    dist_amount: int = moneybox_distribution_amounts.get(mb["id"], 0)

                    if dist_amount > 0:
                        _distribute_amount(mb, dist_amount, simulated_month)
                        distributed_moneybox_ids.add(mb["id"])

                if (
                    len(moneybox_distribution_amounts) == 1
                    and overflow_moneybox_id in moneybox_distribution_amounts
                ):
                    break

            if (current_total:=_total_balances_with_targets(moneyboxes_sorted_by_priority[1:])) == last_total_balances_of_moneyboxes_with_target:
                break
            else:
                last_total_balances_of_moneyboxes_with_target = current_total

            simulated_month += 1

        for mb in moneyboxes_sorted_by_priority:
            if (
                    mb["id"] not in distributed_moneybox_ids or  # never got distributed savings
                    mb["savings_target"] is None or  # will never be full
                    mb["balance"] < mb["savings_target"]  # could be full but no more distributions
            ):
                # only add -1 marker if the last entry is not set already with -1
                if not moneybox_with_savings_target_distribution_data[mb["id"]] or (
                        moneybox_with_savings_target_distribution_data[mb["id"]][-1].month != -1
                ):
                    moneybox_with_savings_target_distribution_data[mb["id"]].append(
                        MoneyboxSavingsMonthData(moneybox_id=mb["id"], amount=None, month=-1)
                    )

        if overflow_moneybox_id in moneybox_with_savings_target_distribution_data:
            del moneybox_with_savings_target_distribution_data[overflow_moneybox_id]

        return moneybox_with_savings_target_distribution_data
