import pygame
from pygame.font import Font
from gameoflife.colors import BLACK, GREY
from typing import Tuple

class Button:
    def __init__(self, text:str, font:Font, x:int, y:int, w:int, h:int) -> None:
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.text = text
        self.font = font
        self.rect = pygame.Rect(x, y, w, h)
        self.bgColor = GREY

    def setX(self, x) -> None:
        self.x = x

    def setY(self, y) -> None:
        self.y = y

    def setW(self, w) -> None:
        self.w = w

    def setH(self, h) -> None:
        self.h = h

    def setFont(self, font:Font) -> None:
        self.font = font

    def setBackgroundColor(self, bgColor:tuple) -> None:
        self.bgColor = bgColor

    def setText(self, text:str) -> None:
        self.text = text

    def draw(self, screen:pygame.Surface) -> None:
        pygame.draw.rect(screen, self.bgColor, self.rect)
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