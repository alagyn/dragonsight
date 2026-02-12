import re

from .character.resourceMap import ResourceMap

EXPR_RE = re.compile(
    r'(?P<numDice>\d*)[dD](?P<diceSize>\d+)\s*((?P<operator>[+-*/]\s*(?P<value>\w+))'
)


class Expression:

    def __init__(self, exprStr: str) -> None:
        m = EXPR_RE.fullmatch(exprStr.strip())
        if m is None:
            raise RuntimeError(f"Invalid expression '{exprStr}'")

    def eval(self, res: ResourceMap) -> int:
        return 0
