import glob
import pygame

from pygame.font import Font
from pygame.locals import KEYDOWN, MOUSEBUTTONUP, MOUSEBUTTONDOWN, K_g, K_ESCAPE
from gameoflife.colors import BLUE, BLACK, GREY, GREY_DARK1, GREY_DARK2, GREY_LIGHT1
from gameoflife.constvars import *
from gameoflife.config import Config
from gameoflife.grid import Grid
from gameoflife.button import RectButton, ButtonText
from gameoflife.cell import *
from gameoflife.pattern import Pattern, PatternMenu, PatternType


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
        self.height = self.cfg.get("screen.height")
        self.width = self.cfg.get("screen.width")
        self.screen = pygame.display.set_mode([self.width, self.height])
        self.cellHeight = self.cfg.get("cell.height", default=5)
        self.cellWidth = self.cfg.get("cell.width", default=5)
        self.actionBarHeight = 70
        self.actionBarX = 0
        self.actionBarY = self.height - self.actionBarHeight
        self.rows = int((self.height - self.actionBarHeight) / self.cellHeight)
        self.cols = int(self.width / self.cellWidth)
        self.clock = pygame.time.Clock()
        self.grid = Grid(self.cols, self.rows, self.cellWidth, self.cellHeight)
        self.cells = [[Cell(x, y, self.cellWidth, self.cellHeight, CellState.DEAD) for x in range(self.cols)] for y in range(self.rows)]
        self._clear = False
        self._next = False
        self._reset = False
        self._running = True
        self._stopped = True
        self.patternsMenu = PatternMenu(50, 50, maxHeight=400)
        self.patternsMenu.setFont(self.font)
        self.patterns = []
        self.patternSelected = None
        self.generation = 0
        self.cellsAlive = 0
        self.cellsBirthed = 0
        self.cellsDied = 0
        self.mouseButtonHeldDown = False

        # Zoom
        self.zoom = 1
        self.zoomMax = 10
        self.zoomMin = 1
        self.zoomStep = 0.10

        self.loadAllPatterns()
        self.initButtons()


    def initButtons(self) -> None:
        btnHeight = 30
        btnMargin = 15
        btnWidth = 100

        self.buttons = [
            #RectButton(ButtonText.RESET, btnWidth, btnHeight),
            RectButton(ButtonText.CLEAR, btnWidth, btnHeight),
            RectButton(ButtonText.START, btnWidth, btnHeight),
            RectButton(ButtonText.NEXT, btnWidth, btnHeight),
            RectButton(ButtonText.PATTERNS, btnWidth, btnHeight),
            RectButton(ButtonText.EXIT, btnWidth, btnHeight),
        ]

        btnCount = len(self.buttons)
        buttonsTotalWidth = (btnCount * (btnWidth + btnMargin)) - btnMargin
        remainingScreenSpace = self.width - buttonsTotalWidth
        buttonX = remainingScreenSpace / 2
        buttonY = (self.actionBarY) + ((self.actionBarHeight / 2) - btnHeight / 2)

        for button in self.buttons:
            button.setFont(self.font)
            button.setHoverBackgroundColor(GREY_DARK2)
            button.setX(buttonX)
            button.setY(buttonY)
            buttonX += btnWidth + btnMargin

    def loadPatterns(self, path:str, patternType:PatternType) -> Pattern:
        widestPattern = None
        for p in glob.glob(path):
            pattern = Pattern(path.split("/")[-1], p, patternType)
            if pattern.getRows():
                self.patterns.append(pattern)
                patternWidth = pattern.getWidth()
                if widestPattern is None or patternWidth > widestPattern.getWidth():
                    widestPattern = pattern
        return widestPattern

    def loadAllPatterns(self) -> None:
        patternDirTypes = {
            'oscillators': PatternType.Oscillator,
            'spaceships': PatternType.Spacehship,
            'flipflops': PatternType.FlipFlop,
            'methuselah': PatternType.Methuselah,
            'still-lifes': PatternType.StillLife
        }

        widestPattern = None
        for patternDir, patternType in patternDirTypes.items():
            pattern = self.loadPatterns(f"patterns/{patternDir}/*", patternType)
            if widestPattern is None or pattern.getWidth() > widestPattern.getWidth():
                widestPattern = pattern

        self.patternsMenu.setPatternRowWidth(widestPattern.getWidth())
        self.patternsMenu.setPatterns(self.patterns)

    def eventLoop(self) -> None:
        for event in pygame.event.get():
            #print(event)
            handlerResp = self.patternsMenu.eventHandler(event)
            if handlerResp:
                self.mouseButtonHeldDown = False
                if isinstance(handlerResp, Pattern):
                    self.patternSelected = handlerResp
                    self.patternSelected.setCellHeight(self.cellHeight)
                    self.patternSelected.setCellWidth(self.cellWidth)
                return
            if event.type == pygame.QUIT:
                self.quit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.patternSelected = None
                if event.key == K_g:
                    self.grid.toggle()
            elif (event.type == MOUSEBUTTONUP and event.dict.get('button') == MOUSEBUTTON_LCLICK) or (self.mouseButtonHeldDown):
                #print(event.dict)
                if event.type == MOUSEBUTTONUP and self.mouseButtonHeldDown:
                    print("mouseButtonHeldDown = False")
                    self.mouseButtonHeldDown = False
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
                        elif btnTxt == ButtonText.RESET:
                            self.reset()
                        elif btnTxt == ButtonText.EXIT:
                            self.quit()

                if mY < self.actionBarY:
                    cellX = int(mX / self.cellWidth)
                    cellY = int(mY / self.cellHeight)
                    try:
                        if self.patternSelected:
                            selectedCells = self.patternSelected.getCells()
                            for y in range(len(selectedCells)):
                                for x in range(len(selectedCells[y])):
                                    nextCellX = cellX + x
                                    nextCellY = cellY + y
                                    if nextCellX < self.cols and nextCellY < self.rows:
                                        self.cells[nextCellY][nextCellX].setState(selectedCells[y][x].getState())
                        else:
                            cell = self.cells[cellY][cellX]
                            cell.setState(CellState.ALIVE)
                    except Exception as e:
                        print(e)
            elif event.type == MOUSEBUTTONDOWN and event.dict.get('button') == MOUSEBUTTON_LCLICK:
                (mX, mY) = pygame.mouse.get_pos()
                if mY < self.actionBarY:
                    self.mouseButtonHeldDown = True
            elif event.type == MOUSEBUTTONUP:
                buttonCode = event.dict.get('button')
                if buttonCode == MOUSEBUTTON_SCROLL_DOWN and self.zoom >= self.zoomMin + self.zoomStep:
                    self.zoom -= self.zoomStep
                elif buttonCode == MOUSEBUTTON_SCROLL_UP and self.zoom < self.zoomMax - self.zoomStep:
                    self.zoom += self.zoomStep
    def loop(self) -> None:
        while self.running():
            self.eventLoop()
            self.update()
            self.draw()
            self.clock.tick(self.cfg.get("fps", default=5))
        pygame.quit()

    def update(self) -> None:
        if self.isReset():
            self.cells = [
                [Cell(x, y, self.cellWidth, self.cellHeight) for x in range(self.cols)]
                for y in range(self.rows)
            ]
        elif self.cleared():
            self.cells = [
                [
                    Cell(x, y, self.cellWidth, self.cellHeight, CellState.DEAD)
                    for x in range(self.cols)
                ]
                for y in range(self.rows)
            ]

        for button in self.buttons:
            button.update()

        self.patternsMenu.update()

        if not self.stopped() or self.next():
            self.generation += 1
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
            self.cellsAlive = 0
            self.cellsBirthed = 0
            self.cellsDied = 0
            for y in range(len(self.cells)):
                for x in range(len(self.cells[y])):
                    cell = self.cells[y][x]
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

            if allCellsDead:
                self.stop()

    def draw(self) -> None:
        self.screen.fill((255, 255, 255))

        for y in range(len(self.cells)):
            for x in range(len(self.cells[y])):
                cell = self.cells[y][x]
                cell.draw(self.screen)

        self.grid.draw(self.screen)
        self.drawActionBar()
        self.patternsMenu.draw(self.screen)

        if self.patternSelected and pygame.mouse.get_pos()[1] < self.actionBarY:
            patternSurf = self.patternSelected.getSurface()
            self.screen.blit(patternSurf, pygame.mouse.get_pos())

        pygame.display.update()

    def drawActionBar(self) -> None:
        x = self.actionBarX
        y = self.actionBarY
        bg = pygame.Rect(x, y, self.width, self.actionBarHeight)
        pygame.draw.rect(self.screen, GREY_LIGHT1, bg)
        pygame.draw.line(self.screen, GREY, (x, y), (x + self.width, y))

        for button in self.buttons:
            button.draw(self.screen)

        stats = [
            f"Alive: {self.cellsAlive}",
            f"Births: {self.cellsBirthed}",
            f"Deaths: {self.cellsDied}",
            f"Generation: {self.generation}"
        ]

        statIdx = 0
        statFont = pygame.font.Font(None, 11)
        for stat in stats:
            fontSize = statFont.size(stat)
            textImg = self.font.render(stat, True, BLACK)
            self.screen.blit(textImg, (10, (y + 5) + ((fontSize[1] * 2) * statIdx)))
            statIdx += 1

        zoomText = self.font.render("Zoom: {:.2f}".format(self.zoom), True, BLACK)
        self.screen.blit(zoomText, (self.width - 100, self.actionBarY + 5))

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

    def isReset(self) -> bool:
        val = self._reset
        self._reset = False
        return val

    def reset(self) -> None:
        self._reset = True

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