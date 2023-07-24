from typing import Union, List
# Still lifes:
# Oscillators:
# Spaceships:
from gameoflife.cell import Cell, CellState
from gameoflife.colors import WHITE, BLACK
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
        self.path:str = path
        self.type:PatternType = type
        self.cells:List[List] = []
        self.cellWidth = 5
        self.cellHeight = 5
        self.rowMaxLen = 0
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

    def setCellHeight(self, height:int) -> None:
        self.cellHeight = height
        for y in range(len(self.cells)):
            for x in range(len(self.cells[y])):
                cell = self.cells[y][x]
                cell.setHeight(height)

    def setCellWidth(self, width:int) -> None:
        self.cellWidth = width

    def getSurface(self) -> Surface:
        width = self.rowMaxLen * self.cellWidth
        height = len(self.cells) * self.cellHeight
        surf = Surface((width, height))
        print(self.name, (width, height))
        for y in range(len(self.cells)):
            for x in range(len(self.cells[y])):
                cell = self.cells[y][x]
                cell.draw(surf)
        return surf

class PatternMenu:
    def __init__(self, x:int, y:
        int, w:int) -> None:
        self.x:int = x
        self.y:int = y
        self.w:int = w
        self.rowHeight = 50
        self.font = None

    def setFont(self, font:Font) -> None:
        self.font = font

    def setPatterns(self, patterns:List) -> None:
        self.patterns = patterns

    def draw(self, screen:Surface):
        h = 300
        rect = Rect(self.x, self.y, self.w, h)

        draw.rect(screen, WHITE, rect)
        draw.line(screen, BLACK, (self.x, self.y), (self.x + self.w, self.y)) # top
        draw.line(screen, BLACK, (self.x, self.y), (self.x, self.y + h))
        draw.line(screen, BLACK, (self.x + self.w, self.y), (self.x + self.w, self.y + h))
        draw.line(screen, BLACK, (self.x, self.y + h), (self.x + self.w, self.y + h))

        row = 0
        for pattern in self.patterns:
            patternSurf = pattern.getSurface()
            screen.blit(patternSurf, (self.x + 15, self.y + (row * pattern.getHeight())))
            row += 1
