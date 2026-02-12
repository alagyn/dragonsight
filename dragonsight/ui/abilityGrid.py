from ..player import Player

import imgui as im

GRID_SIZE = 5


class AbilityModal:

    def __init__(self) -> None:
        self.name = im.StrRef(128)
        self.desc = im.StrRef(256)
        self.cancel = False

    def clear(self):
        self.name.set("")
        self.desc.set("")

    def render(self) -> bool:
        """
        Returns true when accept has been clicked
        """
        out = False
        vp = im.GetMainViewport()
        center = im.Vec2(vp.Pos.x + vp.Size.x * 0.5, vp.Pos.y + vp.Size.y * 0.5)
        im.SetNextWindowPos(center, im.Cond.Appearing, im.Vec2(0.5, 0.5))
        # Maybe this can just be a normal popup?
        # only diff with a modal is you can't exit by clicking outside it
        if im.BeginPopupModal("add_ability_modal", None, im.WindowFlags.AlwaysAutoResize):
            if im.Button("Accept"):
                out = True
                im.CloseCurrentPopup()
            im.SameLine()
            if im.Button("Cancel"):
                im.CloseCurrentPopup()

            im.Separator()

            im.InputText("Name", self.name)
            im.InputTextMultiline("Desc", self.desc)

            if im.BeginTable("_modal_table", 2):
                im.TableNextColumn()
                # Counters
                if im.Button("Add Counter"):
                    pass
                im.TableNextColumn()
                # rolls

            im.EndPopup()
        return out


class AbilityGrid:

    def __init__(self):
        self.abilityModal = AbilityModal()

    TABLE_FLAGS = im.TableFlags.Borders

    def render(self, player: Player):
        if im.Begin("Abilities"):

            # TODO min col size?
            if im.BeginTable("_ability_grid", GRID_SIZE, AbilityGrid.TABLE_FLAGS):
                pass
                im.EndTable()
        im.End()
