import enum

from dragonsight.expression import Expression
from dragonsight.resourceStack import ResourceStack


class When(enum.IntEnum):
    Daily = enum.auto()
    ShortRest = enum.auto()
    LongRest = enum.auto()


class Recharge:

    def __init__(self, when: When, amnt: str) -> None:
        self.when = when
        self.amnt = Expression(amnt)

    def do(self, when: When, res: ResourceStack) -> int:
        """
        Return amount we should recharge
        """
        should = False
        if self.when == When.Daily:
            # Recharge only when a new day
            if when == When.Daily:
                should = True
        elif self.when == When.LongRest:
            # Recharge only on a long rest
            if when == When.LongRest:
                should = True
        # else we recharge on Short/Long
        else:
            should = when != When.Daily

        if should:
            return self.amnt.eval(res)
        else:
            return 0


def parseRecharge(data: dict) -> Recharge:
    amntStr = str(data["amnt"])
    whenStr = str(data["when"])

    match whenStr.lower():
        case "daily":
            rechargeWhen = When.Daily
        case 'short-rest':
            rechargeWhen = When.ShortRest
        case 'long-rest':
            rechargeWhen = When.LongRest
        case _:
            raise RuntimeError(f"Invalid recharge type: '{whenStr}'")

    return Recharge(rechargeWhen, amntStr)
