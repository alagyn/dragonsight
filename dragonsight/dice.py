import random
import re

DICE_PATTERN = r'(?P<numDice>\d*)[dD](?P<diceSize>\d+)'
OP_PATTERN = r'(?P<operator>[+-])'
VAL_PATTERN = r'(?P<value>\d+)'
EXPR_RE = re.compile(fr'{DICE_PATTERN}\s*({OP_PATTERN}\s*{VAL_PATTERN})?')


class DiceRoll:

    def __init__(self, dice: str) -> None:
        m = EXPR_RE.fullmatch(dice)
        if m is None:
            try:
                self._add = int(dice)
                self._numRolls = 0
                self._diceSize = 0
                return
            except:
                raise RuntimeError(f"Invalid dice roll: '{dice}'")

        numRolls, diceSize = m.group("numDice", "diceSize")
        if numRolls is None and diceSize is None:
            self._numRolls = 0
        else:
            if diceSize is not None:
                self._diceSize = int(diceSize)
            else:
                self._diceSize = 0

            if numRolls is not None and len(numRolls) > 0:
                self._numRolls = int(numRolls)
            else:
                self._numRolls = 1

        op, value = m.group("operator", "value")
        if op is not None and value is not None:
            self._add = int(value)
            if op == '-':
                self._add = -self._add

        else:
            self._add = 0

    def roll(self) -> int:
        random.seed()

        rolls = 0
        for i in range(self._numRolls):
            roll = random.randint(1, self._diceSize)
            print(f"roll [1,{self._diceSize}] = {roll}")
            rolls += roll

        out = rolls + self._add
        print(f"Total = {rolls} + {self._add} => {out}")

        return out

    def __str__(self) -> str:
        diceStr = ""
        if self._numRolls > 0:
            diceStr += f'{self._numRolls}D{self._diceSize}'
        if self._add < 0:
            diceStr += f'{self._add}'
        elif self._add > 0:
            diceStr += f'+{self._add}'

        return diceStr
