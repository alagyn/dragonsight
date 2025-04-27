import enum

from ..resourceStack import ResourceStack
from .recharge import Recharge, When, parseRecharge


class ResourceMaxType(enum.IntEnum):
    Constant = enum.auto()
    Level = enum.auto()
    Expr = enum.auto()


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

    def __init__(self, name: str, rID: str, rMax: _ResourceMax, recharge: Recharge) -> None:
        self.name = name
        self.rID = rID
        self.rMax = rMax
        self.curValue = 0
        self._recharge = recharge

    def recharge(self, when: When, res: ResourceStack):
        self.curValue += self._recharge.do(when, res)
        rMax = self.rMax.getMax(res)
        if self.curValue > rMax:
            self.curValue = rMax


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
    recharge = parseRecharge(rechargeData)

    # TODO
    return Resource(name, rID, rMax, recharge)
