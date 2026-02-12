import sqlite3
import os

_RESOURCES_SCHEMA = """
CREATE TABLE IF NOT EXISTS
resources
(
    key TEXT PRIMARY KEY,
    value INTEGER
)
"""

_LEVELS_SCHEMA = """
CREATE TABLE IF NOT EXISTS
levels
(
    class_id TEXT,
    level INTEGER
)
"""

_STATS_SCHEMA = """
CREATE TABLE IF NOT EXISTS
stats
(
    str INTEGER,
    dex INTEGER,
    con INTEGER,
    int INTEGER,
    wis INTEGER,
    cha INTEGER
)
"""


class Player:

    def __init__(self, dbFile: str):
        needInit = not os.path.exists(dbFile)

        self.db = sqlite3.connect(dbFile)

        # Resources
        self.res: dict[str,
                       int] = {}

        self.str = 0
        self.dex = 0
        self.con = 0
        self.int = 0
        self.wis = 0
        self.cha = 0

        if needInit:
            cur = self.db.cursor()
            cur.execute(_RESOURCES_SCHEMA)
            cur.execute(_LEVELS_SCHEMA)
            cur.execute(_STATS_SCHEMA)

            cur.execute("INSERT INTO stats VALUES (0, 0, 0, 0, 0, 0)")

            self.db.commit()
        else:
            self._loadPlayer()

        self.levels: dict[str,
                          int] = {}

        self.features = []

    _GET_RESOURCES = "SELECT key, value FROM resources"
    _ADD_RESOURCE = "INSERT INTO resources (key, value) VALUES (:key, :value)"
    _SET_RESOURCE = "UPDATE resources SET value = :value WHERE key = :key"

    _GET_LEVELS = "SELECT class_id, level FROM levels"
    _ADD_LEVEL = "INSERT INTO levels (class_id, level) VALUES (:class_id, :level)"
    _SET_LEVEL = "UPDATE levels SET level = :level WHERE class_id = :class_id"

    _GET_STATS = "SELECT (str, dex, con, int, wis, cha) FROM stats"
    _SET_STATS = "UPDATE stats SET str = :str, dex = :dex, con = :con, int = :int, wis = :wis, cha = :cha"

    def _loadPlayer(self):
        cur = self.db.cursor()

        res = cur.execute(Player._GET_RESOURCES)

        for row in res.fetchall():
            x = iter(row)
            key = str(next(x))
            value = int(next(x))
            self.res[key] = value

        res = cur.execute(Player._GET_LEVELS)

        for row in res.fetchall():
            x = iter(row)
            classID = str(next(x))
            level = int(next(x))
            self.levels[classID] = level

        res = cur.execute(Player._GET_STATS)

        x = iter(res.fetchone())
        self.str = int(next(x))
        self.dex = int(next(x))
        self.con = int(next(x))
        self.int = int(next(x))
        self.wis = int(next(x))
        self.cha = int(next(x))

    def addResource(self, key: str, value: int):
        self.res[key] = value
        cur = self.db.cursor()
        cur.execute(Player._ADD_RESOURCE,
                    {
                        "key": key,
                        "value": value
                    })
        self.db.commit()
