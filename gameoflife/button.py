import math
import pygame

from gameoflife.colors import BLACK, GREY
from gameoflife.helpers import drawRectBorder

from pygame import Surface, draw, Color
from pygame.font import Font
from pygame.rect import Rect

from typing import Union


class ButtonID:
    CLEAR = "Clear"
    EXIT = "Exit"
    NEXT = "Next"
    RESET = "Reset"
    START = "Start"
    STOP = "Stop"
    PATTERNS = "Patterns"
    DRAW = "Draw"
    PAN = "Pan"


class BaseButton:
    def __init__(
        self,
        id: str,
        x: int,
        y: int,
        bgColor: Color = GREY,
        border: bool = True,
        borderColor: Color = BLACK,
    ) -> None:
        self._id = id
        self._x = x
        self._y = y
        self._currBgColor = bgColor
        self._bgColor = bgColor
        self._hoverBgColor = bgColor
        self._hoverTextColor = None
        self._border = True
        self._borderColor = BLACK
        self._cursor = pygame.SYSTEM_CURSOR_ARROW

    def getBackgroundColor(self) -> Color:
        return self._bgColor

    def getBorderColor(self) -> Color:
        return self._borderColor

    def getHoverBackgroundColor(self) -> Color:
        return self._hoverBgColor

    def getX(self) -> int:
        return self._x

    def getY(self) -> int:
        return self._y

    def getId(self) -> str:
        return self._id

    def setX(self, x: int) -> None:
        self._x = x

    def setY(self, y: int) -> None:
        self._y = y

    def setFont(self, font: Font) -> None:
        self._font = font

    def setBackgroundColor(self, bgColor: Color) -> None:
        self._bgColor = bgColor

    def setHoverBackgroundColor(self, bgColor: Color) -> None:
        self._hoverBgColor = bgColor

    def setBorder(self, border: bool) -> None:
        self._border = border

    def setBorderColor(self, color: Color):
        self._borderColor = color

    def setId(self, id: str) -> None:
        self._id = id

    def draw(self, screen: Surface):
        raise NotImplementedError("button draw() not implemented!")

    def clicked(self, mouseX: int, mouseY: int) -> bool:
        raise NotImplementedError("button clicked() not implemented!")

    def update(self) -> None:
        raise NotImplementedError("button update() not implemented!")

class CircleButton(BaseButton):
    def __init__(
        self,
        id: str,
        x: int,
        y: int,
        radius: float,
        bgColor: Color = GREY,
        border: bool = True,
        borderColor: Color = BLACK
    ) -> None:
        super().__init__(id, x, y, bgColor, border, borderColor)
        self._radius: float = radius

    def getRadius(self) -> float:
        return self._radius

    def setRadius(self, radius: float) -> None:
        self._radius = radius

    def draw(self, surface: Surface) -> None:
        draw.circle(surface, self._currBgColor, (self._x, self._y), self._radius, 0)
        if self._border:
            draw.circle(surface, self._borderColor, (self._x, self._y), self._radius, 1)
        textImg = self._font.render(self._id, True, BLACK)
        fontSize = self._font.size(self._id)
        textX = self._x - int(fontSize[0] / 2)
        textY = self._y - int(fontSize[1] / 2) + 1
        surface.blit(textImg, (textX, textY))

    def clicked(self, mouseX: int, mouseY: int) -> bool:
        sqMouseX = (mouseX - self._x) ** 2
        sqMouseY = (mouseY - self._y) ** 2
        if math.sqrt(sqMouseX + sqMouseY) < self._radius:
            return True
        return False

    def update(self) -> None:
        (mX, mY) = pygame.mouse.get_pos()
        sqMouseX = (mX - self._x) ** 2
        sqMouseY = (mY - self._y) ** 2
        if math.sqrt(sqMouseX + sqMouseY) < self._radius:
            self._cursor = pygame.SYSTEM_CURSOR_HAND
            pygame.mouse.set_cursor(self._cursor)
            self._currBgColor = self._hoverBgColor
        else:
            if self._cursor != pygame.SYSTEM_CURSOR_ARROW:
                self._cursor = pygame.SYSTEM_CURSOR_ARROW
                pygame.mouse.set_cursor(self._cursor)
            if self._currBgColor != self._bgColor:
                self._currBgColor = self._bgColor

class RectButton(BaseButton):
    def __init__(
        self,
        id: str,
        rect:Rect = Rect(0, 0, 0, 0),
        bgColor: Color = GREY,
        border: bool = True,
        borderColor: Color = BLACK,
        imagePath:str = None
    ) -> None:
        super().__init__(id, rect.x, rect.y, bgColor, border, borderColor)
        self._rect = rect
        self._currBgColor = bgColor
        self._surface = None
        if imagePath:
            self._surface = pygame.transform.scale(pygame.image.load(imagePath), (rect.width, rect.height))

    def getRect(self) -> Rect:
        return self._rect

    def getH(self) -> int:
        return self._rect.height

    def getW(self) -> int:
        return self._rect.width

    def getX(self) -> int:
        return self._rect.x

    def getY(self) -> int:
        return self._rect.y

    def setRect(self, rect: Rect):
        self._rect = rect

    def setW(self, width:int) -> None:
        self._rect.width = width

    def setH(self, height:int) -> None:
        self._rect.height = height

    def draw(self, surface: Surface) -> None:
        draw.rect(surface, self._currBgColor, self._rect)
        if self._surface:
            surface.blit(self._surface, (self._x, self._y))
        else:
            textImg = self._font.render(self._id, True, (255, 255, 255))
            fontSize = self._font.size(self._id)
            textX = self._rect.x + ((self._rect.width / 2) - (fontSize[0] / 2))
            textY = self._rect.y + ((self._rect.height / 2) - (fontSize[1] / 2))
            surface.blit(textImg, (textX, textY))
        if self._border:
            drawRectBorder(surface, self._rect, self._borderColor)

    def clicked(self, mouseX:Union[None, int]=None, mouseY:Union[None, int]=None) -> bool:
        if not mouseX or not mouseY:
            (mouseX, mouseY) = pygame.mouse.get_pos()
        if self._rect.collidepoint((mouseX, mouseY)):
            return True
        return False

    def update(self) -> None:
        if self._rect.collidepoint(pygame.mouse.get_pos()):
            self._cursor = pygame.SYSTEM_CURSOR_HAND
            self._currBgColor = self._hoverBgColor
            pygame.mouse.set_cursor(self._cursor)
        else:
            if self._cursor != pygame.SYSTEM_CURSOR_ARROW:
                self._cursor = pygame.SYSTEM_CURSOR_ARROW
                pygame.mouse.set_cursor(self._cursor)
            if self._currBgColor != self._bgColor:
                self._currBgColor = self._bgColor
