import random
import pygame


class CellState:
    DEAD = False
    ALIVE = True


class Cell:
    def __init__(
        self, x: int, y: int, width: int, height: int, state: CellState = None
    ) -> None:
        self.x : int = x
        self.y : int = y
        self.width : int = width
        self.height : int = height
        self.state : CellState = CellState.DEAD
        self.nextState : CellState = None
        self.colors : dict = {CellState.ALIVE: (0, 0, 0), CellState.DEAD: (255, 255, 255)}
        if state is None:
            self.state = (
                CellState.ALIVE if random.randint(0, 100) < 10 else CellState.DEAD
            )
        else:
            self.state = state

    def draw(self, screen: pygame.Surface):
        surface = pygame.Surface((self.width, self.height))
        surface.fill(self.colors[self.state])
        screen.blit(surface, (self.x * self.width, self.y * self.height))

    def getState(self) -> CellState:
        return self.state

    def getNextState(self) -> CellState:
        return self.nextState

    def setState(self, state: CellState) -> None:
        self.state = state

    def setNextState(self, state: CellState) -> None:
        self.nextState = state

    def setStateColor(self, state: CellState, color) -> None:
        self.colors[state] = color

    def setHeight(self, height: int) -> None:
        self.height = height

    def setWidth(self, width: int) -> None:
        self.width = width


def cellAliveNeighborCount(x: int, y: int, cols: int, rows: int, cells: int):
    alive = 0
    # Left
    if x > 0 and cells[y][x - 1].getState() == CellState.ALIVE:
        alive += 1
    # Right
    if x < (cols - 1) and cells[y][x + 1].getState() == CellState.ALIVE:
        alive += 1
    # Top
    if y > 0 and cells[y - 1][x].getState() == CellState.ALIVE:
        alive += 1
    # Bottom
    if y < (rows - 1) and cells[y + 1][x].getState() == CellState.ALIVE:
        alive += 1
    # Top left
    if x > 0 and y > 0 and cells[y - 1][x - 1].getState() == CellState.ALIVE:
        alive += 1
    # Top right
    if x < (cols - 1) and y > 0 and cells[y - 1][x + 1].getState() == CellState.ALIVE:
        alive += 1
    # Bottom left
    if x > 0 and y < (rows - 1) and cells[y + 1][x - 1].getState() == CellState.ALIVE:
        alive += 1
    # Bottom right
    if (
        x < (cols - 1)
        and y < (rows - 1)
        and cells[y + 1][x + 1].getState() == CellState.ALIVE
    ):
        alive += 1

    return alive
