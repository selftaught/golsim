import pygame

from gameoflife.colors import BLACK
from pygame import draw, Rect
from pygame.surface import Surface
from typing import Tuple, List


def drawRectBorder(
    screen: Surface, r:Rect, color=BLACK
) -> None:
    draw.line(screen, color, (r.x, r.y), (r.x + r.w, r.y))
    draw.line(screen, color, (r.x, r.y), (r.x, r.y + r.h))
    draw.line(screen, color, (r.x + r.w, r.y), (r.x + r.w, r.y + r.h))
    draw.line(screen, color, (r.x, r.y + r.h), (r.x + r.w, r.y + r.h))
