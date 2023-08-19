import random
import pygame

from pygame import Rect, Surface
from typing import Union, List, Tuple


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

def getCellAtPoint(x, y, cells, rows) -> Cell:
    pos = rows * y + x
    numCells = len(cells)
    if pos < numCells and x >= 0:
        return cells[pos]
    raise Exception(f"cell point outside of boundary: (x: {x}, y: {y}, rows: {rows}, numCells: {len(cells)})")

def getCellAndNeighbors(x: int, y: int, dimension:int, cells: list) -> Tuple[List[Cell], int]:
    # dimension is the number of rows / columns that make up the cells array
    # a 3x3 cell array would have a dimension of 3, 2x2 would have a dimension of 2, etc
    alive = 0
    r = [
        getCellAtPoint(x-1, y-1, cells, dimension) if x > 0 and y > 0 else None,
        getCellAtPoint(x, y-1, cells, dimension) if y > 0 else None,
        getCellAtPoint(x+1, y-1, cells, dimension) if x < dimension - 1 and y > 0 else None,
        getCellAtPoint(x-1, y, cells, dimension) if x > 0 else None,
        getCellAtPoint(x, y, cells, dimension),
        getCellAtPoint(x+1, y, cells, dimension) if x < dimension - 1 else None,
        getCellAtPoint(x-1, y+1, cells, dimension) if x > 0 and y < dimension - 1 else None,
        getCellAtPoint(x, y+1, cells, dimension) if y < dimension - 1 else None,
        getCellAtPoint(x+1, y+1, cells, dimension) if x < dimension - 1 and y < dimension - 1 else None,
    ]

    for i in range(len(r)):
        if i == 4:
            continue
        alive += r[i].getState() if r[i] is not None else 0
        if alive >= 4:
            break

    return (r, alive)

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

