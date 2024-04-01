from enum import StrEnum


class PeriodType(StrEnum):
    PT15M = "PT15M"
    PT1H = "PT1H"
    P1D = "P1D"
    P1M = "P1M"
    ANDET = "ANDET"


class PeriodTypeException(Exception):
    pass
