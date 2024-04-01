from dataclasses import dataclass
from typing import Any
from period_type import PeriodType


@dataclass
class Tarif:
    name: str
    description: str
    owner: str
    periodType: str | PeriodType
    prices: list[dict[str, Any]]
    validFromDate: str
    validToDate: str | None

    def __post_init__(self):
        if isinstance(self.periodType, str):
            self.periodType = PeriodType(self.periodType)

    def price_pr_hour(self) -> list[dict[str, float]]:
        if self.periodType == PeriodType.PT1H:
            return self.prices

        if self.periodType == PeriodType.P1D:
            price = self.prices[0]["price"]
            return [{"position": i, "price": price} for i in range(1, 25)]
