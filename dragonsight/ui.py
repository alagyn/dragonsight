import os
import json
import sys
import glob
import subprocess

from .ui_boilerplate import window_mainloop
from .resource import Resource, When, RechargeAmount

import markstore
import imgui as im

GRID_SIZE = 6

WIN_FLAGS = im.WindowFlags.NoMove | im.WindowFlags.NoResize | im.WindowFlags.NoDecoration
TABLE_FLAGS = im.TableFlags.Borders

ADD_RES_POPUP = "Resource"

CONFIG_FILE = "dragonsight.json"

GRAY = im.ColorConvertFloat4ToU32(im.Vec4(0.4, 0.4, 0.4, 1.0))
BLACK = im.ColorConvertFloat4ToU32(im.Vec4(0, 0, 0, 1.0))
TABLE_TITLE = im.ColorConvertFloat4ToU32(im.Vec4(0.076, 0.762, 0.85, 1.0))
RES_TITLE = im.ColorConvertFloat4ToU32(im.Vec4(1.0, 0.631, 0.0, 1.0))
RED = im.ColorConvertFloat4ToU32(im.Vec4(1.0, 0.2, 0.2, 1.0))
NEW_PROF_COL = im.ColorConvertFloat4ToU32(im.Vec4(0.092, 0.672, 0.184, 1.0))
GREEN = im.ColorConvertFloat4ToU32(im.Vec4(0.092, 0.672, 0.184, 1.0))

FRAME_BG = im.Vec4(0.25, 0.25, 0.25, 0.54)

NO_MAX_BUTTON = im.ColorConvertFloat4ToU32(im.Vec4(0.25, 0.25, 0.25, 0.54))

# Progress bar colors
PROG_FULL = im.ColorConvertFloat4ToU32(im.Vec4(0.11, 0.682, 0.432, 1.0))
PROG_MID = im.ColorConvertFloat4ToU32(im.Vec4(0.742, 0.636, 0.073, 1.0))
PROG_LOW = im.ColorConvertFloat4ToU32(im.Vec4(0.707, 0.065, 0.065, 1.0))


def getDataDir() -> str:
    if os.name == "nt":
        base = os.environ["APPDATA"]
    elif os.name == 'posix':
        base = os.path.join(os.environ["HOME"], ".config")
    else:
        base = os.path.dirname(sys.argv[0])
    return os.path.join(base, 'bdd', 'dragonsight')


def openDirInExplorer(path: str):
    if os.name == "nt":
        os.startfile(path)
    elif os.name == 'posix':
        subprocess.Popen(["xdg-open", path])


SAN_TABLE = str.maketrans({
    " ": None,
    "\n": None,
    "\t": None,
    ".": None
})


def sanitizeStr(x: str) -> str:
    return x.translate(SAN_TABLE)


def deleteButton(safety: im.BoolRef, label: str) -> bool:
    im.PushStyleColor(im.Col.FrameBg, RED)
    im.PushStyleColor(im.Col.CheckMark, BLACK)
    im.PushStyleColor(im.Col.Text, RED)

    im.CheckBox("Safety", safety)

    im.PopStyleColor(3)

    im.BeginDisabled(not safety.val)
    im.SameLine(spacing=15)
    im.PushStyleColor(im.Col.Button, RED)
    out = im.Button(label)
    im.PopStyleColor(1)
    im.EndDisabled()

    return out


def tooltip(text: str):
    if im.BeginItemTooltip():
        im.PushTextWrapPos(im.GetFontSize() * 35.0)
        im.Text(text)
        im.PopTextWrapPos()
        im.EndTooltip()


def helpMarker(desc: str):
    im.TextDisabled('(?)')
    tooltip(desc)


DESC_FLAGS = im.InputTextFlags.AllowTabInput | im.InputTextFlags.WordWrap


