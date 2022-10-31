from gameoflife.cell import Cell, CellState

def _cell(state:CellState = None):
    return Cell(0, 0, 10, 10, state = state)

def testCellStateValues():
    assert CellState.DEAD == False
    assert CellState.ALIVE == True

def testCellGetSetState():
    cell = _cell(CellState.ALIVE)
    assert cell.getState() == CellState.ALIVE

    cell = _cell(CellState.DEAD)
    assert cell.getState() == CellState.DEAD

    cell.setState(CellState.ALIVE)
    assert cell.getState() == CellState.ALIVE

    cell.setState(CellState.DEAD)
    assert cell.getState() == CellState.DEAD

def testCellGetSetNextState():
    cell = _cell(CellState.DEAD)
    assert cell.getNextState() == None

    cell.setNextState(CellState.ALIVE)
    assert cell.getNextState() == CellState.ALIVE
    assert cell.getState() == CellState.DEAD

    cell.setState(CellState.ALIVE)
    cell.setNextState(CellState.DEAD)
    assert cell.getNextState() == CellState.DEAD
    assert cell.getState() == CellState.ALIVE