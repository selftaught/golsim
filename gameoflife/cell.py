import random
import pygame

class CellState:
    DEAD = False
    ALIVE = True

class Cell:
    x : int = None
    y : int = None
    width : int = None
    height : int = None
    state : CellState = None
    nextState: CellState = None

    def __init__(self, x:int, y:int, width:int, height:int, state:CellState = None) -> None:
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        if state is None:
            self.state = CellState.ALIVE if random.randint(0 , 100) >= 50 else CellState.DEAD
        else:
            self.state = state

    def draw(self, screen : pygame.Surface):
        if self.state == CellState.ALIVE:
            surface = pygame.Surface((self.width, self.height))
            surface.fill((0, 0, 0))
            screen.blit(surface, (self.x * self.width, self.y * self.height))

    def getState(self) -> CellState:
        return self.state

    def getNextState(self) -> CellState:
        return self.nextState

    def setState(self, state:CellState) -> None:
        self.state = state

    def setNextState(self, state:CellState) -> None:
        self.nextState = state