import pygame as pg
import numpy as np
from src.fonts import Fonts
import src.config as cfg

def load_transparent_img(filename: str, filled_color: pg.Color) -> pg.Surface:
    '''
        Load image file with transparent background and fill the untransparent part with filled_color.  
        
        Args:
            filename (str): image file name.
            filled_color (pg.Color): color to fill the transparent part.
        Returns:
            pg.Surface: image with filled untransparent part
    '''
    img = pg.image.load(filename).convert_alpha()

    img_arr = pg.surfarray.pixels3d(img)
    img_alpha = pg.surfarray.pixels_alpha(img)
    mask = img_alpha > 0 # mask of untransparent part
    img_arr[mask] = filled_color[:3]
    
    # create img with filled color
    filled_img = pg.Surface(img.get_size(), pg.SRCALPHA)
    pg.surfarray.blit_array(filled_img, img_arr)

    # set alpha value
    alpha_arr = pg.surfarray.pixels_alpha(filled_img)
    alpha_arr[~mask] = 0

    return filled_img

class BackgruondLogo():
    '''Background F.T.E. logo image'''
    def __init__(self):
        super().__init__()
        self.row_image = load_transparent_img("img/FTE.png", cfg.COLOR_PALE_GRAY)
        self.image = None
        self.window_size = None
        self.blit_dest = None
    
    def update(self) -> None:
        '''Update image size'''
        if self.window_size != pg.display.get_window_size():
            self.window_size = pg.display.get_window_size()
            self.row_image = pg.transform.scale(self.row_image, self.window_size)
            if self.window_size[1] > self.window_size[0]:
                self.image = pg.transform.scale(self.row_image, (self.window_size[0], self.window_size[0]))
                self.blit_dest = (0, (self.window_size[1] - self.window_size[0])//2)
            else:
                self.image = pg.transform.scale(self.row_image, (self.window_size[1], self.window_size[1]))
                self.blit_dest = ((self.window_size[0] - self.window_size[1])//2, 0)
    def draw(self, screen: pg.Surface) -> None:
        '''Draw image on screen'''
        screen.blit(self.image, self.blit_dest)   


class Button(pg.sprite.Sprite):
    def __init__(self, image : pg.Surface, pos: tuple[float, float], size: float, debug_collision_rect: bool = False) -> None:
        '''
        Button class

        Args:
            image (pg.Surface): The image to be used for the button.
            pos (tuple[float, float]): The position of the button as a percentage of the window size.
            size (float): The size of the button as a percentage of the window width.
            debug_collision_rect (bool): Whether to draw the collision rect for debugging.
        '''
        super().__init__()
        self.raw_image: pg.Surface        = image
        self.image: pg.Surface            = image
        self.size: float                  = size / 100
        self.pos: tuple[float, float]     = [pos[0]/100, pos[1]/100]
        self.window_size: tuple[int, int] = None
        self.rect: pg.Rect                = None
        self.on_click: callable           = lambda: None
        self.debug_collision_rect         = debug_collision_rect
    
    def set_callback(self, callback) -> None:
        '''Set the function to be called when the button is clicked'''
        self.on_click = callback
    
    def update(self) -> None:
        '''Update the button size and position based on the current window size'''
        if self.window_size != pg.display.get_window_size():
            self.window_size = pg.display.get_window_size()
            # Update the button size and position based on the current window size
            size = [int(self.window_size[0] * self.size), int(self.window_size[0] * self.size)]
            pos = [int(self.window_size[0] * self.pos[0]), int(self.window_size[1] * self.pos[1])]
            self.rect = pg.Rect(pos[0], pos[1], size[0], size[1])
            self.image = pg.transform.scale(self.raw_image, size)
    
    def event_handler(self, event: pg.event.Event) -> None:
        '''Handle the mouse click event'''
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.on_click()

    def draw(self, screen: pg.Surface) -> None:
        '''Draw the button on the screen'''
        if self.debug_collision_rect:
            pg.draw.rect(screen, pg.Color("red"), self.rect, 2)
        screen.blit(self.image, self.rect)

class UI_Text(pg.sprite.Sprite):
    def __init__(self, text: str, font_name: str, font_size: float, font_color: pg.Color, pos: tuple[float, float], centering: bool = False, line_height: float = 1.0, debug_collision_rect: bool = False) -> None:
        '''
        UI Text class

        Args:
            text (str): The text to be displayed.
            font_name (str): The name of the font to be used.
            font_size (float): The size of the font as a percentage of the window width.
            font_color (pg.Color): The color of the font.
            pos (tuple[float, float]): The position of the text as a percentage of the window size.
            centering (bool): Whether to center the text.
            line_height (float): The height of each line.
            debug_collision_rect (bool): Whether to draw the collision rect for debugging.
        '''
        super().__init__()
        self.rendered_text: list[pg.Surface] = None
        self.text: str                       = text
        self.font_name: str                  = font_name
        self.font_color: pg.Color            = font_color
        self.pos: tuple[float, float]        = [pos[0]/100, pos[1]/100]
        self.window_size: tuple[int, int]    = None
        self.image: pg.Surface               = None
        self.rects: list[pg.Rect]            = None
        self.font_size: float                = font_size / 100
        self.on_click: callable              = lambda: None
        self.centering: bool                 = centering
        self.line_height: float              = line_height
        self.debug_collision_rect: bool      = debug_collision_rect
    
    def set_callback(self, callback) -> None:
        '''Set the function to be called when the text is clicked'''
        self.on_click = callback
    
    def set_text(self, text: str) -> None:
        '''Set the text to be displayed'''
        self.text = text
        self.update() # update the text size and position
    
    def update(self) -> None:
        '''Update the text size and position based on the current window size'''
        if self.window_size != pg.display.get_window_size():
            self.window_size = pg.display.get_window_size()
            font_size = int(self.window_size[0] * self.font_size)
            pos = [int(self.window_size[0] * self.pos[0]), int(self.window_size[1] * self.pos[1])]
            font =  Fonts.get_font(self.font_name, font_size)
            self.rendered_text = [font.render(line, True, self.font_color) for line in self.text.split("\n")] # list of rendered text lines
            ascent = font.get_ascent() # length of the text above the baseline
            descent = font.get_descent() # length of the text below the baseline
            height = font.get_height() # total height of the text
            linesize = font.get_linesize() # height of a line of text
            
            self.rects = [pg.Rect(pos[0], pos[1] + i * linesize * self.line_height, text.get_width(), linesize) for i, text in enumerate(self.rendered_text)]
            if self.centering:
                for rect in self.rects:
                    rect.x -= rect.width // 2
    
    def event_handler(self, event: pg.event.Event) -> None:
        if event.type == pg.MOUSEBUTTONDOWN:
            for rect in self.rects:
                if rect.collidepoint(event.pos):
                    self.on_click()
    
    def draw(self, screen: pg.Surface) -> None:
        '''Draw the text on the screen'''
        if self.debug_collision_rect:
            for rect in self.rects:
                pg.draw.rect(screen, pg.Color("red"), rect, 2)
        for text, rect in zip(self.rendered_text, self.rects):
            screen.blit(text, rect)