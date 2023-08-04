import math
import pygame

from pygame import Surface, draw, Color
from pygame.font import Font
from pygame.rect import Rect
from gameoflife.colors import BLACK, GREY


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
        bgColor: Color,
    ) -> None:
        self.text = text
        self.x = x
        self.y = y
        self.currBgColor = bgColor
        self.bgColor = bgColor
        self.textColor = None
        self.hoverBgColor = None
        self.hoverTextColor = None
        self.border = True
        self.borderColor = BLACK
        self.cursor = pygame.SYSTEM_CURSOR_ARROW

    def getBackgroundColor(self) -> Color:
        return self.bgColor

    def getBorderColor(self) -> Color:
        return self.borderColor

    def getX(self) -> int:
        return self.x

    def getY(self) -> int:
        return self.y

    def getText(self) -> str:
        return self.text

    def setX(self, x: int) -> None:
        self.x = x

    def setY(self, y: int) -> None:
        self.y = y

    def setFont(self, font: Font) -> None:
        self.font = font

    def setBackgroundColor(self, bgColor: Color) -> None:
        self.bgColor = bgColor

    def setHoverBackgroundColor(self, bgColor: Color) -> None:
        self.hoverBgColor = bgColor

    def setBorder(self, border: bool) -> None:
        self.border = border

    def setBorderColor(self, color: Color):
        self.borderColor = color

    def setText(self, text: str) -> None:
        self.text = text

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
    ) -> None:
        super().__init__(text, x, y, bgColor)
        self.radius: float = radius

    def getRadius(self) -> float:
        return self.radius

    def setRadius(self, radius: float) -> None:
        self.radius = radius

    def draw(self, surface: Surface) -> None:
        draw.circle(surface, self.currBgColor, (self.x, self.y), self.radius, 0)
        if self.border:
            draw.circle(surface, self.borderColor, (self.x, self.y), self.radius, 1)
        if self.text:
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
        w: int,
        h: int,
        x: int = 0,
        y: int = 0,
        bgColor: Color = GREY,
    ) -> None:
        super().__init__(text, x, y, bgColor)
        self.h: int = h
        self.w: int = w
        self.rect: Rect = Rect(x, y, w, h)

    def getRect(self) -> Rect:
        return self.rect

    def getH(self) -> int:
        return self.h

    def setH(self, h: int) -> None:
        self.h = h
        self.rect.h = h

    def setW(self, w: int) -> None:
        self.w = w

    def setX(self, x: int) -> None:
        self.x = x
        self.rect.x = x

    def setY(self, y: int) -> None:
        self.y = y
        self.rect.y = y

    def draw(self, surface: Surface) -> None:
        draw.rect(surface, self.currBgColor, self.rect)
        textImg = self.font.render(self.text, True, (255, 255, 255))
        fontSize = self.font.size(self.text)
        textX = self.x + ((self.w / 2) - (fontSize[0] / 2))
        textY = self.y + ((self.h / 2) - (fontSize[1] / 2))
        surface.blit(textImg, (textX, textY))

    def clicked(self, mouseX: int, mouseY: int) -> bool:
        if (mouseX >= self.x and mouseX <= self.x + self.w) and (
            mouseY >= self.y and mouseY <= self.y + self.h
        ):
            return True
        return False

    def update(self) -> None:
        (mX, mY) = pygame.mouse.get_pos()
        if (mX >= self.x and mX <= self.x + self.w) and (
            mY >= self.y and mY <= self.y + self.h
        ):
            self.cursor = pygame.SYSTEM_CURSOR_HAND
            self.currBgColor = self.hoverBgColor
            pygame.mouse.set_cursor(self.cursor)
        else:
            if self.cursor != pygame.SYSTEM_CURSOR_ARROW:
                self.cursor = pygame.SYSTEM_CURSOR_ARROW
                pygame.mouse.set_cursor(self.cursor)
            if self.currBgColor != self.bgColor:
                self.currBgColor = self.bgColor
