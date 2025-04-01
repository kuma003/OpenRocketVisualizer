"""scenel.py"""

import enum
from pathlib import Path

import numpy as np
import pygame as pg

import visualizer.config as cfg
import visualizer.ui_elements as ui_elements
from visualizer.dialogs import ask_whether_to_exit, open_ork_file
from visualizer.fonts import Fonts
from visualizer.rocket import *

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
        self.briefing = Briefing()

        self.scene_flag = SCENE_STATE.TOP

    def run(self) -> None:
        clock = pg.time.Clock()

        fps = 60
        clock.tick(fps)
        while True:
            # main loop
            match self.scene_flag:
                case SCENE_STATE.TOP:
                    self.scene_flag = self.top.exec(self.screen)
                    if (
                        self.scene_flag == SCENE_STATE.BRIEFING
                    ):  # if the scene is changed to BRIEFING, run the simulation
                        self.briefing.run_simulation(self.top.ork_file)
                case SCENE_STATE.BRIEFING:
                    self.scene_flag = self.briefing.exec(self.screen)
                case SCENE_STATE.GAME:
                    self.scene_flag = self.game.exec(self.screen)
                case SCENE_STATE.QUIT:
                    break
                case _:
                    break
        pg.quit()


class Top:
    """
    Top scene of the game. This Scene is the first scene to be displayed when the game starts.
    """

    def __init__(self) -> None:
        self.ork_file: Path = Path("")
        self.state: SCENE_STATE = SCENE_STATE.TOP

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
        self.oepn_file_text.set_callback(lambda: self.set_ork_file())
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
        self.ork_file = Path(open_ork_file())
        if self.ork_file.exists() and self.ork_file.suffix == ".ork":
            print(f"Open file: {self.ork_file}")
            self.state = SCENE_STATE.BRIEFING  # next scene

    def exec(self, scene: pg.surface) -> None:
        """
        Execute the scene.
        """

        for event in pg.event.get():
            if event.type == pg.QUIT:
                if ask_whether_to_exit():
                    self.state = SCENE_STATE.EXIT
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    if ask_whether_to_exit():
                        self.state = SCENE_STATE.EXIT
            self.settings_button.event_handler(event=event)
            self.oepn_file_text.event_handler(event)

        # fill the screen background
        scene.fill(cfg.COLOR_PALE_WHITE1)

        # update
        self.FTE_icon.update()
        self.settings_button.update()
        # self.settings_message.update()
        self.title.update()
        self.oepn_file_text.update()
        self.copyright.update()

        # draw
        self.FTE_icon.draw(scene)
        self.settings_button.draw(scene)
        # self.settings_message.draw(scene)
        self.oepn_file_text.draw(scene)
        self.title.draw(scene)

        self.copyright.draw(scene)

        pg.display.update()
        return self.state


class Briefing:

    def __init__(self) -> None:
        self.state: SCENE_STATE = SCENE_STATE.BRIEFING
        self.rocket = None

    def run_simulation(self, ork_file: os.PathLike):
        """
        Set the ork file data and run simulaition.

        Args:
            ork_file (os.PathLike): path to the ork file.
        """
        self.rocket = Rocket(ork_file)
        self.rocket.run_simulation()

    def exec(self, scene: pg.surface) -> None:
        """
        Execute the scene.
        """

        for event in pg.event.get():
            if event.type == pg.QUIT:
                if ask_whether_to_exit():
                    self.state = SCENE_STATE.EXIT
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    if ask_whether_to_exit():
                        self.state = SCENE_STATE.EXIT

        # fill the screen background
        scene.fill(cfg.COLOR_PALE_WHITE1)

        self.rocket.update()
        self.rocket.draw(scene)

        # pg.draw.polygon(
        #     scene,
        #     cfg.COLOR_PALE_GRAY,
        #     np.array(
        #         [
        #             np.array([0, 0]),
        #             np.array([0, 100]),
        #             np.array([100, 200]),
        #             np.array([100, 0]),
        #         ]
        #     ),
        # )

        pg.display.update()
        return self.state
