import asyncio
import concurrent.futures
import glob
import pygame
import time

from pygame.font import Font
from pygame.locals import KEYDOWN, MOUSEBUTTONUP, MOUSEBUTTONDOWN, K_g, K_a, K_d, K_s, K_w, K_ESCAPE
from gameoflife.colors import BLUE, BLACK, GREY, GREY_DARK1, GREY_DARK2, GREY_LIGHT1, WHITE
from gameoflife.constvars import *
from gameoflife.config import Config
from gameoflife.grid import Grid
from gameoflife.button import RectButton, ButtonText
from gameoflife.cell import *
from gameoflife.pattern import Pattern, PatternMenu, PatternType
from gameoflife.cell import getCellAtPoint
from gameoflife.helpers import drawRectBorder

class MouseModes:
    DRAW = 0
    PAN = 1

class Game:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Game of Life")

        iconImg = pygame.image.load("images/gameoflife.png")
        if iconImg:
            pygame.display.set_icon(iconImg)

        self.buttons = []
        self.cfg = Config()
        self.font = Font(None, 24)
        self.fps = self.cfg.get("fps", default=5)
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
        self.cameraX = int((self.cols / 2) - (self.colsVisible / 2))
        self.cameraY = int((self.rows / 2) - (self.rowsVisible / 2))
        self._clear = False
        self._next = False
        self._running = True
        self._stopped = True
        self.patternsMenu = PatternMenu(50, 50, maxHeight=400)
        self.patternsMenu.setFont(self.font)
        self.pattern = None
        self.generation = 0
        self.cells = []
        self.cellsAlive = 0
        self.cellsBirthed = 0
        self.cellsDied = 0
        self.mouseButtonHold = False

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
        btnMargin = 15
        btnWidth = 100

        self.buttons = [
            RectButton(ButtonText.CLEAR),
            RectButton(ButtonText.START),
            RectButton(ButtonText.NEXT),
            RectButton(ButtonText.PATTERNS),
            RectButton(ButtonText.EXIT),
        ]

        widthRem = self.width - (
            (len(self.buttons) * (btnWidth + btnMargin)) - btnMargin
        )
        buttonX = widthRem / 2
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

    def initPatternsByType(self, path: str, type: PatternType) -> List[Pattern]:
        patterns:List[Pattern] = []
        for p in glob.glob(path):
            pattern = Pattern(path.split("/")[-1], p, type)
            if pattern.getRows():
                patterns.append(pattern)
        return patterns

    def initPatterns(self) -> None:
        patternTypes = {
            "oscillators": PatternType.Oscillator,
            "spaceships": PatternType.Spacehship,
            "flipflops": PatternType.FlipFlop,
            "methuselah": PatternType.Methuselah,
            "still-lifes": PatternType.StillLife,
        }

        patterns = []
        for name, type in patternTypes.items():
            patterns += self.initPatternsByType(f"patterns/{name}/*", type)

        self.patternsMenu.setPatterns(patterns)

    def eventLoop(self) -> None:
        for event in pygame.event.get():
            if self.patternsMenu.enabled():
                ret = self.patternsMenu.eventHandler(event)
                if ret:
                    self.mouseButtonHold = False
                    if isinstance(ret, Pattern):
                        self.pattern = ret
                        self.pattern.setCellHeight(self.cellH)
                        self.pattern.setCellWidth(self.cellW)
                    break
            if event.type == pygame.QUIT:
                self.quit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.pattern = None
                elif event.key == K_g:
                    self.grid.toggle()
                elif event.key == K_a: # left
                    if self.cameraX:
                        self.cameraX -= 1
                elif event.key == K_d: # right
                    if self.cameraX < self.cols - self.colsVisible:
                        self.cameraX += 1
                elif event.key == K_s: # down
                    if self.cameraY < self.rows - self.rowsVisible:
                        self.cameraY += 1
                elif event.key == K_w: # up
                    if self.cameraY:
                        self.cameraY -= 1
            elif (
                event.type == MOUSEBUTTONUP
                and event.dict.get("button") == MOUSEBUTTON_LCLICK
            ) or (self.mouseButtonHold):
                if event.type == MOUSEBUTTONUP and self.mouseButtonHold:
                    self.mouseButtonHold = False
                (mX, mY) = pygame.mouse.get_pos()
                for button in self.buttons:
                    if button.clicked(mX, mY):
                        btnTxt = button.getText()
                        if btnTxt == ButtonText.CLEAR:
                            self.clear()
                            for b in self.buttons:
                                if b.getText() == ButtonText.STOP:
                                    b.setText(ButtonText.START)
                                    self.stop()
                                    break
                        elif btnTxt == ButtonText.NEXT:
                            self._next = True
                        elif btnTxt == ButtonText.START:
                            self.start()
                            button.setText(ButtonText.STOP)
                        elif btnTxt == ButtonText.STOP:
                            self.stop()
                            button.setText(ButtonText.START)
                        elif btnTxt == ButtonText.PATTERNS:
                            self.patternsMenu.toggle()
                        elif btnTxt == ButtonText.EXIT:
                            self.quit()

                if mY < self.actionBarY:
                    cellX = int(mX / self.cellW) + self.cameraX
                    cellY = int(mY / self.cellH) + self.cameraY
                    try:
                        if self.pattern:
                            selectedCells = self.pattern.getCells()
                            for y in range(len(selectedCells)):
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
                    self.mouseButtonHold = True
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
            self.clock.tick(self.fps)
        pygame.quit()

    def update(self) -> None:
        if self.cleared():
            self.initCells()

        for button in self.buttons:
            button.update()

        if self.patternsMenu.enabled():
            self.patternsMenu.update()

        if not self.stopped() or self.next():
            self.generation += 1
            self.cellsAlive = 0
            self.cellsBirthed = 0
            self.cellsDied = 0

            changed = []
            #loopOneStart = time.time()
            for pos in range(self.rows * self.cols):
                x = pos % self.rows
                y = int(pos / self.rows)
                alive = getAliveNeighbors(x, y, self.rows, self.cells)
                cell = self.cells[pos]

                # 1. Alive cells with < 2 alive neighbors die (under-population).
                # 2. Alive cells with 2 or 3 neighbors survives to the next generation.
                # 3. Alive cells with > 3 neighbors dies (over-population).
                # 4. Dead cells with exactly 3 live neighbors becomes a live cell (reproduction).
                cellState = cell.getState()
                if cellState == CellState.ALIVE:
                    if alive < 2 or alive > 3:
                        cell.setNextState(CellState.DEAD)
                        self.cellsDied += 1
                        changed.append(cell)
                    elif alive == 2 or alive == 3:
                        cell.setNextState(CellState.ALIVE)
                        self.cellsAlive += 1
                        changed.append(cell)
                elif cellState == CellState.DEAD:
                    if alive == 3:
                        cell.setNextState(CellState.ALIVE)
                        self.cellsBirthed += 1
                        changed.append(cell)
                    else:
                        cell.setNextState(CellState.DEAD)
                        changed.append(cell)
            # loopOneElapsed = time.time() - loopOneStart
            # loopTwoStart = time.time()
            for cell in changed:
                currState = cell.getState()
                nextState = cell.getNextState()
                cell.setState(nextState)
            # loopTwoElapsed = time.time() - loopTwoStart
            # print('update() loop 1 took {:.2} seconds'.format(loopOneElapsed))
            # print('update() loop 2 took {:.2} seconds'.format(loopTwoElapsed))
            if not self.cellsAlive:
                self.stop()

    def draw(self) -> None:
        self.screen.fill(WHITE)

        for y in range(self.rowsVisible):
            for x in range(self.colsVisible):
                cellX = self.cameraX + x
                cellY = self.cameraY + y
                cell = getCellAtPoint(cellX, cellY, self.cells, self.rows)
                cell.draw(self.cellSurf)

        cellSurfX = self.cameraX * self.cellW
        cellSurfY = self.cameraY * self.cellH
        cellSurfW = self.colsVisible * self.cellW
        cellSurfH = self.rowsVisible * self.cellH
        cellSurfR = pygame.Rect(cellSurfX, cellSurfY, cellSurfW, cellSurfH)

        self.screen.blit(self.cellSurf, (0, 0), cellSurfR)
        self.grid.draw(self.screen)
        self.drawActionBar()

        if self.patternsMenu.enabled():
            self.patternsMenu.draw(self.screen)

        if self.pattern and pygame.mouse.get_pos()[1] < self.actionBarY:
            patternSurf = self.pattern.getSurface()
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
        # vcText = self.font.render(
        #     "visible cols: {}".format(self.colsVisible), True, BLACK
        # )
        # self.screen.blit(vcText, (self.width - 130, self.actionBarY + 25))
        # vrText = self.font.render(
        #     "visible rows: {}".format(self.rowsVisible), True, BLACK
        # )
        # self.screen.blit(vrText, (self.width - 130, self.actionBarY + 45))

    def clear(self) -> None:
        self._clear = True
        self.cellsAlive = 0
        self.cellsBirthed = 0
        self.cellsDied = 0
        self.generation = 0

    def cleared(self) -> bool:
        val = self._clear
        self._clear = False
        return val

    def next(self) -> bool:
        val = self._next
        self._next = False
        return val

    def running(self) -> bool:
        return self._running

    def quit(self) -> None:
        self._running = False

    def start(self) -> None:
        self._stopped = False

    def stop(self) -> None:
        self._stopped = True

    def stopped(self) -> bool:
        return self._stopped
