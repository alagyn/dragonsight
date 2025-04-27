class ResourceStack:

    def __init__(self) -> None:
        self.stack: list[dict[str, int]] = []

    def pushLayer(self, layer: dict[str, int]) -> None:
        self.stack.append(layer)

    def popLayer(self) -> None:
        self.stack.pop()

    def __getitem__(self, key: str) -> int:
        """
        Attempt to resolve a key from the stack
        """
        for x in reversed(self.stack):
            try:
                return x[key]
            except KeyError:
                pass

        raise KeyError(key)
