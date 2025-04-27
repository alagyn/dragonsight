import enum
from resourceStack import ResourceStack


class ResourceMaxType(enum.IntEnum):
    Constant = enum.auto()
    Level = enum.auto()
    Expr = enum.auto()


class Recharge(enum.IntEnum):
    Daily = enum.auto()
    ShortRest = enum.auto()
    LongRest = enum.auto()


class _ResourceMax:

    def __init__(self, maxType: ResourceMaxType) -> None:
        self.maxType = maxType

    def getMax(self, res: ResourceStack) -> int:
        raise NotImplementedError()


class _ResourceMaxConstant(_ResourceMax):

    def __init__(self, maxVal: int) -> None:
        super().__init__(ResourceMaxType.Constant)
        self.maxVal = maxVal

    def getMax(self, res: ResourceStack) -> int:
        return self.maxVal


class _ResourceMaxLevel(_ResourceMax):

    def __init__(self, values: list[int]) -> None:
        super().__init__(ResourceMaxType.Level)
        self.values = values

    def getMax(self, res: ResourceStack) -> int:
        return self.values[res["sorcerer_level"]]


class _ResourceMaxExpr(_ResourceMax):

    def __init__(self, maxExpr: str) -> None:
        super().__init__(ResourceMaxType.Expr)
        self.maxExpr = maxExpr

    def getMax(self, res: ResourceStack) -> int:
        # TODO for now, just assume the value is a key in the resources
        return res[self.maxExpr]


class Resource:

    def __init__(
        self,
        name: str,
        rID: str,
        rMax: _ResourceMax,
        rechargeWhen: Recharge,
        rechargeAmntStr: str,
    ) -> None:
        self.name = name
        self.rID = rID
        self.rMax = rMax
        self.rechargeWhen = rechargeWhen
        self.rechargeAmntStr = rechargeAmntStr

    def recharge(self, when: Recharge):
        if self.rechargeWhen == Recharge.Daily:
            # Recharge only when a new day
            if when == Recharge.Daily:
                self._recharge()
        elif self.rechargeWhen == Recharge.LongRest:
            # Recharge only on a long rest
            if when == Recharge.LongRest:
                self._recharge()
        # else we recharge on Short/Long
        elif when != Recharge.Daily:
            self._recharge()

    def _recharge(self):
        # TODO
        pass


def parseResource(data: dict) -> Resource:
    name = str(data["name"])
    rID = str(data["id"])

    # Max
    maxData = data["max"]
    maxTypeStr = str(maxData["type"])
    maxValue = maxData["value"]

    match maxTypeStr.lower():
        case 'level':
            if not isinstance(maxValue, list):
                raise RuntimeError()
            rMax = _ResourceMaxLevel(maxValue)
        case 'constant':
            if not isinstance(maxValue, int):
                raise RuntimeError()
            rMax = _ResourceMaxConstant(maxValue)
        case 'expr':
            if not isinstance(maxValue, str):
                raise RuntimeError()
            rMax = _ResourceMaxExpr(maxValue)
        case _:
            raise RuntimeError(f"Invalid resource max type: '{maxTypeStr}'")

    # Recharge
    rechargeData = data["recharge"]
    rechargeAmntStr = str(rechargeData["amnt"])
    rechargeWhenStr = str(rechargeData["when"])

    match rechargeWhenStr.lower():
        case "daily":
            rechargeWhen = Recharge.Daily
        case 'short-rest':
            rechargeWhen = Recharge.ShortRest
        case 'long-rest':
            rechargeWhen = Recharge.LongRest
        case _:
            raise RuntimeError(f"Invalid recharge type: '{rechargeWhenStr}'")

    return Resource(name, rID, rMax, rechargeWhen, rechargeAmntStr)
