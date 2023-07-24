import pygame
from pygame import Surface, draw
from pygame.font import Font
from pygame.rect import Rect
from gameoflife.colors import BLACK, GREY
from typing import Tuple

class Button:
    def __init__(self, text:str, font:Font, x:int, y:int, w:int, h:int) -> None:
        self.x:int = x
        self.y:int = y
        self.w:int = w
        self.h:int = h
        self.text:str = text
        self.font:Font = font
        self.rect:Rect = Rect(x, y, w, h)
        self.bgColor = GREY

    def setX(self, x:int) -> None:
        self.x = x

    def setY(self, y:int) -> None:
        self.y = y

    def setW(self, w:int) -> None:
        self.w = w

    def setH(self, h:int) -> None:
        self.h = h

    def setFont(self, font:Font) -> None:
        self.font = font

    def setBackgroundColor(self, bgColor:tuple) -> None:
        self.bgColor = bgColor

    def setText(self, text:str) -> None:
        self.text = text

    def draw(self, screen:Surface) -> None:
        draw.rect(screen, self.bgColor, self.rect)
        textImg = self.font.render(self.text, True, (255, 255, 255))
        fontSize = self.font.size(self.text)
        textX = self.x + ((self.w / 2) - (fontSize[0] / 2))
        textY = self.y + ((self.h / 2) - (fontSize[1] / 2))
        screen.blit(textImg, (textX, textY))

    def clicked(self, mouseX:int, mouseY:int) -> bool:
        if ((mouseX >= self.x and mouseX <=self.x + self.w) and
            (mouseY >= self.y and mouseY <= self.y + self.h)):
            return True
        return False