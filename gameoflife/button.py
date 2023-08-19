import math
import pygame

from gameoflife.colors import BLACK, GREY
from gameoflife.helpers import drawRectBorder

from pygame import Surface, draw, Color
from pygame.font import Font
from pygame.rect import Rect

from typing import Union


class ButtonText:
    CLEAR = "Clear"
    EXIT = "Exit"
    NEXT = "Next"
    RESET = "Reset"
    START = "Start"
    STOP = "Stop"
    PATTERNS = "Patterns"


class BaseButton:
    def __init__(
        self,
        text: str,
        x: int,
        y: int,
        bgColor: Color = GREY,
        border: bool = True,
        borderColor: Color = BLACK,
    ) -> None:
        self.text = text
        self.x = x
        self.y = y
        self.w = w
        self.currBgColor = bgColor
        self.bgColor = bgColor
        self.textColor = None
        self.hoverBgColor = bgColor
        self.hoverTextColor = None
        self.border = True
        self.borderColor = BLACK
        self.cursor = pygame.SYSTEM_CURSOR_ARROW

    def getText(self) -> str:
        return self.text

    def setX(self, x: int) -> None:
        self.x = x

    def setY(self, y: int) -> None:
        self.y = y

    def setW(self, w: int) -> None:
        self.w = w

    def setFont(self, font: Font) -> None:
        self.font = font

    def setBackgroundColor(self, bgColor: Color) -> None:
        self.bgColor = bgColor

    def setHoverBackgroundColor(self, bgColor: Color) -> None:
        self.hoverBgColor = bgColor

    def setBorder(self, border: bool) -> None:
        self.border = border

    def setBorderColor(self, color: Color):
        pass

    def setText(self, text: str) -> None:
        self.text = text
        self.id = text

    def draw(self, screen: Surface):
        raise NotImplementedError("button draw() not implemented!")

    def clicked(self, mouseX: int, mouseY: int) -> bool:
        raise NotImplementedError("button clicked() not implemented!")

    def update(self) -> None:
        raise NotImplementedError("button update() not implemented!")


class CircleButton(BaseButton):
    def __init__(
        self,
        text: str,
        x: int,
        y: int,
        radius: float,
        bgColor: Color = GREY,
        border: bool = True,
        borderColor: Color = BLACK,
    ) -> None:
        super().__init__(text, x, y, 0, bgColor)
        self.radius: float = radius

    def getRadius(self) -> float:
        return self.radius

    def setRadius(self, radius: float) -> None:
        self.radius = radius

    def draw(self, surface: Surface) -> None:
        draw.circle(surface, self.currBgColor, (self.x, self.y), self.radius, self.w)
        if self.border:
            draw.circle(surface, self.borderColor, (self.x, self.y), self.radius, 1)
        if self.text:
            textLen = len(self.text)
            textImg = self.font.render(self.text, True, BLACK)
            fontSize = self.font.size(self.text)
            textX = self.x - int(fontSize[0] / 2)
            textY = self.y - int(fontSize[1] / 2) + 1
            surface.blit(textImg, (textX, textY))

    def clicked(self, mouseX: int, mouseY: int) -> bool:
        sqMouseX = (mouseX - self.x) ** 2
        sqMouseY = (mouseY - self.y) ** 2
        if math.sqrt(sqMouseX + sqMouseY) < self.radius:
            return True
        return False

    def update(self) -> None:
        (mX, mY) = pygame.mouse.get_pos()
        sqMouseX = (mX - self.x) ** 2
        sqMouseY = (mY - self.y) ** 2
        if math.sqrt(sqMouseX + sqMouseY) < self.radius:
            self.cursor = pygame.SYSTEM_CURSOR_HAND
            pygame.mouse.set_cursor(self.cursor)
            self.currBgColor = self.hoverBgColor
        else:
            if self.cursor != pygame.SYSTEM_CURSOR_ARROW:
                self.cursor = pygame.SYSTEM_CURSOR_ARROW
                pygame.mouse.set_cursor(self.cursor)
            if self.currBgColor != self.bgColor:
                self.currBgColor = self.bgColor


class RectButton(BaseButton):
    def __init__(
        self,
        text: str,
        rect:Rect = Rect(0, 0, 0, 0),
        bgColor: Color = GREY,
        border: bool = True,
        borderColor: Color = BLACK,
    ) -> None:
        super().__init__(text, rect.x, rect.y, bgColor, border, borderColor)
        self._rect = rect
        self.currBgColor = bgColor

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
        draw.rect(surface, self.currBgColor, self._rect)
        textImg = self.font.render(self.text, True, (255, 255, 255))
        fontSize = self.font.size(self.text)
        textX = self._rect.x + ((self._rect.width / 2) - (fontSize[0] / 2))
        textY = self._rect.y + ((self._rect.height / 2) - (fontSize[1] / 2))
        surface.blit(textImg, (textX, textY))
        if self.border:
            drawRectBorder(surface, self._rect, self.borderColor)

    def clicked(self, mouseX: int, mouseY: int) -> bool:
        if self._rect.collidepoint((mouseX, mouseY)):
            return True
        return False

    def update(self) -> None:
        if self._rect.collidepoint(pygame.mouse.get_pos()):
            self.cursor = pygame.SYSTEM_CURSOR_HAND
            self.currBgColor = self.hoverBgColor
            pygame.mouse.set_cursor(self.cursor)
        else:
            if self.cursor != pygame.SYSTEM_CURSOR_ARROW:
                self.cursor = pygame.SYSTEM_CURSOR_ARROW
                pygame.mouse.set_cursor(self.cursor)
            if self.currBgColor != self.bgColor:
                self.currBgColor = self.bgColor
