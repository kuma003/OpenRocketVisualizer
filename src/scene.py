import pygame as pg
from abc import ABCMeta, abstractmethod

class AppMain:
    def __init__(self) -> None:
        pg.init()
        info = pg.display.Info()
        screen_width, screen_height = info.current_w, info.current_h 

        # self.screen = pg.display.set_mode((screen_width, screen_height), pg.FULLSCREEN)
        self.screen = pg.display.set_mode((screen_width//2, screen_height//2))
        
        self.scenes : list[Scene] = []
        self.sceneIds : list[int] = []
    
    def register_scene(self, scene: Scene):
        self.scenes.append(Scene)
        self.sceneIds.append(len(self.scenes) - 1)
        return self.sceneIds[-1]
    
    def switch_scene(self, id : int):
        self.scenes[id].enable = True;
        
    
    

class Scene(metaclass = ABCMeta):
    def __init__(self, enable=False) -> None:
        self.enable = False
        self.nextId
    
    # def update(self) -> None:
    #     """
    #         Update function that is called every frame unless `self.enable` is set to True.
            
    #         This function is not intended to be overriden by subclass. Custom behavior should  
    #         be implemented in the `_update` function instead.
    #     """
    #     if self.enable:
    #         self._update()
    
    # def _update(self) -> None:
    #     """
    #         Custom behavior function called as part of the update process.

    #         Subclasses can override this method to implement specific behavior that  
    #         should occur during each frame update. This function is called only when  
    #         `self.enable` is set to True.
            
    #         Note: 
    #             - `_update` is designed for subclass-specific logic and should not call 
    #             the parent class's `update` method directly.
    #     """
    #     pass
    
    # def draw(self, screen : pg.Surface) -> None:
    #     """
    #         Drawing function that is called every frame unless `self.enable` is set to True.
            
    #         This function is not intended to be overriden by subclass. Custom behavior should  
    #         be implemented in the `_draw` function instead.
            
    #         Args:
    #             - screen : A Pygame surface used for rendering graphics.
    #     """
    #     if self.enable:
    #         self._draw(scene=screen)
    
    # @abstractmethod
    # def _draw(self, scene) -> None:
    #     """
    #         Custom behavior function called as part of the drawing process.

    #         Subclasses can override this method to implement specific behavior that  
    #         should occur during each frame update. This function is called only when  
    #         `self.enable` is set to True.
            
    #         Note: 
    #             - `_draw` is designed for subclass-specific logic and should not call 
    #             the parent class's `draw` method directly.
    #     """
        pass

class Top(Scene):
    def __init__(self):
        
