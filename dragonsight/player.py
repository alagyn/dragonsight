import sqlite3
import os
from .ability import Ability, Roll, Counter
from .dbWriter import DBWriter

ABILITY_SCHEMA = """
CREATE TABLE IF NOT EXISTS
abilities
(
    abilityID INTEGER PRIMARY KEY,
    name TEXT,
    desc TEXT
)
"""

ROLLS_SCHEMA = """
CREATE TABLE IF NOT EXISTS
rolls
(
    rollID INTEGER PRIMARY KEY,
    abilityID INTEGER NOT NULL,
    name TEXT,
    roll TEXT,
    FOREIGN KEY (abilityID) REFERENCES abilities (abilityID)
)
"""

COUNTERS_SCHEMA = """
CREATE TABLE IF NOT EXISTS
counters
(
    counterID INTEGER PRIMARY KEY,
    abilityID INTEGER NOT NULL,
    name TEXT,
    max INTEGER,
    value INTEGER,
    FOREIGN KEY (abilityID) REFERENCES abilities (abilityID)
)
"""


class Player:

    def __init__(self, dbFile: str):
        needInit = not os.path.exists(dbFile)

        self._dbConn = sqlite3.connect(dbFile)
        self.db = DBWriter(self._dbConn)

        self.abilities: list[Ability] = []

        if needInit:
            cur = self.db.cursor()
            cur.execute(ABILITY_SCHEMA)
            cur.execute(ROLLS_SCHEMA)
            cur.execute(COUNTERS_SCHEMA)
            self.db.commit()
        else:
            self._loadPlayer()

    _GET_ABILITIES = """
    SELECT abilityID, name, desc FROM abilities
    """

    _GET_ROLLS = """
    SELECT rollID, abilityID, name, roll FROM rolls
    """

    _GET_COUNTERS = """
    SELECT counterID, abilityID, name, max, value FROM counters
    """

    def _loadPlayer(self):
        cur = self.db.cursor()

        res = cur.execute(Player._GET_ABILITIES)

        # save the abilities for later
        aMap: dict[int, Ability] = {}

        for row in res.fetchall():
            x = iter(row)
            aID = int(next(x))
            name = str(next(x))
            desc = str(next(x))
            ability = Ability(self.db, aID, name, desc)
            aMap[aID] = ability
            self.abilities.append(ability)

        res = cur.execute(Player._GET_ROLLS)

        for row in res.fetchall():
            x = iter(row)
            rID = int(next(x))
            aID = int(next(x))
            name = str(next(x))
            rollStr = str(next(x))
            roll = Roll(self.db, rID, aID, name, rollStr)
            aMap[aID].rolls.append(roll)

        res = cur.execute(Player._GET_COUNTERS)

        for row in res.fetchall():
            x = iter(row)
            cID = int(next(x))
            aID = int(next(x))
            name = str(next(x))
            maxVal = int(next(x))
            curVal = int(next(x))
            counter = Counter(self.db, cID, aID, name, maxVal, curVal)
            aMap[aID].counters.append(counter)

    def addAbility(self, name: str, desc: str):
        a = Ability.new(self.db, name, desc)
        self.abilities.append(a)
