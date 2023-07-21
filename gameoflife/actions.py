import pygame

from pygame import Surface, Rect
from pygame.locals import *
from gameoflife.button import Button
from gameoflife.colors import BLACK, LITE_GREY , GREY



class Actions:
    def __init__(self, x:int, y:int, width:int, height:int) -> None:
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.font = pygame.font.Font(None, 32)

        btnMargin = 30
        btnWidth = 100
        btnHeight = 30

        startStopBtnX = (x + width / 2) - (btnWidth / 2)
        startStopBtnY = (y + height / 2) - (btnHeight / 2)
        self.startStopBtn = Button("Stop", self.font, startStopBtnX, startStopBtnY, 100, 30)
        self.stopped = False

        resetBtnX = startStopBtnX - btnWidth - btnMargin
        resetBtnY = startStopBtnY
        self.resetBtn = Button("Reset", self.font, resetBtnX, resetBtnY, btnWidth, btnHeight)
        self.reset = False

        recordBtnX = resetBtnX - btnWidth - btnMargin
        recordBtnY = startStopBtnY
        self.recordBtn = Button("Record", self.font, recordBtnX, recordBtnY, btnWidth, btnHeight)
        self.record = False

        nextBtnX = startStopBtnX + btnWidth + btnMargin
        nextBtnY = startStopBtnY
        self.nextBtn = Button("Next", self.font, nextBtnX, nextBtnY, btnWidth, btnHeight)
        self.next = False

        clearBtnX = nextBtnX + btnWidth + btnMargin
        clearBtnY = startStopBtnY
        self.clearBtn = Button("Clear", self.font, clearBtnX, clearBtnY, btnWidth, btnHeight)
        self.clear = False


    def eventHandler(self, event:pygame.event):
        if event.type == MOUSEBUTTONUP:
            (mX, mY) = pygame.mouse.get_pos()
            if self.startStopBtn.clicked(mX, mY):
                self.stopped = not self.stopped
                self.startStopBtn.setText("Start" if self.stopped else "Stop")
            elif self.resetBtn.clicked(mX, mY):
                self.reset = True
            elif self.nextBtn.clicked(mX, mY):
                self.next = True
            elif self.clearBtn.clicked(mX, mY):
                self.clear = True

    def getHeight(self):
        return self.height

    def isStopped(self):
        return self.stopped

    def stop(self):
        self.stopped = True
        self.startStopBtn.setText("Start")

    def resetCells(self):
        reset = self.reset
        self.reset = False
        return reset

    def clearCells(self):
        clear = self.clear
        self.clear = False
        return clear

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
        self.clearBtn.draw(screen)
        self.recordBtn.draw(screen)

        # TODO:
        #   - speed / fps dial
        #   - cell size dial

        (mouseX, mouseY) = pygame.mouse.get_pos()
        mousePosImg = self.font.render(f"{mouseX}, {mouseY}", True, BLACK)
        screen.blit(mousePosImg, (self.x + 25, self.y + 25))
