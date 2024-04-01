from dataclasses import dataclass
from datetime import datetime
from period_type import PeriodType, PeriodTypeException


@dataclass
class Subscription:
    name: str
    description: str
    owner: str
    periodType: str | PeriodType
    price: int | float
    quantity: int
    validFromDate: str
    validToDate: str | None

    def __post_init__(self):
        if isinstance(self.periodType, str):
            self.periodType = PeriodType(self.periodType)

    def price_pr_hour(self):
        if self.periodType == PeriodType.P1M:
            return round((self.price * 12) / 365 / 24, 6)
        if self.periodType == PeriodType.PT15M:
            return self.price * 4
        if self.periodType == PeriodType.PT1H:
            return self.price

        raise PeriodTypeException
