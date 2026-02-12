from .ui.boilerplate import window_mainloop

from .ui.abilityGrid import AbilityGrid
from .player import Player


class UI:

    def __init__(self):
        self.abilityGrid = AbilityGrid()
        # TODO
        self.player = Player("test.db")

    def ui_init(self):
        pass

    def render(self):
        self.abilityGrid.render(self.player)

    def cleanup(self):
        pass


def main():
    ui = UI()
    window_mainloop("Dragonsight", 1024, 768, ui.render, ui.ui_init, ui.cleanup)


if __name__ == '__main__':
    main()
