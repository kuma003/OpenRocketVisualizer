"""scenel.py"""
import pygame as pg
import numpy as np
from abc import ABCMeta, abstractmethod
import enum
from src.fonts import Fonts

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
        pg.init()
        info = pg.display.Info()
        screen_width, screen_height = info.current_w, info.current_h 

        # self.screen = pg.display.set_mode((screen_width, screen_height), pg.FULLSCREEN)
        self.screen = pg.display.set_mode((screen_width//2, screen_height//2))
        pg.display.set_caption("F.T.E. OpenRocket Flight Visualizer")
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

def load_transparent_img(filename: str, filled_color: pg.Color) -> pg.Surface:
    img = pg.image.load(filename).convert_alpha()

    img_arr = pg.surfarray.pixels3d(img)
    img_alpha = pg.surfarray.pixels_alpha(img)
    mask = img_alpha > 0
    img_arr[mask] = filled_color[:3]

    filled_img = pg.Surface(img.get_size(), pg.SRCALPHA)
    pg.surfarray.blit_array(filled_img, img_arr)

    # # アルファチャンネルを設定
    # alpha_arr = pg.surfarray.pixels_alpha(filled_img)
    # alpha_arr[mask] = img_alpha[mask]

    return filled_img

class Top:
    """
        Top scene of the game. This Scene is the first scene to be displayed when the game starts.
    """
    COLOR_BACKGROUND = pg.Color(0x0, 0xFC, 0xFF) # background color of the scene.
    COLOR_ICON  = pg.Color(0xD0, 0xD0, 0xD0) # color of the icon.
    # ICON_FTE = load_transparent_img("img/FTE.png", COLOR_ICON) # F.T.E. icon image.
    ICON_FTE = None
    COPYRIGHT_TEXT = Fonts.get_font("ZenMaruGothic", 15).render("@2024 From The Earth.", True, pg.Color(0xC0, 0xC0, 0xC0))
    
    def __init__(self) -> None:
        # self.ICON_FTE = fill_image()
        # fte_icon_arr = pg.surfarray.pixels3d(Top.ICON_FTE)
        # fte_icon_alpha = pg.surfarray.pixels_alpha(Top.ICON_FTE)
        # mask = fte_icon_alpha > 0
        # fte_icon_arr[mask] = self.COLOR_ICON[:3]
        
        # self.ICON_FTE = pg.Surface(Top.ICON_FTE.get_size(), pg.SRCALPHA)
        # pg.surfarray.blit_array(self.ICON_FTE, fte_icon_arr)
        # self.ICON_FTE = load_transparent_img("img/FTE.png", self.COLOR_ICON) 
        Top.ICON_FTE = load_transparent_img("img/FTE.png", self.COLOR_ICON)
        pass

    def exec(self, scene: pg.surface) -> None:
        """
            Execute the scene.
        """
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return SCENE_STATE.QUIT
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    return SCENE_STATE.QUIT
        
        screen_width, screen_height = scene.get_width(), scene.get_height()
        if screen_height > screen_width:
            fte_icon = pg.transform.scale(Top.ICON_FTE, (screen_width, screen_width))
        else:
            fte_icon = pg.transform.scale(Top.ICON_FTE, (screen_height, screen_height))
        
        scene.fill(Top.COLOR_BACKGROUND)
        scene.blit(fte_icon, (0 if screen_height > screen_width else (screen_width - screen_height)//2 ,
                              0 if screen_width > screen_height else (screen_height - screen_width)//2))
        scene.blit(self.COPYRIGHT_TEXT, (screen_width - self.COPYRIGHT_TEXT.get_width(), screen_height - self.COPYRIGHT_TEXT.get_height()))
        pg.display.update()
        return SCENE_STATE.TOP