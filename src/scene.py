"""scenel.py"""

import tkinter.filedialog
import pygame as pg
import numpy as np
import enum
from src.fonts import Fonts
import src.ui_elements as ui_elements
import src.config as cfg
import tkinter.filedialog

pg.init()


class SCENE_STATE(enum.Enum):
    """
    enum class for scene state.
    """

    TOP = 0
    BRIEFING = 1
    GAME = 2
    EXIT = 3
    QUIT = 4


class AppMain:
    def __init__(self) -> None:
        info = pg.display.Info()
        screen_width, screen_height = info.current_w, info.current_h

        # self.screen = pg.display.set_mode((screen_width, screen_height), pg.FULLSCREEN)
        self.screen = pg.display.set_mode((screen_width // 2, screen_height // 2))
        pg.display.set_caption("F.T.E. OpenRocket Visualizer")
        pg.display.set_icon(pg.image.load("img/ろけにゃん_ロケット.png"))
        self.top = Top()

        self.scene_flag = SCENE_STATE.TOP

    def run(self) -> None:
        clock = pg.time.Clock()

        fps = 60
        clock.tick(fps)
        while True:
            # main loop
            if self.scene_flag is SCENE_STATE.TOP:
                self.scene_flag = self.top.exec(self.screen)
            else:
                break


class Top:
    """
    Top scene of the game. This Scene is the first scene to be displayed when the game starts.
    """

    def __init__(self) -> None:
        self.orkFile: str = ""
        self.FTE_icon = ui_elements.BackgruondLogo()
        self.settings_button = ui_elements.Button(
            ui_elements.load_transparent_img("img/settings.png", cfg.COLOR_GRAY1),
            (0, 0),
            4,
        )
        self.settings_button.set_callback(lambda: self.set_ork_file())
        # self.settings_message = ui_elements.UI_Text("Settings", "ZenKakuGothic", 3, cfg.COLOR_GRAY1, (4, 2), True)
        # self.settings_message.set_callback(lambda : print("Configurations"))

        self.oepn_file_text = ui_elements.UI_Text(
            "orkファイルを開く | Open ork File",
            "ZenKakuGothic",
            3.75,
            cfg.COLOR_BLACK,
            (50, 75),
            True,
            debug_collision_rect=True,
        )
        self.oepn_file_text.set_callback(open_ork_file)
        self.title = ui_elements.UI_Text(
            "From The Earth\nOpenRocket Visualizer",
            "oswald",
            7.5,
            cfg.COLOR_BLACK,
            (50, 20),
            True,
            0.85,
        )

        self.copyright = ui_elements.UI_Text(
            cfg.TEXT_COPYRIGHT, "oswald", 1.25, cfg.COLOR_GRAY1, (87.5, 97)
        )

    def set_ork_file(self):
        self.orkFile = open_ork_file()

    def exec(self, scene: pg.surface) -> None:
        """
        Execute the scene.
        """
        if self.orkFile:
            return SCENE_STATE.BRIEFING

        # fill the screen background
        scene.fill(cfg.COLOR_PALE_WHITE1)

        # update
        self.FTE_icon.update()
        self.settings_button.update()
        # self.settings_message.update()
        self.title.update()
        self.oepn_file_text.update()
        self.copyright.update()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                return SCENE_STATE.QUIT
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    return SCENE_STATE.QUIT
            self.settings_button.event_handler(event)
            self.oepn_file_text.event_handler(event)

        # draw
        self.FTE_icon.draw(scene)
        self.settings_button.draw(scene)
        # self.settings_message.draw(scene)
        self.oepn_file_text.draw(scene)
        self.title.draw(scene)

        self.copyright.draw(scene)

        pg.display.update()
        return SCENE_STATE.TOP


def open_ork_file():
    """Open file dialog and return the file name"""
    top = tkinter.Tk()
    top.withdraw()  # hide window
    file_name = tkinter.filedialog.askopenfilename(
        parent=top, filetypes=[("OpenRocket Files", "*.ork")]
    )
    top.destroy()
    # NOTE: Clear event queue to avoid double file open event occurred(ad hoc). That is why other event (e.g. QUIT) does not work.
    pg.event.clear()
    print(f"Open file: {file_name}")
    return file_name
