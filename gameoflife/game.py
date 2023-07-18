import pygame
from pygame.locals import KEYDOWN, K_ESCAPE, MOUSEBUTTONUP, K_g
from gameoflife.colors import BLUE
from gameoflife.config import Config
from gameoflife.grid import Grid
from gameoflife.toolbar import Toolbar
from gameoflife.cell import *


class Game:
    cfg : Config = None
    running : bool = True
    height : int
    width : int
    cellHeight : int = None
    cellWidth : int = None
    cells : list = []
    cols : int = None
    rows : int = None
    clock : pygame.time.Clock = None
    screen : pygame.Surface = None

    def __init__(self) -> None:
        pygame.init()
        self.cfg = Config()
        self.height = self.cfg.get('screen.height')
        self.width = self.cfg.get('screen.width')
        self.screen = pygame.display.set_mode([self.width, self.height])
        self.cellHeight = self.cfg.get('cell.height', default=5)
        self.cellWidth = self.cfg.get('cell.width', default=5)
        self.rows = int((self.height - 100) / self.cellHeight)
        self.cols = int(self.width / self.cellWidth)
        self.clock = pygame.time.Clock()
        self.grid = Grid(self.cols, self.rows, self.cellWidth, self.cellHeight)
        self.cells = [[Cell(x, y, self.cellWidth, self.cellHeight) for x in range(self.cols)] for y in range(self.rows)]
        self.toolbar = Toolbar(0, self.height - 100, self.width, 100)

    def isRunning(self):
        return self.running

    def eventLoop(self):
        for event in pygame.event.get():
            self.toolbar.eventHandler(event)
            # Window was closed
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == KEYDOWN:
                # ESC key down
                if event.key == K_ESCAPE :
                    self.running = False
                if event.key == K_g:
                    self.grid.toggle()
            elif event.type == MOUSEBUTTONUP:
                pass

    def loop(self) -> None:
        while self.isRunning():
            self.eventLoop()
            self.update()
            self.draw()
            self.clock.tick(self.cfg.get('fps', default=60))
        pygame.quit()

    def update(self) -> None:
        if not self.toolbar.isStopped():
            for y in range(len(self.cells)):
                for x in range(len(self.cells[y])):
                    alive = cellAliveNeighborCount(x, y, self.cols, self.rows, self.cells)
                    cell = self.cells[y][x]

                    # 1. Alive cells with < 2 alive neighbors die (under-population).
                    # 2. Alive cells with 2 or 3 neighbors survives to the next generation.
                    # 3. Alive cells with > 3 neighbors dies (over-population).
                    # 4. Dead cells with exactly 3 live neighbors becomes a live cell (reproduction).
                    if cell.getState() == CellState.ALIVE:
                        if alive < 2:
                            cell.setNextState(CellState.DEAD)
                        elif alive == 2 or alive == 3:
                            cell.setNextState(CellState.ALIVE)
                        elif alive > 3:
                            cell.setNextState(CellState.DEAD)
                    elif cell.getState() == CellState.DEAD:
                        if alive == 3:
                            cell.setNextState(CellState.ALIVE)
                        else:
                            cell.setNextState(CellState.DEAD)

            for y in range(len(self.cells)):
                for x in range(len(self.cells[y])):
                    cell = self.cells[y][x]
                    nextState = cell.getNextState()
                    cell.setState(nextState)

        self.toolbar.update()

    def draw(self) -> None:
        self.screen.fill((255, 255, 255))
        self.grid.draw(self.screen)

        for y in range(len(self.cells)):
            for x in range(len(self.cells[y])):
                cell = self.cells[y][x]
                cell.draw(self.screen)

        self.toolbar.draw(self.screen)

        pygame.display.update()