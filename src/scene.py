"""scenel.py"""
import pygame as pg
import numpy as np
from abc import ABCMeta, abstractmethod
import enum
from src.fonts import Fonts
import src.ui_elements as ui_elements
import src.config as cfg

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



class Top:
    """
        Top scene of the game. This Scene is the first scene to be displayed when the game starts.
    """
    
    def __init__(self) -> None:
        self.FTE_icon = ui_elements.BackgruondLogo()
        self.settings_button = ui_elements.Button(ui_elements.load_transparent_img("img/settings.png", cfg.COLOR_GRAY1), (0, 0), 2.5)
        self.settings_button.set_callback(lambda : print("settings"))
        self.settings_message = ui_elements.UI_Text("Settings", "ZenMaruGothic", 2.5, cfg.COLOR_GRAY1, (2.5, 0))
        self.settings_message.set_callback(lambda : print("Configurations"))
        
        self.copyright = Fonts.get_font("ZenMaruGothic", 15).render(cfg.TEXT_COPYRIGHT, True, cfg.COLOR_GRAY1)
    
    
    def exec(self, scene: pg.surface) -> None:
        """
            Execute the scene.
        """
        
        screen_width, screen_height = scene.get_width(), scene.get_height()
        
        # fill the screen background
        scene.fill(cfg.COLOR_PALE_WHITE)
        
        # update
        self.FTE_icon.update()
        self.settings_button.update()
        self.settings_message.update()
        
        
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return SCENE_STATE.QUIT
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    return SCENE_STATE.QUIT
            self.settings_button.event_handler(event)
            self.settings_message.event_handler(event)
        
        # draw
        self.FTE_icon.draw(scene)
        self.settings_button.draw(scene)
        self.settings_message.draw(scene)
        
        scene.blit(self.copyright, (screen_width - self.copyright.get_width(), screen_height - self.copyright.get_height()))
        
        
        
        pg.display.update()
        return SCENE_STATE.TOP