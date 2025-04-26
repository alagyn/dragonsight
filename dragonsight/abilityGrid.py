from .player import Player

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
        center = im.Vec2(vp.Pos.x + vp.Size.x * 0.5,
                         vp.Pos.y + vp.Size.y * 0.5)
        im.SetNextWindowPos(center, im.Cond.Appearing, im.Vec2(0.5, 0.5))
        # Maybe this can just be a normal popup?
        # only diff with a modal is you can't exit by clicking outside it
        if im.BeginPopupModal("add_ability_modal", None,
                              im.WindowFlags.AlwaysAutoResize):
            im.InputText("Name", self.name)
            im.InputTextMultiline("Desc", self.desc)
            if im.Button("Accept"):
                out = True
                im.CloseCurrentPopup()
            im.SameLine()
            if im.Button("Cancel"):
                im.CloseCurrentPopup()

            im.EndPopup()
        return out


class AbilityGrid:

    def __init__(self):
        self.abilityModal = AbilityModal()

    TABLE_FLAGS = im.TableFlags.Borders

    def render(self, player: Player):
        if im.Begin("Abilities"):
            if im.Button("Add Ability"):
                im.OpenPopup("add_ability_modal")
                self.abilityModal.clear()

            # Noop if not needed
            if self.abilityModal.render():
                player.addAbility(self.abilityModal.name.view(),
                                  self.abilityModal.desc.view())

            if im.BeginTable("_ability_grid", GRID_SIZE,
                             AbilityGrid.TABLE_FLAGS):
                for ability in player.abilities:
                    im.TableNextColumn()
                    im.TextWrapped(ability.name)
                    im.Separator()
                    im.TextWrapped(ability.desc)

                im.EndTable()
        im.End()