class AddResourceModal:

    def __init__(self) -> None:
        self.name = im.StrRef(1024)
        self.max = im.IntRef(1)
        self.rechargeWhen = When.Never
        self.rechargeAmnt = im.StrRef(10)
        self.rechargeAll = im.BoolRef(False)
        self.desc = im.StrRef(4096)
        self.index = im.IntRef(0)
        self.numRes = 0

        self.errorText = ''

        self.submit = False
        self.cancel = False
        self.deleteSafety = im.BoolRef(False)
        self.delete = False

    def render(self, isEditing: bool = False) -> None:
        im.SetNextItemWidth(200)
        im.InputText("Name", self.name)
        if isEditing:
            im.SameLine(spacing=30)
            im.SetNextItemWidth(60)
            if im.InputInt("Position", self.index):
                self.index.val = min(self.numRes, max(0, self.index.val))
        im.PushItemWidth(200)
        if im.InputInt("Max Charges", self.max):
            self.max.val = max(-1, self.max.val)
        tooltip(
            "Set to 0 to disable charges display. Good for quick references!\n"
            "Set to -1 to allow infinite maximums."
        )
        im.BeginDisabled(self.max.val == 0)
        if im.BeginCombo("Recharge", self.rechargeWhen.toStr()):
            for x in When:
                if im.Selectable(x.toStr()):
                    self.rechargeWhen = x
            im.EndCombo()

        im.BeginDisabled(
            self.rechargeWhen == When.Never or (self.rechargeAll.val and not self.max.val == -1)
        )

        im.InputText("Recharge Amount", self.rechargeAmnt)
        tooltip("Enter a dice roll formula such as '2d6+2', '1d20', or simply '+2'")
        im.PopItemWidth()

        im.EndDisabled()  # End disabled if never recharge, or recharge all

        im.SameLine()
        im.BeginDisabled(self.max.val == -1)
        im.CheckBox("All", self.rechargeAll)
        tooltip("Toggle to recharge all instead of a dice roll")
        im.EndDisabled()  # End disabled if max == -1

        im.EndDisabled()  # End disabled if charges == 0

        im.InputTextMultiline("Description", self.desc, flags=DESC_FLAGS)
        if im.Button("Save"):
            self.submit = True
        im.SameLine(spacing=30)
        if im.Button("Cancel"):
            self.cancel = True
        if isEditing:
            im.Dummy(im.Vec2(1, 30))
            if deleteButton(self.deleteSafety, "Delete"):
                self.delete = True

        if len(self.errorText) > 0:
            im.PushStyleColor(im.Col.Text, RED)
            im.Text(self.errorText)
            im.PopStyleColor(1)

    def clear(self) -> None:
        self.name.set("")
        self.max.val = 1
        self.rechargeWhen = When.Never
        self.rechargeAmnt.set("")
        self.desc.set("")
        self.index.val = 0
        self.submit = False
        self.cancel = False
        self.delete = False
        self.errorText = ''

    def setResource(self, res: Resource, idx: int, numRes: int):
        self.name.set(res.name)
        self.max.val = res.maxVal
        self.rechargeWhen = res.rechargeWhen
        if res.rechargeAmount == RechargeAmount.All:
            self.rechargeAll.val = True
        else:
            self.rechargeAll.val = False
            self.rechargeAmnt.set(str(res.rechargeRoll))

        self.desc.set(res.desc.copy())
        self.index.val = idx
        self.numRes = numRes

    def updateResource(self, res: Resource) -> int:
        """
        Returns the index
        """
        res.name = self.name.copy()
        res.maxVal = self.max.val
        if res.maxVal >= 0:
            res.value = min(res.value, res.maxVal)
        res.rechargeWhen = self.rechargeWhen
        if self.rechargeAll.val:
            res.rechargeAmount = RechargeAmount.All
        else:
            res.rechargeAmount = RechargeAmount.Roll
            res.setRoll(self.rechargeAmnt.copy())

        res.desc.set(self.desc.copy())
        return self.index.val

    def getResource(self):
        if self.rechargeAll.val or self.rechargeWhen == When.Never:
            rechargeAmount = RechargeAmount.All
            rollStr = None
        else:
            rechargeAmount = RechargeAmount.Roll
            rollStr = self.rechargeAmnt.copy()

        res = Resource(
            name=self.name.copy(),
            desc=self.desc.copy(),
            maxVal=self.max.val,
            value=self.max.val if self.max.val > 0 else 0,
            when=self.rechargeWhen,
            rechargeAmount=rechargeAmount,
            rollStr=rollStr
        )

        return res


class Profile:

    def __init__(self, name: str = "New Profile", file: str | None = None) -> None:
        self.name = im.StrRef(name, 256)
        self.file = file


