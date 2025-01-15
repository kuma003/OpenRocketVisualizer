import pygame as pg
import orhelper
import src.scene as scene

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
