import enum

from .recharge import Recharge


class ActionType(enum.IntEnum):
    Single = enum.auto()
    Charges = enum.auto()
    Resource = enum.auto()


class Action:

    def __init__(self, name: str, desc: str | None) -> None:
        self.name = name
        self.desc = desc

    def available(self) -> bool:
        raise NotImplementedError()

    def recharge(self, when: Recharge):
        raise NotImplementedError()


class Action_Single(Action):
    pass


def parseAction(data: dict) -> Action:
    pass
