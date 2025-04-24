import sqlite3
from .dbWriter import DBObject, DBWriter


class Counter(DBObject):

    def __init__(self,
                 dbWriter: DBWriter,
                 counterID: int,
                 abilityID: int,
                 name: str,
                 maxValue: int,
                 curValue: int | None = None):
        super().__init__(dbWriter)
        self.id = counterID
        self._abilityID = abilityID
        self._name = name
        self._maxValue = maxValue
        self._curValue = curValue or maxValue

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name_set(self, name: str):
        self._dirty = True
        self._name = name

    @property
    def maxValue(self) -> int:
        return self._maxValue

    @maxValue.setter
    def maxValue_set(self, maxValue: int):
        self._dirty = True
        self._maxValue = maxValue

    @property
    def curValue(self) -> int:
        return self._curValue

    @curValue.setter
    def curValue_set(self, curValue: int):
        self._dirty = True
        self._curValue = curValue

    _UPDATE = """
    UPDATE counters SET
        name = :name,
        max = :max,
        value = :value
    WHERE
        counterID = :counterID
    """

    def serialize(self, cur: sqlite3.Cursor):
        cur.execute(
            Counter._UPDATE, {
                "name": self._name,
                "max": self._maxValue,
                "value": self._curValue,
                "counterID": self.id
            })

    _INSERT = """
    INSERT INTO counters
    (abilityID, name, max, value)
    VALUES
    (:abilityID, :name, :max, :max)
    RETURNING counterID
    """

    @classmethod
    def new(cls, dbWriter: DBWriter, abilityID: int, name: str,
            maxVal: int) -> 'Counter':
        cur = dbWriter.cursor()
        res = cur.execute(Counter._INSERT, {
            "abilityID": abilityID,
            "name": name,
            "max": maxVal
        })

        cID = int(res.fetchone()[0])

        dbWriter.commit()

        return Counter(dbWriter, cID, abilityID, name, maxVal)


class Roll(DBObject):

    def __init__(self, dbWriter: DBWriter, rollID: int, abilityID: int,
                 name: str, rollStr: str):
        super().__init__(dbWriter)
        self.id = rollID
        self._abilityID = abilityID
        self._name = name
        self._rollStr = rollStr

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name_set(self, name: str):
        self._dirty = True
        self._name = name

    @property
    def rollStr(self) -> str:
        return self._rollStr

    @rollStr.setter
    def rollStr_set(self, rollStr: str):
        self._dirty = True
        self._rollStr = rollStr

    _UPDATE = """
    UPDATE rolls SET
        name = :name, roll = :roll
    WHERE
        rollID = :rollID
    """

    def serialize(self, cur: sqlite3.Cursor) -> None:
        cur.execute(Roll._UPDATE, {
            "name": self._name,
            "roll": self._rollStr,
            "rollID": self.id
        })

    _INSERT = """
    INSERT INTO rolls
    (abilityID, name, roll)
    VALUES
    (:abilityID, :name, :roll)
    RETURNING rollID
    """

    @classmethod
    def new(cls, dbWriter: DBWriter, abilityID: int, name: str,
            rollStr: str) -> 'Roll':
        cur = dbWriter.cursor()
        res = cur.execute(Roll._INSERT, {
            "abilityID": abilityID,
            "name": name,
            "roll": rollStr
        })

        rID = int(res.fetchone()[0])

        dbWriter.commit()

        return Roll(dbWriter, rID, abilityID, name, rollStr)


class Ability(DBObject):

    def __init__(self, dbWriter: DBWriter, abilityID: int, name: str,
                 desc: str):
        super().__init__(dbWriter)
        self._dbWriter = dbWriter
        self.id = abilityID
        self._name = name
        self._desc = desc
        self.counters: list[Counter] = []
        self.rolls: list[Roll] = []

    def addCounter(self, name: str, maxValue: int):
        c = Counter.new(self._dbWriter, self.id, name, maxValue)
        self.counters.append(c)

    def addRoll(self, name: str, rollStr: str):
        r = Roll.new(self._dbWriter, self.id, name, rollStr)
        self.rolls.append(r)

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name_set(self, name: str):
        self._dirty = True
        self._name = name

    @property
    def desc(self) -> str:
        return self._desc

    @desc.setter
    def desc_set(self, desc: str):
        self._dirty = True
        self._desc = desc

    _UPDATE = """
    UPDATE abilities SET
        name = :name,
        desc = :desc,
    WHERE
        abilityID = :abilityID
    """

    def serialize(self, cur: sqlite3.Cursor) -> None:
        cur.execute(Ability._UPDATE, {
            "name": self._name,
            "desc": self._desc,
            "abilityID": self.id
        })

    _INSERT = """
    INSERT INTO abilities
    (name, desc)
    VALUES 
    (:name, :desc)
    RETURNING abilityID
    """

    @classmethod
    def new(cls, dbWriter: DBWriter, name: str, desc: str) -> 'Ability':
        cur = dbWriter.cursor()
        res = cur.execute(Ability._INSERT, {"name": name, "desc": desc})

        aID = int(res.fetchone()[0])

        dbWriter.commit()

        return Ability(dbWriter, aID, name, desc)
