from .resource import Resource, parseResource
from .feature import Feature, parseFeature
from .resourceMap import ResourceMap


class CharClass:

    def __init__(self) -> None:
        self.name = ""
        self.cID = ""
        self.spellcasting: str | None = None
        self.hitDice: str = ""
        # TODO proficiencies?
        self.spellslotsPerLevel: list[list[int]] = []
        self.resources: list[Resource] = []
        self.features: list[Feature] = []


def parseCharClass(data: dict, res: ResourceMap) -> CharClass:
    out = CharClass()
    out.name = str(data["name"])
    out.cID = str(data['id'])
    try:
        out.spellcasting = str(data["spellcasting"])
    except KeyError:
        pass

    try:
        out.spellslotsPerLevel = data["spellslots-per-level"]
    except KeyError:
        pass

    try:
        for x in data["resources"]:
            out.resources.append(parseResource(x, out.cID, res))
    except KeyError:
        pass

    try:
        for x in data["features"]:
            out.features.append(parseFeature(x, out.cID, res))
    except KeyError:
        pass

    return out
