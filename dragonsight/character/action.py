import enum


class ActionType(enum.IntEnum):
    Single = enum.auto()
    Charges = enum.auto()
    Resource = enum.auto()


class Action:

    def __init__(self, name: str, desc: str | None, ifStr: str, thenStr: str) -> None:
        self.name = name
        self.desc = desc
        self.ifStr = ifStr
        self.thenStr = thenStr
