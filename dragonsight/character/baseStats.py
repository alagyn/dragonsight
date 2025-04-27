def calcModifier(value: int):
    return value // 2 - 5


class BaseStats:

    def __init__(self) -> None:
        self.str = 0
        self.dex = 0
        self.con = 0
        self.int = 0
        self.wis = 0
        self.cha = 0
