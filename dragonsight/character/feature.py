import enum


class FeatureType(enum.IntEnum):
    Flavor = enum.auto()
    Action = enum.auto()
    MultiAction = enum.auto()
    Selection = enum.auto()


class Feature:
    """
    Base Class
    """

    def __init__(
        self,
        ftype: FeatureType,
        name: str,
        unlock: int,
        shortDesc: str,
        longDesc: str | None,
        resists: list[str],
        immunities: list[str]
    ) -> None:
        self.name = name
        self.ftype = ftype
        self.unlock = unlock
        self.shortDesc = shortDesc
        self.longDesc = longDesc
        self.resists = resists
        self.immunities = immunities


class Feature_Action(Feature):

    def __init__(
        self,
        name: str,
        unlock: int,
        shortDesc: str,
        longDesc: str | None,
        resists: list[str],
        immunities: list[str],
        ifStr: str,
        thenStr: str
    ) -> None:
        super().__init__(FeatureType.Action, name, unlock, shortDesc, longDesc, resists, immunities)
        self.ifStr = ifStr
        self.thenStr = thenStr


def parseFeature(data: dict) -> Feature:
    # TODO error handling
    name = str(data['name'])
    ftypeStr = str(data['type'])
    unlock = int(data['unlock'])
    shortDesc = str(data['short-desc'])
    try:
        longDesc = str(data['long-desc'])
    except KeyError:
        longDesc = None
    try:
        resists = str(data['resist']).split(",")
    except KeyError:
        resists = []
    try:
        immunities = str(data['immune']).split(",")
    except KeyError:
        immunities = []

    match ftypeStr.lower():
        case 'flavor':
            return Feature(
                FeatureType.Flavor,
                name,
                unlock,
                shortDesc,
                longDesc,
                resists,
                immunities
            )
        case 'action':
            ifStr = str(data["if"])
            thenStr = str(data["then"])
            return Feature_Action(
                name,
                unlock,
                shortDesc,
                longDesc,
                resists,
                immunities,
                ifStr,
                thenStr
            )
        case 'multi-action':
            pass
        case 'selection':
            pass
        case _:
            raise RuntimeError(f"Invalid feature type: '{ftypeStr}'")
