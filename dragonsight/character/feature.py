import enum

from .action import Action, parseAction


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
        action: Action
    ) -> None:
        super().__init__(FeatureType.Action, name, unlock, shortDesc, longDesc, resists, immunities)
        self.action = action


class Feature_MultiAction(Feature):

    def __init__(
        self,
        name: str,
        unlock: int,
        shortDesc: str,
        longDesc: str | None,
        resists: list[str],
        immunities: list[str],
        actions: list[Action]
    ) -> None:
        super().__init__(
            FeatureType.MultiAction,
            name,
            unlock,
            shortDesc,
            longDesc,
            resists,
            immunities
        )
        self.actions = actions


class Feature_Selection(Feature):

    def __init__(
        self,
        name: str,
        unlock: int,
        shortDesc: str,
        longDesc: str | None,
        resists: list[str],
        immunities: list[str],
        actions: list[Action]
    ) -> None:
        super().__init__(
            FeatureType.Selection,
            name,
            unlock,
            shortDesc,
            longDesc,
            resists,
            immunities
        )
        self.actions = actions


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
            action = parseAction(data["action"])
            return Feature_Action(name, unlock, shortDesc, longDesc, resists, immunities, action)
        case 'multi-action':
            actions = []
            for x in data["actions"]:
                actions.append(parseAction(x))
            return Feature_MultiAction(
                name,
                unlock,
                shortDesc,
                longDesc,
                resists,
                immunities,
                actions
            )
        case 'selection':
            actions = []
            for x in data["actions"]:
                actions.append(parseAction(x))
            return Feature_Selection(
                name,
                unlock,
                shortDesc,
                longDesc,
                resists,
                immunities,
                actions
            )
        case _:
            raise RuntimeError(f"Invalid feature type: '{ftypeStr}'")
