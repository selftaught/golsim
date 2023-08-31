import asyncio
import concurrent.futures
import glob
import pygame
import time

from pygame.font import Font
from pygame.locals import KEYDOWN, MOUSEBUTTONUP, MOUSEBUTTONDOWN, K_g, K_a, K_d, K_s, K_w, K_ESCAPE, TEXTINPUT, MOUSEMOTION
from gameoflife.colors import BLUE, BLACK, GREY, GREY_DARK1, GREY_DARK2, GREY_LIGHT1, WHITE
from gameoflife.mouse import MOUSEBUTTON_LCLICK, MOUSEBUTTON_RCLICK, MOUSEBUTTON_SCROLL_DOWN, MOUSEBUTTON_SCROLL_UP, MouseMode
from gameoflife.config import Config
from gameoflife.grid import Grid
from gameoflife.button import RectButton, ButtonText
from gameoflife.cell import *
from gameoflife.pattern import Pattern, PatternMenu, PatternType
from gameoflife.cell import getCellAtPoint
from gameoflife.helpers import drawRectBorder


class Game:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Game of Life")

        iconImg = pygame.image.load("images/gameoflife.png")
        if iconImg:
            pygame.display.set_icon(iconImg)

        self._buttons = []
        self._cfg = Config()
        self._clock = pygame.time.Clock()
        self._fontSize = self._cfg.get('font.size', default=24)
        self._font = Font(None, self._fontSize)
        self._fps = self._cfg.get("fps", default=5)
        self._height = self._cfg.get("screen.height")
        self._width = self._cfg.get("screen.width")
        self._screen = pygame.display.set_mode([self._width, self._height])
        self._cellH = self._cfg.get("cell.height", default=5)
        self._cellW = self._cfg.get("cell.width", default=5)
        self._actionBarHeight = 70
        self._actionBarX = 0
        self._actionBarY = self._height - self._actionBarHeight
        self._cells = None
        self._cols = 200
        self._colsVisible = int(self._width / self._cellW)
        self._rows = 200
        self._rowsVisible = int(self._height / self._cellH)
        self._grid = Grid(self._colsVisible, self._rowsVisible, self._cellW, self._cellH)
        self._cellsurf = pygame.Surface((self._cols * self._cellW, self._rows * self._cellH))
        self._cameraX = int((self._cols / 2) - (self._colsVisible / 2))
        self._cameraY = int((self._rows / 2) - (self._rowsVisible / 2))
        self._clear = False
        self._next = False
        self._running = True
        self._stopped = True
        self._patternsMenu = PatternMenu(50, 50, maxHeight=400, font=self._font)
        self._pattern = None
        self._generation = 0
        self._cells = []
        self._cellsAlive = 0
        self._cellsBirthed = 0
        self._cellsDied = 0
        self._mouseButtonHold = False

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

        self._buttons = [
            RectButton(ButtonText.CLEAR),
            RectButton(ButtonText.START),
            RectButton(ButtonText.NEXT),
            RectButton(ButtonText.PATTERNS),
            RectButton(ButtonText.EXIT),
        ]

        widthRem = self._width - (
            (len(self._buttons) * (btnWidth + btnMargin)) - btnMargin
        )
        buttonX = widthRem / 2
        buttonY = (self._actionBarY) + ((self._actionBarHeight / 2) - btnHeight / 2)

        for button in self._buttons:
            button.setFont(self._font)
            button.setHoverBackgroundColor(GREY_DARK2)
            button.setBorderColor(GREY_DARK2)
            if isinstance(button, RectButton):
                button.setRect(pygame.Rect(buttonX, buttonY, btnWidth, btnHeight))
            buttonX += btnWidth + btnMargin

    def initCells(self) -> None:
        self._cells = []
        for i in range(self._cols * self._rows):
            x = i % self._rows
            y = int(i / self._rows)
            self._cells.append(Cell(x, y, self._cellW, self._cellH, CellState.DEAD))

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

        self._patternsMenu.setPatterns(patterns)

    def eventLoop(self) -> None:
        for event in pygame.event.get():
            (mX, mY) = pygame.mouse.get_pos()
            if self._patternsMenu.enabled():
                ret = self._patternsMenu.eventHandler(event)
                if ret:
                    self._mouseButtonHold = False
                    if isinstance(ret, Pattern):
                        self._pattern = ret
                        self._pattern.setCellHeight(self._cellH)
                        self._pattern.setCellWidth(self._cellW)
                    continue
            if event.type == pygame.QUIT:
                self.quit()

            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self._pattern = None
                elif event.key == K_g:
                    self._grid.toggle()
                elif event.key == K_a: # left
                    if self._cameraX:
                        self._cameraX -= 1
                elif event.key == K_d: # right
                    if self._cameraX < self._cols - self._colsVisible:
                        self._cameraX += 1
                elif event.key == K_s: # down
                    if self._cameraY < self._rows - self._rowsVisible:
                        self._cameraY += 1
                elif event.key == K_w: # up
                    if self._cameraY:
                        self._cameraY -= 1

            elif event.type == TEXTINPUT:
                if event.dict.get('text') == 'a':
                    if self._cameraX:
                        self._cameraX -= 1
                elif event.dict.get('text') == 'd':
                    if self._cameraX < self._cols - self._colsVisible:
                        self._cameraX += 1
                elif event.dict.get('text') == 's':
                    if self._cameraY < self._rows - self._rowsVisible:
                        self._cameraY += 1
                elif event.dict.get('text') == 'w':
                    if self._cameraY:
                        self._cameraY -= 1

            elif (event.type == MOUSEBUTTONDOWN and event.dict.get("button") == MOUSEBUTTON_LCLICK):

                # if event.type == MOUSEBUTTONUP and self._mouseButtonHold:
                #     self._mouseButtonHold = False

                if mY < self._actionBarY:
                    self._mouseButtonHold = True

                for button in self._buttons:
                    if button.clicked(mX, mY):
                        btnTxt = button.getText()
                        if btnTxt == ButtonText.CLEAR:
                            self.clear()
                            for b in self._buttons:
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
                            self._patternsMenu.toggle()
                        elif btnTxt == ButtonText.EXIT:
                            self.quit()

                if mY < self._actionBarY:
                    cellX = int(mX / self._cellW) + self._cameraX
                    cellY = int(mY / self._cellH) + self._cameraY
                    try:
                        if self._pattern:
                            selectedCells = self._pattern.getCells()
                            for y in range(len(selectedCells)):
                                for x in range(len(selectedCells[y])):
                                    selectedCell = selectedCells[y][x]
                                    nextCellX = cellX + x
                                    nextCellY = cellY + y
                                    if nextCellX < self._cols and nextCellY < self._rows:
                                        cell = getCellAtPoint(nextCellX, nextCellY, self._cells, self._rows)
                                        cell.setState(selectedCell.getState())
                        else:
                            cell = getCellAtPoint(cellX, cellY, self._cells, self._rows)
                            cell.setState(CellState.ALIVE)
                    except Exception as e:
                        print(e)

            elif event.type == MOUSEBUTTONUP:
                buttonCode = event.dict.get("button")
                if (
                    buttonCode == MOUSEBUTTON_SCROLL_DOWN
                    and self.zoom >= self.zoomMin + self.zoomStep
                ):
                    self.zoom -= self.zoomStep
                elif (
                    buttonCode == MOUSEBUTTON_SCROLL_UP
                    and self.zoom < self.zooamMax - self.zoomStep
                ):
                    self.zoom += self.zoomStep
                elif buttonCode == MOUSEBUTTON_RCLICK:
                    cellX = int(mX / self._cellW) + self._cameraX
                    cellY = int(mY / self._cellH) + self._cameraY
                    cell = getCellAtPoint(cellX, cellY, self._cells, self._rows)
                    cell.setState(CellState.DEAD)
                elif buttonCode == MOUSEBUTTON_LCLICK:
                    self._mouseButtonHold = False

            elif event.type == MOUSEMOTION:
                if self._mouseButtonHold:
                    if mY < self._actionBarY:
                        cellX = int(mX / self._cellW) + self._cameraX
                        cellY = int(mY / self._cellH) + self._cameraY
                        cell = getCellAtPoint(cellX, cellY, self._cells, self._rows)
                        cell.setState(CellState.ALIVE)

    async def loop(self) -> None:
        while self.running():
            self.eventLoop()
            self.update()
            self.draw()
            self._clock.tick(self._fps)
        pygame.quit()

    def update(self) -> None:
        if self.cleared():
            self.initCells()

        for button in self._buttons:
            button.update()

        if self._patternsMenu.enabled():
            self._patternsMenu.update()

        if not self.stopped() or self.next():
            self._generation += 1
            self._cellsAlive = 0
            self._cellsBirthed = 0
            self._cellsDied = 0

            changed = []
            #loopOneStart = time.time()
            for pos in range(self._rows * self._cols):
                x = pos % self._rows
                y = int(pos / self._rows)
                alive = getAliveNeighbors(x, y, self._rows, self._cells)
                cell = self._cells[pos]

                # 1. Alive cells with < 2 alive neighbors die (under-population).
                # 2. Alive cells with 2 or 3 neighbors survives to the next generation.
                # 3. Alive cells with > 3 neighbors dies (over-population).
                # 4. Dead cells with exactly 3 live neighbors becomes a live cell (reproduction).
                cellState = cell.getState()
                if cellState == CellState.ALIVE:
                    if alive < 2 or alive > 3:
                        cell.setNextState(CellState.DEAD)
                        self._cellsDied += 1
                        changed.append(cell)
                    elif alive == 2 or alive == 3:
                        cell.setNextState(CellState.ALIVE)
                        self._cellsAlive += 1
                        changed.append(cell)
                elif cellState == CellState.DEAD:
                    if alive == 3:
                        cell.setNextState(CellState.ALIVE)
                        self._cellsBirthed += 1
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
            if not self._cellsAlive:
                self.stop()

    def draw(self) -> None:
        self._screen.fill(WHITE)

        for y in range(self._rowsVisible):
            for x in range(self._colsVisible):
                cellX = self._cameraX + x
                cellY = self._cameraY + y
                cell = getCellAtPoint(cellX, cellY, self._cells, self._rows)
                cell.draw(self._cellsurf)

        cellSurfX = self._cameraX * self._cellW
        cellSurfY = self._cameraY * self._cellH
        cellSurfW = self._colsVisible * self._cellW
        cellSurfH = self._rowsVisible * self._cellH
        cellSurfR = pygame.Rect(cellSurfX, cellSurfY, cellSurfW, cellSurfH)

        self._screen.blit(self._cellsurf, (0, 0), cellSurfR)
        self._grid.draw(self._screen)
        self.drawActionBar()

        if self._patternsMenu.enabled():
            self._patternsMenu.draw(self._screen)

        if self._pattern and pygame.mouse.get_pos()[1] < self._actionBarY:
            patternSurf = self._pattern.getSurface()
            self._screen.blit(patternSurf, pygame.mouse.get_pos())

        pygame.display.update()

    def drawActionBar(self) -> None:
        bg = pygame.Rect(
            self._actionBarX, self._actionBarY, self._width, self._actionBarHeight
        )
        pygame.draw.rect(self._screen, GREY_LIGHT1, bg)
        pygame.draw.line(
            self._screen,
            GREY,
            (self._actionBarX, self._actionBarY),
            (self._actionBarX + self._width, self._actionBarY),
        )

        for button in self._buttons:
            button.draw(self._screen)

        stats = [
            f"Alive: {self._cellsAlive}",
            f"Births: {self._cellsBirthed}",
            f"Deaths: {self._cellsDied}",
            f"Generation: {self._generation}",
        ]

        statIdx = 0
        statFont = pygame.font.Font(None, 11)
        for stat in stats:
            fontSize = statFont.size(stat)
            textImg = self._font.render(stat, True, BLACK)
            self._screen.blit(
                textImg, (10, (self._actionBarY + 5) + ((fontSize[1] * 2) * statIdx))
            )
            statIdx += 1

        zoomText = self._font.render("Zoom: {:.2f}".format(self.zoom), True, BLACK)
        self._screen.blit(zoomText, (self._width - 100, self._actionBarY + 5))
        # vcText = self._font.render(
        #     "visible cols: {}".format(self._colsVisible), True, BLACK
        # )
        # self._screen.blit(vcText, (self._width - 130, self._actionBarY + 25))
        # vrText = self._font.render(
        #     "visible rows: {}".format(self._rowsVisible), True, BLACK
        # )
        # self._screen.blit(vrText, (self._width - 130, self._actionBarY + 45))

    def clear(self) -> None:
        self._clear = True
        self._cellsAlive = 0
        self._cellsBirthed = 0
        self._cellsDied = 0
        self._generation = 0

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
