import pygame

from gameoflife.button import CircleButton
from gameoflife.cell import Cell, CellState
from gameoflife.colors import (
    WHITE,
    BLACK,
    GREY_LIGHT1,
    GREY_LIGHT2,
    GREY,
    RED,
    RED_LIGHT1,
    GREY_DARK1,
)
from gameoflife.helpers import drawRectBorder
from pygame import Surface, draw, Rect, Color
from pygame.font import Font
from pygame.locals import MOUSEBUTTONUP
from typing import Union, List


class PatternType:
    StillLife: int = 1
    Oscillator: int = 2
    Spacehship: int = 3
    FlipFlop: int = 4
    Methuselah: int = 5


class Pattern:
    def __init__(self, name: str, path: str, type: PatternType) -> None:
        self.rows: list = 0
        self.cols: list = 0
        self.name: str = name
        self.desc: str = ""  # TODO
        self.path: str = path
        self.type: PatternType = type
        self.cells: List[List] = []
        self.cellWidth = 10
        self.cellHeight = 10
        self.rowMaxLen = 0
        self.bgColor = GREY_LIGHT1
        self._load()

    def _load(self):
        with open(self.path) as file:
            lines = [line.rstrip() for line in file]
            self.rows = len(lines)
            y = 0
            for line in lines:
                if len(line) > self.rowMaxLen:
                    self.rowMaxLen = len(line)
                row = []
                x = 0
                for char in line:
                    cellState = CellState.DEAD if char == "0" else CellState.ALIVE
                    c = Cell(x, y, self.cellWidth, self.cellHeight, cellState)
                    row.append(c)
                    x += 1
                self.cells.append(row)
                y += 1
            self.cols = self.rowMaxLen

    def getCells(self) -> List[List]:
        return self.cells

    def getCols(self) -> int:
        return self.cols

    def getHeight(self) -> int:
        return self.cellHeight * len(self.cells)

    def getName(self) -> str:
        return self.name

    def getRows(self) -> int:
        return self.rows

    def getSurface(self) -> Surface:
        width = self.rowMaxLen * self.cellWidth
        height = len(self.cells) * self.cellHeight
        surf = Surface((width, height)).convert_alpha()
        surf.fill(self.bgColor)
        for y in range(len(self.cells)):
            for x in range(len(self.cells[y])):
                cell = self.cells[y][x]
                cell.draw(surf)
        return surf

    def getWidth(self) -> int:
        return self.cellWidth * self.cols

    def setBgColor(self, color) -> None:
        self.bgColor = color
        for y in range(len(self.cells)):
            for x in range(len(self.cells[y])):
                cell = self.cells[y][x]
                cell.setStateColor(CellState.DEAD, color)

    def setCellHeight(self, height: int) -> None:
        self.cellHeight = height
        for y in range(len(self.cells)):
            for x in range(len(self.cells[y])):
                cell = self.cells[y][x]
                cell.setHeight(height)

    def setCellWidth(self, width: int) -> None:
        self.cellWidth = width
        for y in range(len(self.cells)):
            for x in range(len(self.cells[y])):
                cell = self.cells[y][x]
                cell.setHeight(width)


