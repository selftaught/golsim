from pygame import draw, Rect
from pygame.freetype import SysFont
from pygame.surface import Surface
from typing import Tuple

from gameoflife.draw import drawRectBorder


# TODO: dynamic mode - detect boundaries and change position accordingly
# TODO: static mode - static position on a specified side
# TODO: theme - allow for additional styling parameters
class Tooltip:
    def __init__(self, text:str, font:SysFont, elePos:Tuple[int, int], bgColor:Tuple[int, int, int], padding:int=5) -> None:
        self._bgColor:Tuple[int, int, int] = bgColor
        self._elePos:Tuple[int, int] = elePos
        self._enabled:bool = False
        self._font:SysFont = font
        self._padding:int = padding
        self._text:str = text

    def draw(self, surface:Surface) -> None:
        if self._enabled:
            fontRect = self._font.get_rect(self._text)
            (x, y) = (self._elePos[0], self._elePos[1] - fontRect.height - 15)
            rect = Rect(x, y, fontRect.width + (self._padding * 2), fontRect.height + (self._padding * 2))
            draw.rect(surface, self._bgColor, rect)
            self._font.render_to(surface, (x + self._padding, y + self._padding), self._text)
            drawRectBorder(surface, rect)

    def setFont(self, font:SysFont) -> None:
        self._font = font

    def disable(self) -> None:
        self._enabled = False

    def enable(self) -> None:
        self._enabled = True
