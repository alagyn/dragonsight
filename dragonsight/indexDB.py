import sqlite3
import os
import yaml
import glob

# TODO location
DATA_DIR = os.path.realpath(os.path.join(__file__, "..", "data"))

_CLASS_SCHEMA = """
CREATE TABLE IF NOT EXISTS
classes
(
    name TEXT,
    cID TEXT PRIMARY KEY,
    path TEXT
)
"""

_INSERT_CLASS = """
INSERT INTO classes
    (name, cID, path)
VALUES
    (:name, :cID, :path)
"""

_GET_CLASSES = """
SELECT name, cID, path FROM classes
"""

_SUBCLASS_SCHEMA = """
CREATE TABLE IF NOT EXISTS
subclasses
(
    name TEXT,
    cID TEXT,
    path TEXT,
    FOREIGN KEY (cID) REFERENCES classes (cID)
)
"""

_INSERT_SUBCLASS = """
INSERT INTO subclasses
    (name, cID, path)
VALUES
    (:name, :cID, :path)
"""

_GET_SUBCLASSES = """
SELECT name, cID, path FROM subclasses
"""


class IndexedClass:

    def __init__(self, name: str, cID: str, path: str) -> None:
        self.name = name
        self.cID = cID
        self.path = path


class IndexDB:

    def __init__(self) -> None:
        # TODO location
        dbLoc = "ds_index.db"
        needsInit = not os.path.exists(dbLoc)
        self.db = sqlite3.connect(dbLoc)

        self.classes: list[IndexedClass] = []
        self.subclasses: list[IndexedClass] = []

        if needsInit:
            cur = self.db.cursor()
            cur.execute(_CLASS_SCHEMA)
            cur.execute(_SUBCLASS_SCHEMA)
            self.db.commit()

            # TODO delay this?
            self.reindex()
        else:
            self.loadIndex()

    def reindex(self):
        self.classes.clear()
        self.subclasses.clear()

        cur = self.db.cursor()

        classesDir = os.path.join(DATA_DIR, "classes")
        for file in glob.iglob(os.path.join(classesDir, "*.yaml")):
            fullPath = os.path.join(classesDir, file)
            with open(fullPath, mode='rb') as f:
                data = yaml.load(f, yaml.CLoader)
            name = data["name"]
            cID = data["id"]
            cur.execute(_INSERT_CLASS,
                        {
                            "name": name,
                            "cID": cID,
                            "path": file
                        })

            self.classes.append(IndexedClass(name, cID, file))

        subclassesDir = os.path.join(DATA_DIR, "subclasses")
        for file in glob.iglob(os.path.join(subclassesDir, "*.yaml")):
            fullPath = os.path.join(subclassesDir, file)
            with open(fullPath, mode='rb') as f:
                data = yaml.load(f, yaml.CLoader)
            name = data["name"]
            cID = data["base"]
            cur.execute(_INSERT_SUBCLASS,
                        {
                            "name": name,
                            "cID": cID,
                            "path": file
                        })

            self.classes.append(IndexedClass(name, cID, file))

        self.db.commit()

    def loadIndex(self):
        self.classes.clear()
        self.subclasses.clear()

        cur = self.db.cursor()

        res = cur.execute(_GET_CLASSES)
        for row in res.fetchall():
            x = iter(row)
            name = next(x)
            cID = next(x)
            path = next(x)
            self.classes.append(IndexedClass(name, cID, path))

        res = cur.execute(_GET_SUBCLASSES)
        for row in res.fetchall():
            x = iter(row)
            name = next(x)
            cID = next(x)
            path = next(x)
            self.subclasses.append(IndexedClass(name, cID, path))
