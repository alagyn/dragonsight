import enum

from .recharge import When, Recharge
from .resourceMap import ResourceMap
from dragonsight.expression import Expression


class ResourceMaxType(enum.IntEnum):
    Constant = enum.auto()
    Level = enum.auto()
    Expr = enum.auto()


class _ResourceMax:

    def __init__(self, maxType: ResourceMaxType) -> None:
        self.maxType = maxType

    def getMax(self, res: ResourceMap) -> int:
        raise NotImplementedError()


class _ResourceMaxConstant(_ResourceMax):

    def __init__(self, maxVal: int) -> None:
        super().__init__(ResourceMaxType.Constant)
        self.maxVal = maxVal

    def getMax(self, res: ResourceMap) -> int:
        return self.maxVal


class _ResourceMaxLevel(_ResourceMax):

    def __init__(self, values: list[int], namespace: str) -> None:
        super().__init__(ResourceMaxType.Level)
        self._values = values
        self._key = f'{namespace}.level'

    def getMax(self, res: ResourceMap) -> int:
        curLevel = res[self._key]
        return self._values[curLevel]


class _ResourceMaxExpr(_ResourceMax):

    def __init__(self, maxExpr: str) -> None:
        super().__init__(ResourceMaxType.Expr)
        self._maxExpr = Expression(maxExpr)

    def getMax(self, res: ResourceMap) -> int:
        return self._maxExpr.eval(res)


class Resource:

    def __init__(self, name: str, rID: str, rMax: _ResourceMax, recharge: Recharge) -> None:
        self.name = name
        self.rID = rID
        self.rMax = rMax
        self._recharge = recharge

    def recharge(self, when: When, res: ResourceMap):
        rMax = self.rMax.getMax(res)
        self._recharge.recharge(when, res, self.rID, rMax)


def parseResource(data: dict, namespace: list[str], res: ResourceMap) -> Resource:
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
            rMax = _ResourceMaxLevel(maxValue, ".".join(namespace))
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
    amntStr = str(rechargeData["amnt"])
    whenStr = str(rechargeData["when"])
    rechargeWhen = When.parse(whenStr)

    return Resource(name, rID, rMax, Recharge(rechargeWhen, amntStr))