class PatternMenuRow:
    def __init__(
        self,
        x: int,
        y: int,
        w: int,
        pattern: Pattern,
        bgColor: Color,
        borderColor: Color,
    ) -> None:
        self.inactiveBgColor = bgColor
        self.bgColor = self.inactiveBgColor
        self.hoveredBgColor = GREY_LIGHT2
        self.pattern = pattern
        self.pattern.setBgColor(self.bgColor)
        self.padding = 0
        self.h = self.pattern.getHeight() + (self.padding * 2)
        self.x = x
        self.y = y
        self.w = w + (self.padding * 2)
        self.cursor = pygame.SYSTEM_CURSOR_ARROW

    def update(self) -> None:
        if self.hovered():
            self.bgColor = self.hoveredBgColor
            self.cursor = pygame.SYSTEM_CURSOR_HAND
            pygame.mouse.set_cursor(self.cursor)
        else:
            if self.cursor != pygame.SYSTEM_CURSOR_ARROW:
                self.cursor = pygame.SYSTEM_CURSOR_ARROW
                pygame.mouse.set_cursor(self.cursor)
            self.bgColor = self.inactiveBgColor
        self.pattern.setBgColor(self.bgColor)

    def draw(self, screen: Surface) -> None:
        surf = Surface((self.w, self.h))
        patternSurf = self.pattern.getSurface()
        patternHeight = self.pattern.getHeight()
        surf.fill(self.bgColor)
        surf.blit(patternSurf, (self.padding, self.padding))
        screen.blit(surf, (self.x, self.y))
        drawRectBorder(
            screen,
            self.x,
            self.y,
            self.w,
            self.h,
            GREY_DARK1,
        )

    def getHeight(self) -> int:
        return self.h

    def getPattern(self) -> Pattern:
        return self.pattern

    def hovered(self) -> bool:
        (mX, mY) = pygame.mouse.get_pos()
        if (mX >= self.x and mX <= self.x + self.w) and (
            mY >= self.y and mY <= self.y + self.h
        ):
            return True
        return False

    def clicked(self, event) -> bool:
        if event.type == MOUSEBUTTONUP and self.hovered():
            return True
        return False


class PatternMenu:
    def __init__(self, x: int, y: int) -> None:
        self.padding = 12
        self.x: int = x
        self.y: int = y
        self.w: int = 0
        self.pmrW: int = 0
        self.font = None
        self.bgColor = GREY_LIGHT1
        self.closeBtn = CircleButton("X", self.x + self.w, self.y, 10, RED_LIGHT1)
        self.closeBtn.setHoverBackgroundColor(RED)
        self._enabled = False
        self.rows = []

    def enable(self) -> None:
        self._enabled = True

    def enabled(self) -> bool:
        return self._enabled

    def disable(self) -> None:
        self._enabled = False

    def toggle(self) -> None:
        self._enabled = not self._enabled

    def setFont(self, font: Font) -> None:
        self.font = font
        self.closeBtn.setFont(font)

    def setPatterns(self, patterns: List[Pattern]) -> None:
        self.patterns = patterns
        self.rows.clear()
        yOffset = self.padding
        for pattern in patterns:
            pattern.setBgColor(self.bgColor)
            row = PatternMenuRow(
                self.x + self.padding,
                self.y + yOffset,
                self.pmrW,
                pattern,
                self.bgColor,
                BLACK,
            )
            self.rows.append(row)
            yOffset += row.getHeight() + self.padding

    def setPatternRowWidth(self, patternRowWidth:int) -> None:
        self.w = patternRowWidth + (self.padding * 2)
        self.pmrW = patternRowWidth
        self.closeBtn.setX(self.x + self.w)

    def getHeight(self) -> int:
        height = self.padding
        for row in self.rows:
            height += row.getHeight() + self.padding
        return height

    def update(self) -> None:
        if self._enabled:
            self.closeBtn.update()
            for row in self.rows:
                row.update()

    def eventHandler(self, event) -> bool:
        if self._enabled:
            if event.type == MOUSEBUTTONUP:
                (mX, mY) = pygame.mouse.get_pos()
                if self.closeBtn.clicked(mX, mY):
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                    self._enabled = False
                    return True
                else:
                    for row in self.rows:
                        if row.clicked(event):
                            return row.getPattern()
                if (mX >= self.x and mX <= self.x + self.w) and (
                    mY >= self.y and mY <= self.y + self.getHeight()
                ):
                    return True
        return False

    def draw(self, screen: Surface) -> None:
        if self._enabled:
            height = self.getHeight()
            rect = Rect(self.x, self.y, self.w, height)
            draw.rect(screen, self.bgColor, rect)
            drawRectBorder(screen, self.x, self.y, self.w, height)

            for row in self.rows:
                row.draw(screen)

            self.closeBtn.draw(screen)
