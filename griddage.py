# Jan Tabaczynski
# January 1, 2016
# Griddage Game
# griddage.py

'''This script allows two players to take turns at a game of Griddage.'''

import sys, pygame
pygame.init()

size = width, height = 1080, 960

screen = pygame.display.set_mode(size)

for event in pygame.event.get():
    if event.type == pygame.quit(): sys.exit()
