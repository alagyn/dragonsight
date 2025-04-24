from .ui_boilerplate import window_mainloop


class UI:

    def __init__(self):
        pass

    def ui_init(self):
        pass

    def render(self):
        pass

    def cleanup(self):
        pass


def main():
    ui = UI()
    window_mainloop("Dragonsight", 1024, 768, ui.render, ui.ui_init,
                    ui.cleanup)


if __name__ == '__main__':
    main()
