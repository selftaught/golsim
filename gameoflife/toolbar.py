import pygame

from pygame import Surface, Rect
from pygame.locals import *
from gameoflife.button import Button
from gameoflife.colors import BLACK, LITE_GREY , GREY



class Toolbar:
    def __init__(self, x:int, y:int, width:int, height:int) -> None:
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.stopped = False
        self.reset = False

        startBtnW = 100
        startBtnH = 30
        startBtnX = (x + width / 2) - (startBtnW / 2)
        startBtnY = (y + height / 2) - (startBtnH / 2)
        self.startBtn = Button("Stop", startBtnX, startBtnY, 100, 30)

    def update(self):
        pass

    def eventHandler(self, event:pygame.event):
        if event.type == MOUSEBUTTONUP:
            print(f"MOUSEBUTTONUP\n")
            print(pygame.mouse.get_pos())

    def isStopped(self):
        return self.stopped

    def setStopped(self, state:bool):
        self.stopped = state

    def isReset(self):
        return self.reset

    def setReset(self, state:bool):
        self.reset = state

    def draw(self, screen:Surface):
        bg = Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(screen, LITE_GREY, bg)
        pygame.draw.line(screen, GREY, (self.x, self.y), (self.x + self.width, self.y))
        # TODO:
        #   - start / stop button
        self.startBtn.draw(screen)
        #   - reset button
        #   - next button
        #   - speed / fps dial
        #   - cell size dial
