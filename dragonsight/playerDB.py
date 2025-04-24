import sqlite3

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
    abilityID INTEGER NOT NULL,
    name TEXT,
    max INTEGER,
    FOREIGN KEY (abilityID) REFERENCES abilities (abilityID)
)
"""


class Counter:

    def __init__(self, name: str):
        self.name = name


class Roll:

    def __init__(self, name: str, roll: str):
        self.name = name
        self.roll = roll


class Ability:

    def __init__(self, name: str, desc: str):
        self.name = name
        self.desc = desc
        self.counters: list[Counter] = []
        self.rolls: list[Roll] = []

    def addCounter(self, name: str):
        self.counters.append(Counter(name))

    def addRoll(self, name: str, roll: str):
        self.rolls.append(Roll(name, roll))


class PlayerDB:

    def __init__(self, dbFile: str):
        self.db = sqlite3.connect(dbFile)

    _ADD_ABILITY = """
    INSERT INTO abilities
    (name, desc)
    VALUES 
    (:name, :desc)
    """

    def addAbility(self, name: str, desc: str):
        cur = self.db.cursor()
        cur.execute(PlayerDB._ADD_ABILITY, {"name": name, "desc": desc})
        self.db.commit()

    _ADD_ROLL = """
    INSERT INTO rolls
    (abilityID, name, roll)
    VALUES
    (:abilityID, :name, :roll)
    """

    def addRoll(self, abilityID: int, name: str, roll: str):
        cur = self.db.cursor()
        cur.execute(PlayerDB._ADD_ROLL, {
            "abilityID": abilityID,
            "name": name,
            "roll": roll
        })
        self.db.commit()

    _ADD_COUNTER = """
    INSERT INTO counters
    (abilityID, name, max)
    VALUES
    (:abilityID, :name, :max)
    """

    def addCounter(self, abilityID: int, name: str, maxValue: int):
        cur = self.db.cursor()
        cur.execute(PlayerDB._ADD_COUNTER, {
            "abilityID": abilityID,
            "name": name,
            "max": maxValue
        })
        self.db.commit()
