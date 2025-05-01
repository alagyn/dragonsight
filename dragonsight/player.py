import sqlite3
import os
from .ability import Ability, Roll, Counter
from .dbWriter import DBWriter

_RESOURCES_SCHEMA = """
CREATE TABLE IF NOT EXISTS
resources
(
    key TEXT PRIMARY KEY,
    value INTEGER
)
"""


class Player:

    def __init__(self, dbFile: str):
        needInit = not os.path.exists(dbFile)

        self._dbConn = sqlite3.connect(dbFile)
        self.db = DBWriter(self._dbConn)

        # Resources
        self.res: dict[str,
                       int] = {}

        if needInit:
            cur = self.db.cursor()
            cur.execute(_RESOURCES_SCHEMA)
            self.db.commit()
        else:
            self._loadPlayer()

    _GET_RESOURCES = "SELECT key, value FROM resources"
    _ADD_RESOURCE = "INSERT INTO resources (key, value) VALUES (:key, :value)"

    def _loadPlayer(self):
        cur = self.db.cursor()

        res = cur.execute(Player._GET_RESOURCES)

        for row in res.fetchall():
            x = iter(row)
            key = str(next(x))
            value = int(next(x))
            self.res[key] = value

    def addResource(self, key: str, value: int):
        self.res[key] = value
        cur = self.db.cursor()
        cur.execute(Player._ADD_RESOURCE,
                    {
                        "key": key,
                        "value": value
                    })
        self.db.commit()