class ResourceTable:

    def __init__(self, name: str) -> None:
        self.name = im.StrRef(name, 256)
        self.resources: list[Resource] = []
        self.deleteSafety = im.BoolRef(False)
        self.updates = []

    def __getitem__(self, idx: int) -> Resource:
        return self.resources[idx]

    def __len__(self) -> int:
        return len(self.resources)


class DragonSightUI:

    def __init__(self) -> None:
        self.tables: list[ResourceTable] = []

        self.resModal = AddResourceModal()

        self.edit = im.BoolRef(False)

        self.selectedTable: int = 0
        self.selectedResource: int | None = None

        self.profileDeleteSafety = im.BoolRef(False)
        self.fastEditVar = im.IntRef(0)

        self.dataDir = getDataDir()
        self.profileDir = os.path.join(self.dataDir, "profiles")
        self.configFile = os.path.join(self.dataDir, CONFIG_FILE)

        if not os.path.exists(self.profileDir):
            os.makedirs(self.profileDir, exist_ok=True)

        self.profiles: list[Profile] = []
        self.selectProfIdx = 0

        for p in glob.glob(os.path.join(self.profileDir, "*.md")):
            with open(p, mode='rb') as f:
                prof = markstore.load(f)
            self.profiles.append(Profile(prof['name'], p))
            print("Loaded profile:", self.profiles[-1].name.view())

        if os.path.exists(self.configFile):
            with open(self.configFile, mode='rb') as f:
                config = json.load(f)
            selectedName = config['selected']
            for idx, p in enumerate(self.profiles):
                if p.name.view() == selectedName:
                    self.selectProfIdx = idx
                    break

            self.loadResources()
        else:
            self.profiles = [Profile()]
            self.edit.val = True

    def getSelectedProfile(self) -> Profile:
        try:
            return self.profiles[self.selectProfIdx]
        except IndexError:
            self.selectProfIdx = 0
            if len(self.profiles) == 0:
                self.profiles.append(Profile())
                self.edit.val = True

            return self.profiles[0]

    def isProfileEmpty(self) -> bool:
        if len(self.tables) == 0:
            return True
        for t in self.tables:
            if len(t.resources) > 0:
                return False
        return True

    def saveConfig(self):
        selectedProfile = self.profiles[self.selectProfIdx]
        config = {
            "selected": selectedProfile.name.copy()
        }
        with open(self.configFile, mode='w') as f:
            json.dump(config, f)

    def loadResources(self):
        self.tables.clear()
        p = self.getSelectedProfile()
        if p.file is None:
            return
        with open(p.file, mode='rb') as f:
            data = markstore.load(f)

        tables = data["tables"]

        for tData in tables:
            table = ResourceTable(tData["name"])

            res = tData["res"]
            for entry in res:
                name = entry['name']
                desc = entry['desc']
                val = int(entry['val'])
                maxVal = int(entry['max'])
                when = When[entry['when']]
                amnt = RechargeAmount[entry["type"]]

                chargeStr = None
                if when != When.Never and amnt != RechargeAmount.All:
                    chargeStr = entry["recharge"]

                table.resources.append(Resource(name, desc, maxVal, val, when, amnt, chargeStr))

            self.tables.append(table)

    def saveResources(self):
        p = self.getSelectedProfile()

        if self.isProfileEmpty():
            if p.file is None:
                return
            else:
                os.remove(p.file)
                return
        tables = []

        for table in self.tables:
            res = []
            for x in table.resources:
                d = {
                    "name": x.name,
                    "desc": x.desc.copy(),
                    "val": x.value,
                    "max": x.maxVal,
                    "when": x.rechargeWhen.name,
                    "type": x.rechargeAmount.name
                }

                if x.rechargeRoll is not None:
                    d['recharge'] = str(x.rechargeRoll)
                res.append(d)

            tData = {
                "name": table.name.view(),
                "res": res
            }
            tables.append(tData)

        data = {
            "name": p.name.copy(),
            "tables": tables
        }

        fileName = f'{self.selectProfIdx:04d}-{sanitizeStr(p.name.view())}.md'
        outFile = os.path.join(self.profileDir, fileName)
        tmpFile = outFile + ".tmp"
        with open(tmpFile, mode='wb') as f:
            markstore.dump(data, f)

        if p.file is not None and os.path.exists(p.file):
            os.remove(p.file)
        os.rename(tmpFile, outFile)
        p.file = outFile

    def run(self):
        if self.isProfileEmpty():
            self.edit.val = True
        try:
            window_mainloop("dragonsight", 1424, 768, self.render, self.init)
        except KeyboardInterrupt:
            pass
        self.saveResources()
        self.saveConfig()

    def init(self):
        style = im.GetStyle()
        style.Colors[im.Col.FrameBg] = FRAME_BG

    def loadProfile(self, idx: int):
        self.saveResources()
        self.selectProfIdx = idx
        self.loadResources()

    def render(self) -> bool:
        vp = im.GetMainViewport()
        im.SetNextWindowSize(vp.Size)
        im.SetNextWindowPos(vp.Pos)

        if im.Begin("Main", flags=WIN_FLAGS):
            p = self.getSelectedProfile()
            im.SetNextItemWidth(200)
            if self.edit.val:
                im.InputText("Profile", p.name)
            elif im.BeginCombo("Profile", p.name.view()):
                for idx, p in enumerate(self.profiles):
                    if im.Selectable(f'{p.name.view()}##{idx}', idx == self.selectProfIdx):
                        self.loadProfile(idx)

                im.PushStyleColor(im.Col.Text, NEW_PROF_COL)
                if im.Selectable(f"New Profile##{len(self.profiles)}"):
                    self.saveResources()
                    self.selectProfIdx = len(self.profiles)
                    self.profiles.append(Profile())
                    self.loadResources()
                    p = self.profiles[-1]
                    self.edit.val = True
                im.PopStyleColor(1)
                im.EndCombo()

            im.SameLine(spacing=20)

            if self.edit.val:
                im.PushStyleColor(im.Col.FrameBg, RED)
                im.PushStyleColor(im.Col.CheckMark, BLACK)
                im.PushStyleColor(im.Col.Text, RED)
                im.CheckBox("Edit", self.edit)
                im.PopStyleColor(3)

                im.SameLine(spacing=80)

                if deleteButton(self.profileDeleteSafety, "Delete Profile"):
                    self.profileDeleteSafety.val = False
                    toDelete = self.profiles.pop(self.selectProfIdx)
                    self.selectProfIdx = max(0, self.selectProfIdx - 1)
                    if toDelete.file is not None:
                        if os.path.isfile(toDelete.file):
                            print("Deleting", toDelete.file)
                            os.remove(toDelete.file)
                    self.edit.val = False

                    self.loadResources()

                im.SameLine(spacing=80)
                if im.Button("Profile Folder"):
                    openDirInExplorer(self.profileDir)
                tooltip(f"{self.profileDir}")

            else:
                if im.CheckBox("Edit", self.edit):
                    self.resModal.deleteSafety.val = False
                    for t in self.tables:
                        t.deleteSafety.val = False

            im.Dummy(im.Vec2(2, 5))

            rechargeWhen: When | None = None
            rechargeHovered: When = When.Never

            def rechargeButton(w: When):
                nonlocal rechargeWhen, rechargeHovered
                if im.Button(w.toStr()):
                    rechargeWhen = w
                if im.IsItemHovered():
                    rechargeHovered = w

            im.Text("Recharge:")
            im.SameLine(spacing=5)
            rechargeButton(When.ShortRest)
            im.SameLine(spacing=10)
            rechargeButton(When.LongRest)
            im.SameLine(spacing=10)
            rechargeButton(When.Daily)

            if rechargeWhen is not None:
                numUpdates = 0
                for table in self.tables:
                    table.updates = []
                    for res in table.resources:
                        start = res.value
                        amount = res.recharge(rechargeWhen)
                        end = res.value

                        if amount != 0:
                            numUpdates += 1
                            table.updates.append((res, start, amount, end))
                if numUpdates > 0:
                    im.OpenPopup("Update")

            im.SetNextWindowPos(im.Vec2(vp.Size.x / 2, vp.Size.y / 2), pivot=im.Vec2(0.5, 0.5))
            if im.BeginPopup("Update"):
                for table in self.tables:
                    if len(table.updates) == 0:
                        continue
                    im.PushStyleColor(im.Col.Text, TABLE_TITLE)
                    im.Text(table.name.view())
                    im.PopStyleColor(1)
                    im.Indent()
                    if im.BeginTable("UpdateTable", 2):
                        for res, start, amount, end in table.updates:
                            im.TableNextColumn()
                            im.Text(res.name)
                            im.TableNextColumn()
                            op = '+' if amount > 0 else '-'
                            im.Text(f'{start} {op} {abs(amount)} => {end}')
                        im.EndTable()
                    im.Unindent()
                im.EndPopup()

            im.Dummy(im.Vec2(2, 5))
            im.Separator()
            im.Dummy(im.Vec2(2, 5))

            if im.BeginChild("table"):
                deleteIdx = None
                moveTableIdx = None
                moveTableDir = 0
                for idx, table in enumerate(self.tables):
                    deleteTableRef = im.BoolRef(False)
                    moveTableRef = im.IntRef(0)
                    self.renderTable(table, idx, rechargeHovered, deleteTableRef, moveTableRef)
                    if deleteTableRef.val:
                        deleteIdx = idx
                    if moveTableRef.val != 0:
                        moveTableIdx = idx
                        moveTableDir = moveTableRef.val

                    im.Dummy(im.Vec2(2, 5))
                if deleteIdx is not None:
                    self.tables.pop(deleteIdx)
                if moveTableIdx is not None:
                    table = self.tables.pop(moveTableIdx)
                    self.tables.insert(moveTableIdx + moveTableDir, table)

                if self.edit.val:
                    if im.Button("Add Table"):
                        self.tables.append(ResourceTable("New Table"))
            im.EndChild()
        im.End()  # end main window

        return False

    def showEditPopup(self):
        if im.BeginPopupModal(ADD_RES_POPUP):
            self.resModal.render(self.selectedResource is not None)
            self.submitModal()
            im.EndPopup()

    def submitModal(self):
        if self.resModal.submit:
            self.storeResource()
        elif self.resModal.cancel:
            im.CloseCurrentPopup()
            self.resModal.clear()
            self.selectedResource = None
        elif self.resModal.delete:
            im.CloseCurrentPopup()
            self.resModal.clear()
            if self.selectedResource is not None:
                self.tables[self.selectedTable].resources.pop(self.selectedResource)
            self.selectedResource = None

    def storeResource(self):
        if self.selectedResource is None:
            try:
                res = self.resModal.getResource()
                self.tables[self.selectedTable].resources.append(res)
                im.CloseCurrentPopup()
                self.resModal.clear()
            except Exception as err:
                self.resModal.submit = False
                self.resModal.errorText = str(err)
        else:
            try:
                table = self.tables[self.selectedTable]
                selectedRes = table[self.selectedResource]
                oldIndex = self.selectedResource
                newIndex = self.resModal.updateResource(selectedRes)
                # clamp to range
                newIndex = max(min(len(table) - 1, newIndex), 0)
                # check if the index changed
                if oldIndex != newIndex:
                    table.resources.pop(oldIndex)
                    table.resources.insert(newIndex, selectedRes)

                im.CloseCurrentPopup()
                self.resModal.clear()
                self.selectedResource = None
            except Exception as err:
                self.resModal.submit = False
                self.resModal.errorText = str(err)

    def renderTable(
        self,
        table: ResourceTable,
        tableIdx: int,
        rechargeHovered: When,
        deleteTable: im.BoolRef,
        moveTable: im.IntRef
    ):
        """
        Return true if table should be deleted
        """
        im.PushID(tableIdx)

        if self.edit.val:
            im.SetNextItemWidth(200)
            im.InputText("Label", table.name)
            im.SameLine(spacing=20)
            if im.ArrowButton("move_up", im.Dir.Up):
                moveTable.val = -1
            im.SameLine(spacing=5)
            if im.ArrowButton("move_down", im.Dir.Down):
                moveTable.val = 1
            im.SameLine(spacing=50)
            if deleteButton(table.deleteSafety, "Delete Table"):
                deleteTable.val = True
            im.Dummy(im.Vec2(2, 5))
        else:
            style = im.GetStyle()
            im.PushFont(None, style.FontSizeBase * 2.0)  # type: ignore
            im.PushStyleColor(im.Col.Text, TABLE_TITLE)
            im.Text(table.name.view())
            im.PopStyleColor(1)
            im.PopFont()

        if im.BeginTable("main_table", GRID_SIZE, flags=TABLE_FLAGS):
            for idx, res in enumerate(table.resources):
                im.TableNextColumn()
                im.PushID(idx)
                self.renderResource(res, tableIdx, len(table), idx, rechargeHovered)
                im.PopID()

            if self.edit.val:
                im.TableNextColumn()
                im.Dummy(im.Vec2(2, 10))
                if im.Button("Add New Resource"):
                    self.selectedTable = tableIdx
                    self.selectedResource = None
                    im.OpenPopup(ADD_RES_POPUP)
                im.Dummy(im.Vec2(2, 10))

            im.SetNextWindowSize(im.Vec2(500, 400), im.Cond.Once)
            self.showEditPopup()
            im.EndTable()

        im.PopID()

    def renderResource(
        self,
        res: Resource,
        tableIdx: int,
        tableSize: int,
        resIdx: int,
        rechargeHovered: When
    ):
        im.Dummy(im.Vec2(2, 5))
        if self.edit.val:
            if im.Button(res.name):
                self.selectedTable = tableIdx
                self.selectedResource = resIdx
                self.resModal.setResource(res, resIdx, tableSize)
                im.OpenPopup(ADD_RES_POPUP)

            self.showEditPopup()
        else:
            im.PushStyleColor(im.Col.Text, RES_TITLE)
            im.Text(res.name)
            im.PopStyleColor(1)

        if res.maxVal > 0:
            if res.rechargeWhen.check(rechargeHovered):
                im.PushStyleColor(im.Col.Text, GREEN)
            else:
                im.PushStyleColor(im.Col.Text, GRAY)
            im.Text(f"[{res.rechargeWhen.toStr()}]")
            if res.rechargeWhen != When.Never:
                im.SameLine()
                if res.rechargeAmount == RechargeAmount.All:
                    im.Text("All")
                else:
                    im.Text(str(res.rechargeRoll))
            im.PopStyleColor(1)

        if res.maxVal == 1:
            state = im.BoolRef(res.value == 1)
            if im.CheckBox("Charged", state):
                if state.val:
                    res.value = 1
                else:
                    res.value = 0
        elif res.maxVal != 0:
            if im.Button("-") and res.value > 0:
                res.value -= 1
            im.SameLine()
            if res.maxVal > 0:
                perc = res.value / res.maxVal
                if perc > 0.6:
                    col = PROG_FULL
                elif perc > 0.25:
                    col = PROG_MID
                else:
                    col = PROG_LOW
                im.PushStyleColor(im.Col.PlotHistogram, col)
                im.SetNextItemWidth(150)
                im.ProgressBar(perc, size_arg=im.Vec2(0, 0), overlay=f"{res.value}/{res.maxVal}")
                im.PopStyleColor(1)
            else:
                im.PushStyleColor(im.Col.Button, NO_MAX_BUTTON)
                im.Button(f'{res.value}', im.Vec2(150, 0))
                im.PopStyleColor(1)
            tooltip("Click Me!")
            first = False
            if im.IsItemClicked():
                im.OpenPopup("Fast Edit")
                self.fastEditVar.val = 0
                first = True

            if im.BeginPopup("Fast Edit"):
                im.Text("Fast Add")
                if first:
                    im.SetKeyboardFocusHere()
                im.SetNextItemWidth(100)
                im.InputInt("Add/Sub", self.fastEditVar)
                if im.IsKeyPressed(im.ImKey.Enter) or im.IsKeyPressed(im.ImKey.KeypadEnter):
                    res.value += self.fastEditVar.val
                    self.fastEditVar.val = 0
                    res.clamp()
                    im.CloseCurrentPopup()
                im.EndPopup()

            im.SameLine()
            if im.Button("+") and (res.maxVal < 0 or res.value < res.maxVal):
                res.value += 1

        if res.maxVal != 0:
            im.TextWrapped(res.desc.view())
        else:
            im.InputTextMultiline("##desc", res.desc, im.Vec2(220, 100), flags=DESC_FLAGS)

        im.Dummy(im.Vec2(2, 5))


def main():
    ui = DragonSightUI()
    ui.run()
