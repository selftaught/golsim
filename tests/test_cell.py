from typing import Union
from gameoflife.cell import Cell, CellState, getCellAtPoint, getAliveNeighbors, printCells
from pygame import Rect

import pytest

class TestCell:
    def _cell(self, state:Union[int, None] = None):
        return Cell(0, 0, 10, 10, state = state)

    def testCellStateValues(self):
        assert CellState.DEAD == False
        assert CellState.ALIVE == True

    def testCellGetSetState(self):
        cell = self._cell(CellState.ALIVE)
        assert cell.getState() == CellState.ALIVE

        cell = self._cell(CellState.DEAD)
        assert cell.getState() == CellState.DEAD

        cell.setState(CellState.ALIVE)
        assert cell.getState() == CellState.ALIVE

        cell.setState(CellState.DEAD)
        assert cell.getState() == CellState.DEAD

    def testCellGetSetNextState(self):
        cell = self._cell(CellState.DEAD)
        assert cell.getNextState() == None

        cell.setNextState(CellState.ALIVE)
        assert cell.getNextState() == CellState.ALIVE
        assert cell.getState() == CellState.DEAD

        cell.setState(CellState.ALIVE)
        cell.setNextState(CellState.DEAD)
        assert cell.getNextState() == CellState.DEAD
        assert cell.getState() == CellState.ALIVE

    def testGetRect(self):
        cell = Cell(12, 34, 56, 78, CellState.ALIVE)
        assert cell.getRect() == Rect(12, 34, 56, 78)
        assert cell.getX() == 12
        assert cell.getY() == 34
        assert cell.getW() == 56
        assert cell.getH() == 78

    def testGetCellAtPoint(self):
        rows = 3
        cells = [
            Cell(0, 0, 10, 10, CellState.DEAD),
            Cell(1, 0, 10, 10, CellState.ALIVE),
            Cell(2, 0, 10, 10, CellState.DEAD),
            Cell(0, 1, 10, 10, CellState.DEAD),
            Cell(1, 1, 10, 10, CellState.ALIVE),
            Cell(2, 1, 10, 10, CellState.DEAD),
            Cell(0, 2, 10, 10, CellState.DEAD),
            Cell(1, 2, 10, 10, CellState.ALIVE),
            Cell(2, 2, 10, 10, CellState.DEAD),
        ]

        cell = getCellAtPoint(0, 0, cells, rows)
        assert cell.getX() == 0
        assert cell.getY() == 0
        assert cell.getState() == CellState.DEAD

        cell = getCellAtPoint(0, 2, cells, rows)
        assert cell.getX() == 0
        assert cell.getY() == 2
        assert cell.getState() == CellState.DEAD

        cell = getCellAtPoint(1, 2, cells, rows)
        assert cell.getX() == 1
        assert cell.getY() == 2
        assert cell.getState() == CellState.ALIVE

        cell = getCellAtPoint(2, 2, cells, rows)
        assert cell.getX() == 2
        assert cell.getY() == 2
        assert cell.getState() == CellState.DEAD

        with pytest.raises(Exception, match='cell point outside of boundary'):
            getCellAtPoint(2, 3, cells, rows)

        with pytest.raises(Exception, match='cell point outside of boundary'):
            getCellAtPoint(3, 2, cells, rows)

        with pytest.raises(Exception, match='cell point outside of boundary'):
            getCellAtPoint(-1, 2, cells, rows)

    def testGetAliveNeighbors(self):
        cells = [
            Cell(0, 0, 10, 10, CellState.DEAD),
            Cell(1, 0, 10, 10, CellState.DEAD),
            Cell(2, 0, 10, 10, CellState.DEAD),
            Cell(0, 1, 10, 10, CellState.DEAD),
            Cell(1, 1, 10, 10, CellState.ALIVE),
            Cell(2, 1, 10, 10, CellState.DEAD),
            Cell(0, 2, 10, 10, CellState.DEAD),
            Cell(1, 2, 10, 10, CellState.DEAD),
            Cell(2, 2, 10, 10, CellState.DEAD),
        ]

        assert getAliveNeighbors(1, 1, 3, cells) == 0
        assert getAliveNeighbors(0, 0, 3, cells) == 1