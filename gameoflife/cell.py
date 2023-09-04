import pygame
import time

from pygame import Rect, Surface
from typing import List, Tuple, Union


class CellState:
    DEAD:int = 0
    ALIVE:int = 1


class Cell:
    def __init__(
        self, x: int, y: int, width: int, height: int, state: Union[int, None] = None
    ) -> None:
        self._rect = Rect(x, y, width, height)
        self.state: Union[int, None] = CellState.DEAD
        self.nextState: Union[int, None] = None
        self.colors: dict = {
            CellState.ALIVE: (0, 0, 0),
            CellState.DEAD: (255, 255, 255),
        }
        self.state = state
        self.surface = Surface(self._rect.size)

    def draw(self, screen: Surface):
        self.surface.fill(self.colors[self.state])
        screen.blit(self.surface, (self._rect.x * self._rect.width, self._rect.y * self._rect.height))

    def getRect(self) -> Rect:
        return self._rect

    def getState(self) -> Union[int, None]:
        return self.state

    def getH(self) -> int:
        return self._rect.height

    def getW(self) -> int:
        return self._rect.width

    def getX(self) -> int:
        return self._rect.x

    def getY(self) -> int:
        return self._rect.y

    def getCoord(self) -> Tuple[int, int]:
        return (self._rect.y, self._rect.x)

    def getNextState(self) -> Union[int, None]:
        return self.nextState

    def setState(self, state: Union[int, None]) -> None:
        self.state = state

    def setNextState(self, state: Union[int, None]) -> None:
        self.nextState = state

    def setStateColor(self, state: Union[int, None], color) -> None:
        self.colors[state] = color

    def setHeight(self, height: int) -> None:
        self._rect.height = height
        self.surface = Surface(self._rect.size)

    def setWidth(self, width: int) -> None:
        self._rect.width = width
        self.surface = Surface(self._rect.size)

def getCellAtPoint(x, y, cells, dimension) -> Cell:
    pos = dimension * y + x
    count = len(cells)
    if pos < count and x >= 0:
        return cells[pos]
    return None
    #raise Exception(f"cell point outside of boundary: (x: {x}, y: {y}, rows: {rows}, numCells: {len(cells)})")

def getCellStateAtPoint(x, y, cells, dimension) -> int:
    pos = dimension * y + x
    try:
        return cells[pos].getState()
    except:
        pass
    return 0

def getAliveNeighbors(x:int, y:int, dimension:int, cells:List) -> int:
    alive = 0
    alive += getCellStateAtPoint(x-1, y-1, cells, dimension)
    alive += getCellStateAtPoint(x, y-1, cells, dimension)
    alive += getCellStateAtPoint(x+1, y-1, cells, dimension)
    alive += getCellStateAtPoint(x-1, y, cells, dimension)
    alive += getCellStateAtPoint(x+1, y, cells, dimension)
    alive += getCellStateAtPoint(x-1, y+1, cells, dimension)
    alive += getCellStateAtPoint(x, y+1, cells, dimension)
    alive += getCellStateAtPoint(x+1, y+1, cells, dimension)

    return alive

def printCells(cells, rows) -> None:
    output = ''
    for y in range(rows):
        row = ""
        for x in range(rows):
            cell = getCellAtPoint(x, y, cells, rows)
            if cell is None:
                row += "-"
            elif cell.getNextState() == CellState.ALIVE:
                row += "x"
            else:
                row += "."
        output += row + "\n"
    print(output)

