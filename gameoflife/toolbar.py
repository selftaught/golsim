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

        self.startStopBtnW = 100
        self.startStopBtnH = 30
        self.startStopBtnX = (x + width / 2) - (self.startStopBtnW / 2)
        self.startStopBtnY = (y + height / 2) - (self.startStopBtnH / 2)

        self.hackFont = pygame.font.Font(None, 32)
        self.startStopBtn = Button("Stop", self.hackFont, self.startStopBtnX, self.startStopBtnY, 100, 30)

        self.buttons = []

    def update(self):
        pass

    def eventHandler(self, event:pygame.event):
        if event.type == MOUSEBUTTONUP:
            (mouseX, mouseY) = pygame.mouse.get_pos()
            if self.startStopBtn.clicked(mouseX, mouseY):
                self.stopped = not self.stopped
                self.startStopBtn.setText("Start" if self.stopped else "Stop")

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
        self.startStopBtn.draw(screen)
        #   - reset button
        #   - next button
        #   - speed / fps dial
        #   - cell size dial

        mousePos = pygame.mouse.get_pos()
        mousePosImg = self.hackFont.render(f"{mousePos[0]}, {mousePos[1]}", True, BLACK)
        screen.blit(mousePosImg, (self.x + 25, self.y + 25))
