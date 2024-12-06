import pygame as pg
import numpy as np
from abc import ABCMeta, abstractmethod
import enum

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
    COLOR_BACKGROUND = pg.Color(0xFA, 0xFC, 0xFF) # background color of the scene.
    COLOR_ICON  = pg.Color(0xD0, 0xD0, 0xD0) # color of the icon.
    ICON_FTE = pg.image.load( "img/FTE.png") # F.T.E. icon image.
    
    def __init__(self) -> None:
        fte_icon_arr = pg.surfarray.pixels3d(Top.ICON_FTE)
        fte_icon_alpha = pg.surfarray.pixels_alpha(Top.ICON_FTE)
        mask = fte_icon_alpha > 0
        fte_icon_arr[mask] = self.COLOR_ICON[:3]
        
        self.ICON_FTE = pg.Surface(Top.ICON_FTE.get_size(), pg.SRCALPHA)
        pg.surfarray.blit_array(self.ICON_FTE, fte_icon_arr)
            
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
        pg.display.update()
        return SCENE_STATE.TOP