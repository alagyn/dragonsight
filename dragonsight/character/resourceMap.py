class ResourceMap:

    def __init__(self) -> None:
        self._res: dict[str,
                        int] = {}
        self.dirty: set[str] = set()

    def clean(self):
        self.dirty.clear()

    def __contains__(self, key: str) -> bool:
        return key in self._res

    def __getitem__(self, key: str) -> int:
        return self._res[key]

    def __setitem__(self, key: str, val: int):
        self._res[key] = val
        self.dirty.add(key)
