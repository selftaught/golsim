import pygame

from gameoflife.colors import BLACK
from pygame import draw
from pygame.surface import Surface


def drawRectBorder(
    screen: Surface, x: int, y: int, w: int, h: int, color=BLACK
) -> None:
<<<<<<< Updated upstream
    draw.line(screen, color, (x, y), (x + w, y))  # top
    draw.line(screen, color, (x, y), (x, y + h))
    draw.line(screen, color, (x + w, y), (x + w, y + h))
    draw.line(screen, color, (x, y + h), (x + w, y + h))
=======
    draw.line(screen, color, (r.x, r.y), (r.x + r.w, r.y))
    draw.line(screen, color, (r.x, r.y), (r.x, r.y + r.h))
    draw.line(screen, color, (r.x + r.w, r.y), (r.x + r.w, r.y + r.h))
    draw.line(screen, color, (r.x, r.y + r.h), (r.x + r.w, r.y + r.h))
<<<<<<< Updated upstream
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
