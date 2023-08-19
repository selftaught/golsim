import asyncio
import pygame
from gameoflife.game import Game

asyncio.run(Game().loop())
pygame.quit()
