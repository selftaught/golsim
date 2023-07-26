from typing import Union, List
# Still lifes:
# Oscillators:
# Spaceships:
from gameoflife.button import CircleButton
from gameoflife.cell import Cell, CellState
from gameoflife.colors import WHITE, BLACK, GREY_LIGHT1, GREY_LIGHT2, GREY, RED
from gameoflife.helpers import drawRectBorder
from pygame import Surface, draw, Rect
from pygame.font import Font


class PatternType:
    StillLife:int = 1
    Oscillator:int = 2
    Spacehship:int = 3


class Pattern:
    def __init__(self, name:str, path:str, type:PatternType) -> None:
        self.rows:list = 0
        self.cols:list = 0
        self.name:str = name
        self.desc:str = '' # TODO
        self.path:str = path
        self.type:PatternType = type
        self.cells:List[List] = []
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
                    cellState = CellState.DEAD if char == '0' else CellState.ALIVE
                    c = Cell(x, y, self.cellWidth, self.cellHeight, cellState)
                    row.append(c)
                    x += 1
                self.cells.append(row)
                y += 1
            self.cols = self.rowMaxLen

    def getHeight(self) -> int:
        return self.cellHeight * len(self.cells)

    def setBgColor(self, color) -> None:
        self.bgColor = color
        for y in range(len(self.cells)):
            for x in range(len(self.cells[y])):
                cell = self.cells[y][x]
                cell.setStateColor(CellState.DEAD, color)

    def setCellHeight(self, height:int) -> None:
        self.cellHeight = height
        for y in range(len(self.cells)):
            for x in range(len(self.cells[y])):
                cell = self.cells[y][x]
                cell.setHeight(height)

    def setCellWidth(self, width:int) -> None:
        self.cellWidth = width
        for y in range(len(self.cells)):
            for x in range(len(self.cells[y])):
                cell = self.cells[y][x]
                cell.setHeight(width)

    def getSurface(self) -> Surface:
        width = self.rowMaxLen * self.cellWidth
        height = len(self.cells) * self.cellHeight
        surf = Surface((width, height))
        surf.fill(self.bgColor)
        print(self.name, (width, height))
        for y in range(len(self.cells)):
            for x in range(len(self.cells[y])):
                cell = self.cells[y][x]
                cell.draw(surf)
        #draw.line()
        return surf

class PatternMenu:
    def __init__(self, x:int, y:int, w:int) -> None:
        self.x:int = x
        self.y:int = y
        self.w:int = w
        self.font = None
        self.closeBtn = CircleButton("X", self.font, self.x + self.w, self.y, 10, RED)

    def setFont(self, font:Font) -> None:
        self.font = font
        self.closeBtn.setFont(font)

    def setPatterns(self, patterns:List) -> None:
        self.patterns = patterns

    def eventHandler(self, event):
        pass

    def draw(self, screen:Surface):
        padding = 20
        height = padding
        for pattern in self.patterns:
            height += (pattern.getHeight() + padding)

        rect = Rect(self.x, self.y, self.w, height)
        bgColor = GREY_LIGHT1

        draw.rect(screen, bgColor, rect)
        drawRectBorder(screen, self.x, self.y, self.w, height)

        yOffset = padding
        for pattern in self.patterns:
            pattern.setBgColor(bgColor)
            patternSurf = pattern.getSurface()
            patternHeight = pattern.getHeight()
            screen.blit(patternSurf, (self.x + padding, self.y + yOffset))
            drawRectBorder(screen, self.x + padding - 5, self.y + yOffset - 5, self.w - ((padding - 5) * 2), patternHeight + 10, GREY)
            yOffset += patternHeight + padding

        self.closeBtn.draw(screen)