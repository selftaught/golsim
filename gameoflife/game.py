import glob
import pygame

from pygame.font import Font
from pygame.locals import KEYDOWN, K_ESCAPE, MOUSEBUTTONUP, K_g
from gameoflife.colors import BLUE, BLACK
from gameoflife.config import Config
from gameoflife.grid import Grid
from gameoflife.actions import Actions
from gameoflife.button import RectButton
from gameoflife.cell import *
from gameoflife.pattern import Pattern, PatternMenu, PatternType


class State:
    displayPatternMenu: bool = False


class Game:
    cfg: Config = None
    running: bool = True
    height: int
    width: int
    cellHeight: int = None
    cellWidth: int = None
    cells: list = []
    cols: int = None
    rows: int = None
    clock: pygame.time.Clock = None
    screen: pygame.Surface = None

    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Game of Life")

        iconImg = pygame.image.load("images/gameoflife.png")
        if iconImg:
            pygame.display.set_icon(iconImg)

        self.buttons = []
        self.cfg = Config()
        self.font = Font(None, 24)
        self.height = self.cfg.get("screen.height")
        self.width = self.cfg.get("screen.width")
        self.screen = pygame.display.set_mode([self.width, self.height])
        self.cellHeight = self.cfg.get("cell.height", default=5)
        self.cellWidth = self.cfg.get("cell.width", default=5)
        self.rows = int((self.height - 100) / self.cellHeight)
        self.cols = int(self.width / self.cellWidth)
        self.clock = pygame.time.Clock()
        self.grid = Grid(self.cols, self.rows, self.cellWidth, self.cellHeight)
        self.cells = [
            [
                Cell(x, y, self.cellWidth, self.cellHeight, CellState.DEAD)
                for x in range(self.cols)
            ]
            for y in range(self.rows)
        ]
        self.actions = Actions(0, self.height - 100, self.width, 100)
        self.state = State()
        self.patternsMenu = PatternMenu(50, 50, 200)
        self.patternsMenu.setFont(self.font)
        self.patterns = []

        btnMargin = 30
        btnWidth = 100
        btnHeight = 30

        patternsBtnX = 940
        patternsBtnY = 735

        self.patternsBtn = RectButton(
            "Patterns", patternsBtnX, patternsBtnY, btnWidth, btnHeight
        )
        self.patternsBtn.setFont(self.font)
        self.loadPatterns()

    def eventLoop(self) -> None:
        for event in pygame.event.get():
            self.actions.eventHandler(event)
            if self.patternsMenu.eventHandler(event):
                return
            if self.state.displayPatternMenu:
                if self.patternsMenu.eventHandler(event):
                    return
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.running = False
                if event.key == K_g:
                    self.grid.toggle()
            elif event.type == MOUSEBUTTONUP:
                (mouseX, mouseY) = pygame.mouse.get_pos()
                if self.patternsBtn.clicked(mouseX, mouseY):
                    self.patternsMenu.toggle()
                    self.state.displayPatternMenu = self.patternsMenu.enabled()
                elif mouseY < self.height - self.actions.getHeight():
                    cellX = int(mouseX / self.cellWidth)
                    cellY = int(mouseY / self.cellHeight)
                    try:
                        cell = self.cells[cellY][cellX]
                        cell.setState(
                            CellState.DEAD
                            if cell.getState() == CellState.ALIVE
                            else CellState.ALIVE
                        )
                    except Exception as e:
                        print(e)

    def loop(self) -> None:
        while self.running:
            self.eventLoop()
            self.update()
            self.draw()
            self.clock.tick(self.cfg.get("fps", default=5))
        pygame.quit()

    def update(self) -> None:
        if self.actions.resetCells():
            # TODO: instead of resetting to a random state - reset to the initial state?
            self.cells = [
                [Cell(x, y, self.cellWidth, self.cellHeight) for x in range(self.cols)]
                for y in range(self.rows)
            ]
        elif self.actions.clearCells():
            self.actions.stop()
            self.cells = [
                [
                    Cell(x, y, self.cellWidth, self.cellHeight, CellState.DEAD)
                    for x in range(self.cols)
                ]
                for y in range(self.rows)
            ]

        self.patternsBtn.update()
        self.patternsMenu.update()

        if not self.actions.isStopped() or self.actions.nextFrame():
            for y in range(len(self.cells)):
                for x in range(len(self.cells[y])):
                    alive = cellAliveNeighborCount(
                        x, y, self.cols, self.rows, self.cells
                    )
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

            allCellsDead = True
            for y in range(len(self.cells)):
                for x in range(len(self.cells[y])):
                    cell = self.cells[y][x]
                    nextState = cell.getNextState()
                    cell.setState(nextState)
                    if nextState == CellState.ALIVE:
                        allCellsDead = False

            if allCellsDead:
                self.actions.stop()

    def draw(self) -> None:
        self.screen.fill((255, 255, 255))
        self.grid.draw(self.screen)

        for y in range(len(self.cells)):
            for x in range(len(self.cells[y])):
                cell = self.cells[y][x]
                cell.draw(self.screen)

        self.actions.draw(self.screen)
        self.patternsBtn.draw(self.screen)
        self.patternsMenu.draw(self.screen)

        pygame.display.update()

    def loadPatterns(self) -> None:
        # still lifes
        for path in sorted(glob.glob("patterns/still-lifes/*")):
            pattern = Pattern(path.split("/")[-1], path, PatternType.StillLife)
            if pattern.getRows():
                self.patterns.append(pattern)

        # oscillators
        for path in glob.glob("patterns/oscillators/*"):
            pattern = Pattern(path.split("/")[-1], path, PatternType.Oscillator)
            if pattern.getRows():
                self.patterns.append(pattern)

        # spaceships
        for path in glob.glob("patterns/spaceships/*"):
            pattern = Pattern(path.split("/")[-1], path, PatternType.Spacehship)
            if pattern.getRows():
                self.patterns.append(pattern)

        self.patternsMenu.setPatterns(self.patterns)
