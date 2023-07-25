
import pygame

from gameoflife.colors import BLACK
from pygame import draw
from pygame.surface import Surface

def drawRectBorder(screen:Surface, x:int, y:int, w:int, h:int, color=BLACK) -> None:
    draw.line(screen, color, (x, y), (x + w, y)) # top
    draw.line(screen, color, (x, y), (x, y + h))
    draw.line(screen, color, (x + w, y), (x + w, y + h))
    draw.line(screen, color, (x, y + h), (x + w, y + h))