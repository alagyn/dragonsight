import enum

from .recharge import When, Recharge
from .resourceMap import ResourceMap


class ActionType(enum.IntEnum):
    # Single use before recharge
    Single = enum.auto()
    # Has a limited number of use before recharge
    Charges = enum.auto()
    # Consumes a resource
    Resource = enum.auto()


class Action:

    def __init__(self, name: str, desc: str | None, aType: ActionType) -> None:
        self.name = name
        self.desc = desc
        self.aType = aType

    def available(self, res: ResourceMap) -> bool:
        raise NotImplementedError()

    def recharge(self, when: When, res: ResourceMap):
        pass

    def use(self, res: ResourceMap):
        raise NotImplementedError()


class Action_Single(Action):

    def __init__(
        self,
        name: str,
        desc: str | None,
        rechargeWhen: When,
        namespace: str,
        res: ResourceMap
    ) -> None:
        super().__init__(name, desc, ActionType.Single)
        self._key = f'{namespace}.charge'
        if self._key not in res:
            res[self._key] = 1
        self._when = rechargeWhen

    def available(self, res: ResourceMap) -> bool:
        return res[self._key] > 0

    def recharge(self, when: When, res: ResourceMap):
        if self._when.should(when):
            res[self._key] = 1

    def use(self, res: ResourceMap):
        res[self._key] = 0


class Action_Charges(Action):
    # TODO might need to support max charges being an expr

    def __init__(
        self,
        name: str,
        desc: str | None,
        numCharges: int,
        recharge: Recharge,
        namespace: str,
        res: ResourceMap
    ) -> None:
        super().__init__(name, desc, ActionType.Charges)
        self._key = f'{namespace}.charges'
        self._recharge = recharge
        self.numCharges = numCharges
        if self._key not in res:
            res[self._key] = numCharges

    def available(self, res: ResourceMap) -> bool:
        return res[self._key] > 0

    def recharge(self, when: When, res: ResourceMap):
        self._recharge.recharge(when, res, self._key, self.numCharges)

    def use(self, res: ResourceMap):
        res[self._key] -= 1


class Action_Resource(Action):

    def __init__(self, name: str, desc: str | None, resource: str, cost: int) -> None:
        super().__init__(name, desc, ActionType.Resource)
        self._key = resource
        self._num = cost

    def available(self, res: ResourceMap) -> bool:
        return res[self._key] >= self._num

    def use(self, res: ResourceMap):
        res[self._key] -= self._num


def parseAction(data: dict, namespace: str, res: ResourceMap) -> Action:
    name = str(data["name"])
    try:
        desc = str(data["desc"])
    except:
        desc = None
    typeStr = str(data["type"])

    match typeStr:
        case "single-use":
            rWhen = When.parse(data["recharge-when"])
            return Action_Single(name, desc, rWhen, namespace, res)
        case "charges":
            rData = data["recharge"]
            rWhen = When.parse(rData["when"])
            rAmnt = str(rData["amnt"])
            maxCharges = int(data["max-charges"])
            return Action_Charges(name, desc, maxCharges, Recharge(rWhen, rAmnt), namespace, res)
        case "resource":
            amnt, resource = str(data["cost"]).strip().split()
            return Action_Resource(name, desc, resource, int(amnt))
        case _:
            raise RuntimeError(f"Invalid action type '{typeStr}'")
