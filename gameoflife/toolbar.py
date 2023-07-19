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
        self.hackFont = pygame.font.Font(None, 32)

        btnMargin = 30
        btnWidth = 100
        btnHeight = 30

        startStopBtnX = (x + width / 2) - (btnWidth / 2)
        startStopBtnY = (y + height / 2) - (btnHeight / 2)
        self.startStopBtn = Button("Stop", self.hackFont, startStopBtnX, startStopBtnY, 100, 30)

        resetBtnX = startStopBtnX - btnWidth - btnMargin
        resetBtnY = startStopBtnY
        self.resetBtn = Button("Reset", self.hackFont, resetBtnX, resetBtnY, btnWidth, btnHeight)

        nextBtnX = startStopBtnX + btnWidth + btnMargin
        nextBtnY = startStopBtnY
        self.nextBtn = Button("Next", self.hackFont, nextBtnX, nextBtnY, btnWidth, btnHeight)
        self.next = False

    def update(self):
        pass

    def eventHandler(self, event:pygame.event):
        if event.type == MOUSEBUTTONUP:
            (mX, mY) = pygame.mouse.get_pos()
            if self.startStopBtn.clicked(mX, mY):
                self.stopped = not self.stopped
                self.startStopBtn.setText("Start" if self.stopped else "Stop")
            elif self.resetBtn.clicked(mX, mY):
                self.setReset(True)
            elif self.nextBtn.clicked(mX, mY):
                self.next = True

    def isStopped(self):
        return self.stopped

    def setStopped(self, state:bool):
        self.stopped = state

    def isReset(self):
        return self.reset

    def setReset(self, state:bool):
        self.reset = state

    def nextFrame(self):
        next = self.next
        self.next = False
        return next

    def draw(self, screen:Surface):
        bg = Rect(self.x, self.y, self.width, self.height)

        pygame.draw.rect(screen, LITE_GREY, bg)
        pygame.draw.line(screen, GREY, (self.x, self.y), (self.x + self.width, self.y))

        self.startStopBtn.draw(screen)
        self.resetBtn.draw(screen)
        self.nextBtn.draw(screen)

        # TODO:
        #   - speed / fps dial
        #   - cell size dial

        mousePos = pygame.mouse.get_pos()
        mousePosImg = self.hackFont.render(f"{mousePos[0]}, {mousePos[1]}", True, BLACK)
        screen.blit(mousePosImg, (self.x + 25, self.y + 25))
