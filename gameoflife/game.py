import asyncio
import concurrent.futures
import glob
import pygame
import time

from pygame.font import Font
from pygame.locals import KEYDOWN, MOUSEBUTTONUP, MOUSEBUTTONDOWN, K_g, K_ESCAPE
from gameoflife.colors import (
    BLUE,
    BLACK,
    GREY,
    GREY_DARK1,
    GREY_DARK2,
    GREY_LIGHT1,
    RED,
    WHITE,
)
from gameoflife.constvars import *
from gameoflife.config import Config
from gameoflife.grid import Grid
from gameoflife.button import RectButton
from gameoflife.cell import *
from gameoflife.pattern import Pattern, PatternMenu, PatternType
from gameoflife.cell import getCellAtPoint
from gameoflife.helpers import drawRectBorder

class MouseModes:
    DRAW = 0
    PAN = 1


class ButtonID:
    CLEAR = "Clear"
    EXIT = "Exit"
    NEXT = "Next"
    RESET = "Reset"
    START = "Start"
    STOP = "Stop"
    PATTERNS = "Patterns"

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
        self.cellH = self.cfg.get("cell.height", default=5)
        self.cellW = self.cfg.get("cell.width", default=5)
        self.actionBarHeight = 70
        self.actionBarX = 0
        self.actionBarY = self.height - self.actionBarHeight
        self.clock = pygame.time.Clock()
        self.cells = None
        self.cols = 200
        self.colsVisible = int(self.width / self.cellW)
        self.rows = 200
        self.rowsVisible = int(self.height / self.cellH)
        self.grid = Grid(self.colsVisible, self.rowsVisible, self.cellW, self.cellH)
        self.cellSurf = pygame.Surface((self.cols * self.cellW, self.rows * self.cellH))
        self.viewCellX = int((self.cols / 2) - (self.colsVisible / 2))
        self.viewCellY = int((self.rows / 2) - (self.rowsVisible / 2))

        print(
            f"cols: {self.cols}, cols visible: {self.colsVisible}\nrows: {self.rows}, rows visible: {self.rowsVisible}"
        )
        print(f"viewCellX: {self.viewCellX}, viewCellY: {self.viewCellY}")
        #
        self._clear = False
        self._next = False
        self._reset = False
        self._stopped = True
        self.patternsMenu = PatternMenu(50, 50, 200)
        self.patternsMenu.setFont(self.font)
        self.patterns = []
        self.patternSelected = None
        self.generation = 0
        self.cells = []
        self.cellsAlive = 0
        self.cellsBirthed = 0
        self.cellsDied = 0
        self.mouseButtonHeldDown = False

        # Zoom
        self.zoom = 1
        self.zoomMax = 10
        self.zoomMin = 1
        self.zoomStep = 0.10

        self.initPatterns()
        self.initButtons()
        self.initCells()

    def initButtons(self) -> None:
        btnHeight = 30
        btnMargin = 30
        btnWidth = 100

        self.buttons = [
            # RectButton(ButtonText.RESET),
            RectButton(ButtonText.CLEAR),
            RectButton(ButtonText.START),
            RectButton(ButtonText.NEXT),
            RectButton(ButtonText.PATTERNS),
            RectButton(ButtonText.EXIT),
        ]

        widthRemainder = self.width - (
            (len(self.buttons) * (btnWidth + btnMargin)) - btnMargin
        )
        buttonX = widthRemainder / 2
        buttonY = (self.actionBarY) + ((self.actionBarHeight / 2) - btnHeight / 2)

        for button in self.buttons:
            button.setFont(self.font)
            button.setHoverBackgroundColor(GREY_DARK2)
            button.setBorderColor(GREY_DARK2)
            if isinstance(button, RectButton):
                button.setRect(pygame.Rect(buttonX, buttonY, btnWidth, btnHeight))
            buttonX += btnWidth + btnMargin

    def initCells(self) -> None:
        self.cells = []
        for i in range(self.cols * self.rows):
            x = i % self.rows
            y = int(i / self.rows)
            self.cells.append(Cell(x, y, self.cellW, self.cellH, CellState.DEAD))

    def initPattern(self, path: str, patternType: PatternType) -> None:
        for p in glob.glob(path):
            pattern = Pattern(path.split("/")[-1], p, patternType)
            if pattern.getRows():
                self.patterns.append(pattern)

    def initPatterns(self) -> None:
        patternDirTypes = {
            "oscillators": PatternType.Oscillator,
            "spaceships": PatternType.Spacehship,
            "flipflops": PatternType.FlipFlop,
            "methuselah": PatternType.Methuselah,
            "still-lifes": PatternType.StillLife,
        }

        for patternDir, patternType in patternDirTypes.items():
            self.initPattern(f"patterns/{patternDir}/*", patternType)

        self.patternsMenu.setPatterns(self.patterns)

    def eventLoop(self) -> None:
        for event in pygame.event.get():
            # print(event)
            if self.patternsMenu.enabled():
                handlerResp = self.patternsMenu.eventHandler(event)
                if handlerResp:
                    self.mouseButtonHeldDown = False
                    if isinstance(handlerResp, Pattern):
                        self.patternSelected = handlerResp
                        self.patternSelected.setCellHeight(self.cellH)
                        self.patternSelected.setCellWidth(self.cellW)
                    break
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.selectedPattern = None
                if event.key == K_g:
                    self.grid.toggle()
            elif (
                event.type == MOUSEBUTTONUP
                and event.dict.get("button") == MOUSEBUTTON_LCLICK
            ) or (self.mouseButtonHeldDown):
                if event.type == MOUSEBUTTONUP and self.mouseButtonHeldDown:
                    self.mouseButtonHeldDown = False
                (mX, mY) = pygame.mouse.get_pos()
                for button in self.buttons:
                    if button.clicked(mX, mY):
                        bID = button.getID()
                        if bID == ButtonID.CLEAR:
                            self._clear = True
                        elif bID == ButtonID.NEXT:
                            self._next = True
                        elif bID == ButtonID.START:
                            self.start()
                            button.setID(ButtonID.STOP)
                        elif bID == ButtonID.STOP:
                            self.stop()
                            button.setID(ButtonID.START)
                        elif bID == ButtonID.PATTERNS:
                            self.patternsMenu.toggle()
                        elif bID == ButtonID.RESET:
                            self.reset()
                        elif bID == ButtonID.EXIT:
                            self.running = False

                if mY < self.actionBarY:
                    cellX = int(mX / self.cellW) + self.viewCellX
                    cellY = int(mY / self.cellH) + self.viewCellY
                    try:
                        if self.selectedPattern:
                            selectedCells = self.selectedPattern.getCells()
                            for y in range(len(selectedCells)):
                                r = ''
                                for x in range(len(selectedCells[y])):
                                    selectedCell = selectedCells[y][x]
                                    nextCellX = cellX + x
                                    nextCellY = cellY + y
                                    if nextCellX < self.cols and nextCellY < self.rows:
                                        cell = getCellAtPoint(nextCellX, nextCellY, self.cells, self.rows)
                                        cell.setState(selectedCell.getState())
                        else:
                            cell = getCellAtPoint(cellX, cellY, self.cells, self.rows)
                            cell.setState(CellState.ALIVE)
                    except Exception as e:
                        print(e)
            elif (
                event.type == MOUSEBUTTONDOWN
                and event.dict.get("button") == MOUSEBUTTON_LCLICK
            ):
                (mX, mY) = pygame.mouse.get_pos()
                if mY < self.actionBarY:
                    self.mouseButtonHeldDown = True
            elif event.type == MOUSEBUTTONUP:
                buttonCode = event.dict.get("button")
                if (
                    buttonCode == MOUSEBUTTON_SCROLL_DOWN
                    and self.zoom >= self.zoomMin + self.zoomStep
                ):
                    self.zoom -= self.zoomStep
                elif (
                    buttonCode == MOUSEBUTTON_SCROLL_UP
                    and self.zoom < self.zoomMax - self.zoomStep
                ):
                    self.zoom += self.zoomStep

    async def loop(self) -> None:
        while self.running():
            self.eventLoop()
            self.update()
            self.draw()
            self.clock.tick(self.cfg.get("fps", default=5))
        pygame.quit()

    def update(self) -> None:
        if self.isReset() or self.cleared():
            self.initCells()

        for button in self.buttons:
            button.update()

        self.patternsMenu.update()

        if not self.stopped() or self.next():
            self.generation += 1
            # if there are no changes from the previous generation,
            # scan then entire cell array with quadratic complexity O(N^2)
            changed = []
            for pos in range(self.rows * self.cols):
                x = pos % self.rows
                y = int(pos / self.rows)
                (neighbors, alive) = getCellAndNeighbors(x, y, self.rows, self.cells)

                cell = self.cells[pos]

                # 1. Alive cells with < 2 alive neighbors die (under-population).
                # 2. Alive cells with 2 or 3 neighbors survives to the next generation.
                # 3. Alive cells with > 3 neighbors dies (over-population).
                # 4. Dead cells with exactly 3 live neighbors becomes a live cell (reproduction).
                if cell.getState() == CellState.ALIVE:
                    if alive < 2:
                        cell.setNextState(CellState.DEAD)
                        changed.append(cell)
                    elif alive == 2 or alive == 3:
                        cell.setNextState(CellState.ALIVE)
                        changed.append(cell)
                    elif alive > 3:
                        cell.setNextState(CellState.DEAD)
                        changed.append(cell)
                elif cell.getState() == CellState.DEAD:
                    if alive == 3:
                        cell.setNextState(CellState.ALIVE)
                        changed.append(cell)
                    else:
                        cell.setNextState(CellState.DEAD)
                        changed.append(cell)

            allCellsDead = True
            self.cellsAlive = 0
            self.cellsBirthed = 0
            self.cellsDied = 0

            for cell in changed:
                currState = cell.getState()
                nextState = cell.getNextState()
                cell.setState(nextState)
                if nextState == CellState.ALIVE:
                    self.cellsAlive += 1
                    if currState == CellState.DEAD:
                        self.cellsBirthed += 1
                    allCellsDead = False
                else:
                    if currState == CellState.ALIVE:
                        self.cellsDied += 1

            # if allCellsDead:
            #     self.stop()

    def draw(self) -> None:
        self.screen.fill(WHITE)
        self.cellSurf.fill(WHITE)

        for y in range(self.rowsVisible):
            for x in range(self.colsVisible):
                #cell = self.cells[self.viewCellY + y][self.viewCellX + x]
                cell = getCellAtPoint(self.viewCellX + x, self.viewCellY + y, self.cells, self.rows)
                cell.draw(self.cellSurf)

        visibleCellSurfaceRect = pygame.Rect(
            self.viewCellX * self.cellW,
            self.viewCellY * self.cellH,
            self.colsVisible * self.cellW,
            self.rowsVisible * self.cellH,
        )
        self.screen.blit(self.cellSurf, (0, 0), visibleCellSurfaceRect)
        self.grid.draw(self.screen)
        self.drawActionBar()
        self.drawButtons()
        self.patternsMenu.draw(self.screen)

        if self.selectedPattern:
            patternSurf = self.selectedPattern.getSurface()
            self.screen.blit(patternSurf, pygame.mouse.get_pos())

        pygame.display.update()

    def drawActionBar(self) -> None:
        bg = pygame.Rect(
            self.actionBarX, self.actionBarY, self.width, self.actionBarHeight
        )
        pygame.draw.rect(self.screen, GREY_LIGHT1, bg)
        pygame.draw.line(
            self.screen,
            GREY,
            (self.actionBarX, self.actionBarY),
            (self.actionBarX + self.width, self.actionBarY),
        )

    def drawButtons(self) -> None:
        for button in self.buttons:
            button.draw(self.screen)

        stats = [
            f"Alive: {self.cellsAlive}",
            f"Births: {self.cellsBirthed}",
            f"Deaths: {self.cellsDied}",
            f"Generation: {self.generation}",
        ]

        statIdx = 0
        statFont = pygame.font.Font(None, 11)
        for stat in stats:
            fontSize = statFont.size(stat)
            textImg = self.font.render(stat, True, BLACK)
            self.screen.blit(
                textImg, (10, (self.actionBarY + 5) + ((fontSize[1] * 2) * statIdx))
            )
            statIdx += 1

        zoomText = self.font.render("Zoom: {:.2f}".format(self.zoom), True, BLACK)
        self.screen.blit(zoomText, (self.width - 100, self.actionBarY + 5))
        vcText = self.font.render(
            "visible cols: {}".format(self.colsVisible), True, BLACK
        )
        self.screen.blit(vcText, (self.width - 130, self.actionBarY + 25))
        vrText = self.font.render(
            "visible rows: {}".format(self.rowsVisible), True, BLACK
        )
        self.screen.blit(vrText, (self.width - 130, self.actionBarY + 45))

    def clear(self) -> None:
        self._clear = True

    def cleared(self) -> bool:
        val = self._clear
        self._clear = False
        return val

    def next(self) -> bool:
        val = self._next
        self._next = False
        return val

    def reset(self) -> None:
        self._reset = True

    def isReset(self) -> bool:
        val = self._reset
        self._reset = False
        return val

    def start(self) -> None:
        self._stopped = False

    def stop(self) -> None:
        self._stopped = True

    def stopped(self) -> bool:
        return self._stopped
