import pygame as pg
import orhelper
import src.scene as scene

# class AppMain:
#     def __init__(self) -> None:
#         pg.init()
#         info = pg.display.Info()
#         screen_width, screen_height = info.current_w, info.current_h 

#         # self.screen = pg.display.set_mode((screen_width, screen_height), pg.FULLSCREEN)
#         self.screen = pg.display.set_mode((screen_width//2, screen_height//2))

#     def update(self) -> None:
#         pass # 空実装
    
#     def draw(self) -> None:
#         self.screen.fill(pg.Color("blue"))
#         pg.display.update()
    
    
#     def run(self) -> None:
#         clock = pg.time.Clock()
        
#         while True:
#             # main loop
#             fps = 60
#             clock.tick(fps)
            
#             should_quit = False
            
#             for event in pg.event.get():
#                 if event.type == pg.QUIT:
#                     should_quit = True
#                 if event.type == pg.KEYDOWN:
#                     if event.key == pg.K_ESCAPE:
#                         should_quit = True
            
#             if should_quit:
#                 break
#             self.update()
#             self.draw()

if __name__ == "__main__":
    app = scene.AppMain()
    app.run()
    
    

# pygame.init()
# screen = pygame.display.set_mode((600, 400))

# while True:
#     pygame.event.clear()
#     key_pressed = pygame.key.get_pressed()
#     if key_pressed[pygame.K_ESCAPE]:
#         break

#     pygame.draw.circle(screen, pygame.Color("red"), (300, 200), 30)
#     pygame.display.update()

# pygame.quit()
# import os
# import math
# import numpy as np
# from scipy.optimize import fmin
# from matplotlib import pyplot as plt
# import pprint

# import orhelper
# from orhelper import *

# with orhelper.OpenRocketInstance() as instance:
#     orh = orhelper.Helper(instance)

#     # read file
#     doc = orh.load_doc('simple.ork')
#     sim = doc.getSimulation(0)   
#     opts = sim.getOptions()
#     rocket = opts.getRocket()
    
#     fin = orh.get_component_named(rocket, "Trapezoidal fin set")
#     print(fin.getName())
    
    
#     for component in JIterator(rocket):
#         pprint.pprint(component.__class__)

# # Leave OpenRocketInstance context before showing plot in order to shutdown JVM first
# plt.show()