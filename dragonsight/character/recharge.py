import enum

from dragonsight.expression import Expression
from .resourceMap import ResourceMap


class When(enum.IntEnum):
    Daily = enum.auto()
    ShortRest = enum.auto()
    LongRest = enum.auto()

    @classmethod
    def parse(cls, whenStr: str) -> 'When':
        match whenStr.lower():
            case "daily":
                rechargeWhen = When.Daily
            case 'short-rest':
                rechargeWhen = When.ShortRest
            case 'long-rest':
                rechargeWhen = When.LongRest
            case _:
                raise RuntimeError(f"Invalid recharge type: '{whenStr}'")

        return rechargeWhen

    def should(self, when: 'When') -> bool:
        should = False
        if self == When.Daily:
            # Recharge only when a new day
            if when == When.Daily:
                should = True
        elif self == When.LongRest:
            # Recharge only on a long rest
            if when == When.LongRest:
                should = True
        # else we recharge on Short/Long
        else:
            should = when != When.Daily

        return should


class Recharge:

    def __init__(self, when: When, rechargeExpr: str) -> None:
        self._rechargeWhen = when
        if rechargeExpr != "all":
            self._rechargeExpr = Expression(rechargeExpr)
        else:
            self._rechargeExpr = None

    def recharge(self, when: When, res: ResourceMap, key: str, maxVal: int) -> None:
        """
        Recharge some resource specified by key, clipped to maxVal
        """
        if self._rechargeWhen.should(when):
            curVal = res[key]

            # Only none if we should recharge all
            if self._rechargeExpr:
                amnt = self._rechargeExpr.eval(res)
                newVal = curVal + amnt
                if newVal > maxVal:
                    newVal = maxVal
            else:
                newVal = maxVal

            res[key] = newVal
