import math
import pygame

from pygame import Surface, draw
from pygame.font import Font
from pygame.rect import Rect
from gameoflife.colors import BLACK, GREY
from typing import Tuple, Optional


class BaseButton:
    def __init__(self, text:str, font:Font, x:int, y:int, w:int, bgColor:Tuple[int, int, int, Optional[float]]) -> None:
        self.text = text
        self.font = font
        self.x = x
        self.y = y
        self.w = w
        self.bgColor = bgColor
        self.border = True
        self.borderColor = BLACK

    def setX(self, x:int) -> None:
        self.x = x

    def setY(self, y:int) -> None:
        self.y = y

    def setW(self, w:int) -> None:
        self.w = w

    def setFont(self, font:Font) -> None:
        self.font = font

    def setBackgroundColor(self, bgColor:tuple) -> None:
        self.bgColor = bgColor

    def setBorder(self, border:bool) -> None:
        self.border = border

    def setBorderColor(self, color:Tuple[int, int, int, Optional[float]]):
        pass

    def setText(self, text:str) -> None:
        self.text = text

    def draw(self, screen:Surface):
        raise NotImplementedError("draw() not implemented!")

    def clicked(self, mouseX:int, mouseY:int) -> bool:
        raise NotImplementedError("clicked() not implemented!")


class RectButton(BaseButton):
    def __init__(self, text:str, font:Font, x:int, y:int, w:int, h:int, bgColor:Tuple[int, int, int, Optional[float]]=GREY) -> None:
        super().__init__(text, font, x, y, w, bgColor)
        self.h:int = h
        self.rect:Rect = Rect(x, y, w, h)

    def setH(self, h:int) -> None:
        self.h = h

    def draw(self, surface:Surface) -> None:
        draw.rect(surface, self.bgColor, self.rect)
        textImg = self.font.render(self.text, True, (255, 255, 255))
        fontSize = self.font.size(self.text)
        textX = self.x + ((self.w / 2) - (fontSize[0] / 2))
        textY = self.y + ((self.h / 2) - (fontSize[1] / 2))
        surface.blit(textImg, (textX, textY))

    def clicked(self, mouseX:int, mouseY:int) -> bool:
        if ((mouseX >= self.x and mouseX <=self.x + self.w) and
            (mouseY >= self.y and mouseY <= self.y + self.h)):
            return True
        return False


class CircleButton(BaseButton):
    def __init__(self, text: str, font: Font, x: int, y: int, radius:float, bgColor: Tuple[int, int, int, Optional[float]]=GREY) -> None:
        super().__init__(text, font, x, y, 0, bgColor)
        self.radius:float = radius

    def getRadius(self) -> float:
        return self.radius

    def setRadius(self, radius:float) -> None:
        self.radius = radius

    def draw(self, surface:Surface) -> None:
        draw.circle(surface, self.bgColor, (self.x, self.y), self.radius, self.w)
        if self.border:
            draw.circle(surface, self.borderColor, (self.x, self.y), self.radius, 1)

    def clicked(self, mouseX:int, mouseY:int) -> bool:
        sqMouseX = (mouseX - self.x) ** 2
        sqMouseY = (mouseY - self.y) ** 2
        if math.sqrt(sqMouseX + sqMouseY) < self.radius:
            return True
        return False
