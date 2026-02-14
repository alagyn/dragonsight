import enum

from dragonsight.dice import DiceRoll

import imgui as im


class When(enum.IntEnum):
    Never = enum.auto()
    ShortRest = enum.auto()
    LongRest = enum.auto()
    Daily = enum.auto()

    def toStr(self) -> str:
        match self:
            case When.Never:
                return "Never"
            case When.ShortRest:
                return "Short Rest"
            case When.LongRest:
                return "Long Rest"
            case When.Daily:
                return "Daily"
            case _:
                raise RuntimeError("Invalid RechargeWhen")

    def check(self, o: 'When') -> bool:
        if self == When.Never:
            return False
        # Long rest also recharges short rest things
        if self == When.ShortRest and o in [When.ShortRest, When.LongRest]:
            return True
        return self == o


class RechargeAmount(enum.IntEnum):
    # Can be achieved with a dice roll with no dice
    # Fixed = enum.auto()
    Roll = enum.auto()
    All = enum.auto()


class Resource:

    def __init__(
        self,
        name: str,
        desc: str,
        maxVal: int,
        value: int,
        when: When,
        rechargeAmount: RechargeAmount,
        rollStr: str | None,
    ) -> None:
        self.name = name
        self.desc = im.StrRef(desc, 256)
        self.value = value
        self.maxVal = maxVal
        self.rechargeWhen: When = when
        self.rechargeAmount: RechargeAmount = rechargeAmount
        self.rechargeRoll: DiceRoll | None = None
        if rollStr is not None:
            self.rechargeRoll = DiceRoll(rollStr)

    def clamp(self):
        self.value = max(0, self.value)
        if self.maxVal > 0:
            self.value = min(self.value, self.maxVal)

    def setRoll(self, rollStr: str):
        self.rechargeRoll = DiceRoll(rollStr)

    def recharge(self, when: When) -> int:
        if not self.rechargeWhen.check(when):
            return 0

        out = 0

        if self.rechargeAmount == RechargeAmount.All:
            out = self.maxVal - self.value
            self.value = self.maxVal
        elif self.rechargeRoll is not None:
            out = self.rechargeRoll.roll()
            self.value = min(self.maxVal, self.value + out)
        else:
            print("Warning, invalid recharge state")

        return out
