import concurrent.futures
import glob
import pygame
import time

from collections import namedtuple
from pygame.event import Event
from pygame.freetype import SysFont
from pygame.locals import KEYDOWN, MOUSEBUTTONUP, MOUSEBUTTONDOWN, K_g, K_a, K_d, K_s, K_w, K_ESCAPE, K_MINUS, K_PLUS, TEXTINPUT, MOUSEMOTION
from pygame.surface import Surface
from typing import List

from gol.bresenham import bresenham
from gol.button import BaseButton, ButtonID, RectButton, ToggleRectButton
from gol.cell import Cell, CellState, getAliveNeighbors, getCellAtPoint
from gol.color import Color
from gol.config import Config
from gol.draw import drawRectBorder
from gol.event import *
from gol.grid import Grid
from gol.input import InputMode, InputModeManager
from gol.mouse import MOUSEBUTTON_LCLICK, MOUSEBUTTON_RCLICK, MOUSEBUTTON_SCROLL_DOWN, MOUSEBUTTON_SCROLL_UP
from gol.pattern import Pattern, PatternMenu, PatternType

class ZoomDir:
    IN = 0
    OUT = 1

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
        self._fontSize = self._cfg.get('font.size', default=12)
        self._font = SysFont('Hack', self._fontSize)
        self._fps = self._cfg.get("fps", default=60)
        self._height = self._cfg.get("screen.height")
        self._width = self._cfg.get("screen.width")
        self._screen = pygame.display.set_mode([self._width, self._height])
        self._cellH = self._cfg.get("cell.height", default=5)
        self._cellW = self._cfg.get("cell.width", default=5)
        self._actionBarHeight = 70
        self._actionBarX = 0
        self._actionBarY = self._height - self._actionBarHeight
        self._cols = 200
        self._rows = 200
        self._grid = Grid(self._cols / self._cellW, self._rows / self._cellH, self._cellW, self._cellH)
        self._cameraMoveDist = 5
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
        self._mouseClickPos = None
        self._mouseClickPos2 = None
        self._inputModeMngr = InputModeManager(font=self._font)
        self._lastMarkedCell = None

        self._zoom = 1
        self._zoomMax = 10
        self._zoomMin = 1
        self._zoomStep = 1

        self.initPatterns()
        self.initButtons()
        self.initCells()

    def initButtons(self) -> None:
        btnHeight = 30
        btnMargin = 15
        btnWidth = 100

        self._startStopBtnIdx = 1
        self._buttons = [
            RectButton(ButtonID.CLEAR, EVENT_CLEAR),
            ToggleRectButton(ButtonID.START, onDisable=[ButtonID.START, EVENT_STOP], onEnable=[ButtonID.STOP, EVENT_START]),
            RectButton(ButtonID.NEXT, EVENT_NEXT),
            RectButton(ButtonID.PATTERNS, EVENT_PATTERNS),
            RectButton(ButtonID.EXIT, EVENT_EXIT),
        ]

        widthRem = self._width - ((len(self._buttons) * (btnWidth + btnMargin)) - btnMargin)
        buttonX = widthRem / 2
        buttonY = (self._actionBarY) + ((self._actionBarHeight / 2) - btnHeight / 2)

        for button in self._buttons:
            button.setFont(self._font)
            button.setHoverBackgroundColor(Color.GREY_DARK2)
            if isinstance(button, RectButton):
                button.setRect(pygame.Rect(buttonX, buttonY, btnWidth, btnHeight))
            buttonX += btnWidth + btnMargin

        self._inputModeMngr.setBtnStartCoords((buttonX, buttonY))
        self._inputModeMngr.addMode(ButtonID.DRAW, EVENT_INPUT_MODE_DRAW, imagePath="images/draw.png", active=True)
        self._inputModeMngr.addMode(ButtonID.PAN, EVENT_INPUT_MODE_PAN, imagePath="images/pan.png")
        self._inputModeMngr.addMode(ButtonID.SELECT, EVENT_INPUT_MODE_PAN, imagePath="images/select.png")
        self._inputModeMngr.addMode(ButtonID.ZOOM_IN, EVENT_INPUT_MODE_PAN, imagePath="images/zoomin.png")
        self._inputModeMngr.addMode(ButtonID.ZOOM_OUT, EVENT_INPUT_MODE_PAN, imagePath="images/zoomout.png")

    def initCells(self) -> None:
        self._cells = []
        for i in range(self._cols * self._rows):
            x = i % self._rows
            y = int(i / self._rows)
            self._cells.append(Cell(x, y, self._cellW, self._cellH, CellState.DEAD))

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
            path = f"patterns/{name}/*"
            for p in glob.glob(path):
                pattern = Pattern(path.split("/")[-1], p, type)
                if pattern.getRows():
                    patterns.append(pattern)

        self._patternsMenu.setPatterns(patterns)

    def eventLoop(self) -> None:
        for event in pygame.event.get():
            buttonCode = event.dict.get("button")
            inputMode = self._inputModeMngr.mode()

            (mX, mY) = pygame.mouse.get_pos()
            cellX = int(mX / self._cellW)
            cellY = int(mY / self._cellH)

            if self._patternsMenu.enabled():
                ret = self._patternsMenu.eventHandler(event)
                if ret:
                    self._mouseButtonHold = False
                    if isinstance(ret, Pattern):
                        self._pattern = ret
                        self._pattern.setCellHeight(self._cellH)
                        self._pattern.setCellWidth(self._cellW)
                    continue
            elif self._inputModeMngr.eventHandler(event):
                continue
            # -----------------------------------------------------
            if inputMode == InputMode.DRAW:
                if event.type == MOUSEBUTTONDOWN and buttonCode == MOUSEBUTTON_LCLICK and mY < self._actionBarY:
                    if self._pattern:
                        selectedCells = self._pattern.getCells()
                        for y in range(len(selectedCells)):
                            for x in range(len(selectedCells[y])):
                                selectedCell = selectedCells[y][x]
                                nextCellX = cellX + x
                                nextCellY = cellY + y
                                if nextCellX >= self._cols or nextCellY >= self._rows:
                                    break
                                cell = getCellAtPoint(nextCellX, nextCellY, self._cells, self._rows)
                                if selectedCell.getState() == CellState.ALIVE:
                                    cell.setState(CellState.ALIVE)
                    else:
                        cell = getCellAtPoint(cellX, cellY, self._cells, self._rows)
                        if cell:
                            cell.setState(CellState.ALIVE)
                elif event.type == MOUSEMOTION:
                    if self._mouseButtonHold and mY < self._actionBarY:
                        cell = getCellAtPoint(cellX, cellY, self._cells, self._rows)
                        if cell:
                            cell.setState(CellState.ALIVE)
                        if self._lastMarkedCell:
                            (prevX, prevY) = self._lastMarkedCell
                            if cellX - prevX != 0 or cellY - prevY != 0:
                                for point in list(bresenham(prevX, prevY, cellX, cellY)):
                                    (x, y) = point
                                    c = getCellAtPoint(x, y, self._cells, self._rows)
                                    if c:
                                        c.setState(CellState.ALIVE)
                        self._lastMarkedCell = (cellX, cellY)
                elif event.type == MOUSEBUTTONUP:
                    if buttonCode == MOUSEBUTTON_RCLICK:
                        cell = getCellAtPoint(cellX, cellY, self._cells, self._rows)
                        cell.setState(CellState.DEAD)
            elif inputMode == InputMode.PAN:
                pass

            elif inputMode == InputMode.SELECT:
                pass

            elif inputMode == InputMode.ZOOM_IN:
                pass

            elif inputMode == InputMode.ZOOM_OUT:
                pass
            # -----------------------------------------------------
            if event.type == pygame.QUIT:
                self.quit()

            elif event.type == KEYDOWN:
                print(event.key)
                if event.key == K_ESCAPE:
                    self._pattern = None
                    self._mouseClickPos = None
                    self._mouseClickPos2 = None
                elif event.key == K_g:
                    self._grid.toggle()
                elif event.key == K_MINUS:
                    self.zoom(ZoomDir.OUT)
                elif event.key == K_a:
                    self.zoom(ZoomDir.IN)
                # elif event.key == K_a: # left
                #     if self._cameraX:
                #         self._cameraX -= self._cameraMoveDist
                # elif event.key == K_d: # right
                #     if self._cameraX < self._cols - self._colsVisible:
                #         self._cameraX += self._cameraMoveDist
                # elif event.key == K_s: # down
                #     if self._cameraY < self._rows - self._rowsVisible:
                #         self._cameraY += self._cameraMoveDist
                # elif event.key == K_w: # up
                #     if self._cameraY:
                #         self._cameraY -= self._cameraMoveDist

            elif event.type == TEXTINPUT:
                eventText = event.dict.get('text')
                if eventText:
                    eventText = eventText.lower()

                # if eventText == 'a':
                #     if self._cameraX:
                #         self._cameraX -= self._cameraMoveDist
                # elif eventText == 'd':
                #     if self._cameraX < self._cols - self._colsVisible:
                #         self._cameraX += self._cameraMoveDist
                # elif eventText == 's':
                #     if self._cameraY < self._rows - self._rowsVisible:
                #         self._cameraY += self._cameraMoveDist
                # elif eventText == 'w':
                #     if self._cameraY:
                #         self._cameraY -= self._cameraMoveDist

            elif event.type == MOUSEBUTTONDOWN and buttonCode == MOUSEBUTTON_LCLICK:
                if mY < self._actionBarY:
                    self._mouseButtonHold = True
                    if inputMode == InputMode.SELECT:
                        if not self._mouseClickPos:
                            self._mouseClickPos = (mX, mY)
                        elif not self._mouseClickPos2:
                            self._mouseClickPos2 = (mX, mY)
                        else:
                            self._mouseClickPos = (mX, mY)
                            self._mouseClickPos2 = None
                    elif inputMode == InputMode.PAN:
                        self._mouseClickPos = (mX, mY)
                        print(f'self._mouseClickPos = ({mX}, {mY})')

                    if inputMode == InputMode.DRAW and not self.stopped():
                        self.stop()
                        self._buttons[self._startStopBtnIdx].toggle()

            elif event.type == MOUSEBUTTONUP:
                if (
                    buttonCode == MOUSEBUTTON_SCROLL_DOWN
                    and self._zoom >= self._zoomMin + self._zoomStep
                ):
                    self._zoom -= self._zoomStep
                elif (
                    buttonCode == MOUSEBUTTON_SCROLL_UP
                    and self._zoom < self._zoomMax - self._zoomStep
                ):
                    self._zoom += self._zoomStep
                elif buttonCode == MOUSEBUTTON_LCLICK:
                    self._mouseButtonHold = False
                    self._lastMarkedCell = None

            elif event == EVENT_START:
                self.start()
            elif event == EVENT_STOP:
                self.stop()
            elif event == EVENT_CLEAR:
                self.clear()
            elif event == EVENT_NEXT:
                self._next = True
            elif event == EVENT_PATTERNS:
                self._patternsMenu.toggle()
            elif event == EVENT_EXIT:
                self.quit()

            for button in self._buttons:
                button.eventHandler(event)

    def loop(self) -> None:
        while self.running():
            self.eventLoop()
            self.update()
            self.draw()
            self._clock.tick(self._fps)
        pygame.quit()

    def update(self) -> None:
        if self.cleared():
            self.initCells()
            return

        for button in self._buttons:
            button.update()

        self._inputModeMngr.update()

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
                        self._cellsAlive += 1
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
        screen = self._screen
        #cameraX, cameraY = self._cameraX, self._cameraY
        cellH, cellW = self._cellH, self._cellW
        #colsVis, rowsVis = self._colsVisible, self._rowsVisible
        screen.fill(Color.BLACK)

        universeWidth = self._cols * self._cellW
        universeHeight = self._rows * self._cellH
        universeSurface = Surface((universeWidth, universeHeight))

        # Loop through the universe of cells and draw them onto universeSurface
        for y in range(self._rows):
            for x in range(self._cols):
                cell = getCellAtPoint(x, y, self._cells, self._rows)
                cell.draw(universeSurface)

        # Overflow calculations
        universeWindowOverflowY = (self._height - universeHeight) * -1
        universeWindowOverflowX = (self._width - universeWidth) * -1

        # print(f'universeSurface = {universeSurface}')
        # print(f'screen.width = {self._width}')
        # print(f'screen.height = {self._height}')
        # print(f'universe.height = {universeHeight}')
        # print(f'universe.width = {universeWidth}')
        # print(f'universeWindowOverflowY = {universeWindowOverflowY}')
        # print(f'universeWindowOverflowX = {universeWindowOverflowX}')

        # Rect area of cell surface to blit on to screen
        universeScreenDestX, universeScreenDestY = 0, 0
        universeVisibleArea = pygame.Rect(0, 0, 0, 0)
        universeVisibleArea.width = self._width if universeWidth >= self._width else universeWidth
        universeVisibleArea.height = self._height if universeHeight >= self._height else universeHeight

        if universeWindowOverflowX > 0:
            universeVisibleArea.left = universeWindowOverflowX / 2
        else:
            universeScreenDestX = (universeWindowOverflowX / 2) * -1

        if universeWindowOverflowY > 0:
            universeVisibleArea.top = universeWindowOverflowY / 2
        else:
            universeScreenDestY = (universeWindowOverflowY / 2) * -1

        screen.blit(universeSurface, (universeScreenDestX, universeScreenDestY), universeVisibleArea)

        # print(f'universeScreenDestX = {universeScreenDestX}')
        # print(f'universeScreenDestY = {universeScreenDestY}')
        # print(f'universeVisibleArea = {universeVisibleArea}')
        # print('------')
        # Grid
        #self._grid.draw(screen)

        (mX, mY) = pygame.mouse.get_pos()

        # Draw selected pattern at mouse if above action bar
        if self._pattern and mY < self._actionBarY:
            patternSurf = self._pattern.getSurface()
            screen.blit(patternSurf, (mX, mY))

        inputMode = self._inputModeMngr.mode()
        # Select input mode - draw selection rect at last two mouse click points
        if inputMode == InputMode.SELECT:
            mcPos, mcPos2 = self._mouseClickPos, self._mouseClickPos2
            if mcPos:
                if not mcPos2:
                    selectRect = pygame.Rect(mX, mY, mcPos[0] - mX, mcPos[1] - mY)
                else:
                    selectRect = pygame.Rect(mcPos[0], mcPos[1], mcPos2[0] - mcPos[0], mcPos2[1] - mcPos[1])
                drawRectBorder(screen, selectRect)

        # Patterns menu
        if self._patternsMenu.enabled():
            self._patternsMenu.draw(screen)

        # Action bar
        self.drawActionBar()

        # Cursor logic
        if mY < self._actionBarY:
            if self._patternsMenu.hovered():
                pygame.mouse.set_visible(True)
            else:
                cursorSurface = self._inputModeMngr.cursorSurface()
                if cursorSurface and not self._pattern:
                    pygame.mouse.set_visible(False)
                    screen.blit(cursorSurface, (mX, mY))
        else:
            pygame.mouse.set_visible(True)

        # Update display
        pygame.display.update()

    def drawActionBar(self) -> None:
        bg = pygame.Rect(
            self._actionBarX, self._actionBarY, self._width, self._actionBarHeight
        )
        pygame.draw.rect(self._screen, Color.GREY_LIGHT, bg)
        pygame.draw.line(
            self._screen,
            Color.GREY,
            (self._actionBarX, self._actionBarY),
            (self._actionBarX + self._width, self._actionBarY),
        )

        for button in self._buttons:
            button.draw(self._screen)

        self._inputModeMngr.draw(self._screen)

        stats = [
            f"Alive: {self._cellsAlive}",
            f"Births: {self._cellsBirthed}",
            f"Deaths: {self._cellsDied}",
            f"Generation: {self._generation}",
        ]

        statIdx = 0
        statFont = SysFont('Sans', 15)
        for stat in stats:
            fontRect = statFont.get_rect(stat)
            statFont.render_to(self._screen, (5, (self._actionBarY + 5) + ((fontRect.height + 4) * statIdx)), stat)
            statIdx += 1

        statFont.render_to(self._screen, (125, self._actionBarY + 5), "FPS: {:.2f}".format(self._clock.get_fps()))
        statFont.render_to(self._screen, (125, self._actionBarY + 20), "Zoom: {:.2f}".format(self._zoom))
        statFont.render_to(self._screen, (125, self._actionBarY + 35), f"Cell width: {self._cellW}")
        statFont.render_to(self._screen, (125, self._actionBarY + 50), f"Cell height: {self._cellH}")

    def clear(self) -> None:
        startStopBtn = self._buttons[self._startStopBtnIdx]
        if startStopBtn.getId() == ButtonID.STOP:
            startStopBtn.toggle()
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

    def save(self) -> None:
        pass

    def start(self) -> None:
        self._stopped = False

    def stop(self) -> None:
        self._stopped = True

    def stopped(self) -> bool:
        return self._stopped

    def zoom(self, direction:int) -> None:
        if direction == ZoomDir.IN:
            self._cellW += 1
            self._cellH += 1
        elif direction == ZoomDir.OUT:
            # Decrease cell size
            if self._cellW > 1:
                self._cellW -= 1
            if self._cellH > 1:
                self._cellH -= 1
        else:
            return

        for i in range(self._cols * self._rows):
            x = i % self._rows
            y = int(i / self._rows)
            c = getCellAtPoint(x, y, self._cells, self._rows)
            c.setHeight(self._cellH)
            c.setWidth(self._cellW)