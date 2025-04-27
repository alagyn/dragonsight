from .resourceStack import ResourceStack


class Expression:

    def __init__(self, exprStr: str) -> None:
        rawValues = exprStr.split(" ")
        values = []
        for x in rawValues:
            x = x.strip()
            if len(x) == 0:
                continue
            values.append(x)

    def eval(self, res: ResourceStack) -> int:
        return 0
