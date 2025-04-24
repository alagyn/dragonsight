import sqlite3


class DBWriter:

    def __init__(self, db: sqlite3.Connection):
        self._db = db
        self._dbObjs: list[DBObject] = []

    def save(self):
        cur = self._db.cursor()
        for obj in self._dbObjs:
            if obj._dirty:
                obj._dirty = False
                obj.serialize(cur)
                # TODO commit after each?
        self._db.commit()

    def cursor(self) -> sqlite3.Cursor:
        return self._db.cursor()

    def commit(self) -> None:
        self._db.commit()


class DBObject:
    _DB_OBJ_ID_GEN = 0

    def __init__(self, dbWriter: DBWriter):
        self._dbID = DBObject._DB_OBJ_ID_GEN
        DBObject._DB_OBJ_ID_GEN += 1
        self._dirty = False
        dbWriter._dbObjs.append(self)

    def serialize(self, cur: sqlite3.Cursor) -> None:
        raise NotImplementedError()
