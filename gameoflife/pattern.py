import pygame

from gameoflife.button import CircleButton
from gameoflife.cell import Cell, CellState
from gameoflife.colors import (
    WHITE,
    BLACK,
    GREY_LIGHT1,
    GREY_LIGHT2,
    GREY,
    RED,
    RED_LIGHT1,
    GREY_DARK1,
)
from gameoflife.helpers import drawRectBorder
from pygame import Surface, draw, Rect, Color
from pygame.font import Font
from pygame.locals import MOUSEBUTTONUP
from typing import Union, List


class PatternType:
    StillLife: int = 1
    Oscillator: int = 2
    Spacehship: int = 3


class Pattern:
    def __init__(self, name: str, path: str, type: PatternType) -> None:
        self._rows: int = 0
        self._cols: int = 0
        self._name: str = name
        self._desc: str = ""  # TODO
        self._path: str = path
        self._type: PatternType = type
        self._cells: List[List] = []
        self._cellW = 10
        self._cellH = 10
        self._bgColor = GREY_LIGHT1
        self._load()

    def _load(self):
        try:
            with open(self._path) as file:
                data = json.load(file)
                seed = data.get("seed", [])

                self._rows = len(seed)
                y = 0
                longestRow = 0
                for line in seed:
                    if len(line) > longestRow:
                        longestRow = len(line)
                    row = []
                    x = 0
                    for char in line:
                        cellState = CellState.DEAD if char == "0" else CellState.ALIVE
                        c = Cell(x, y, self._cellW, self._cellH, cellState)
                        row.append(c)
                        x += 1
                    self._cells.append(row)
                    y += 1
                self._cols = longestRow
        except Exception as e:
            print(f'failed to load "{self._name}": {e}')

    def getCells(self) -> List[List]:
        return self._cells

    def getCols(self) -> int:
        return self._cols

    def getHeight(self) -> int:
        return self._cellH * len(self._cells)

    def getName(self) -> str:
        return self._name

    def getRows(self) -> int:
        return self.rows

    def getSurface(self) -> Surface:
        width = self._cols * self._cellW
        height = len(self._cells) * self._cellH
        surf = Surface((width, height)).convert_alpha()
        surf.fill(self._bgColor)
        for y in range(len(self._cells)):
            for x in range(len(self._cells[y])):
                cell = self._cells[y][x]
                cell.draw(surf)
        return surf

    def getWidth(self) -> int:
        return self._cellW * self._cols

    def setBgColor(self, color) -> None:
        self.bgColor = color
        for y in range(len(self.cells)):
            for x in range(len(self.cells[y])):
                cell = self.cells[y][x]
                cell.setStateColor(CellState.DEAD, color)

    def setCellHeight(self, height: int) -> None:
        self._cellH = height
        for y in range(len(self._cells)):
            for x in range(len(self._cells[y])):
                cell = self._cells[y][x]
                cell.setHeight(height)

    def setCellWidth(self, width: int) -> None:
        self._cellW = width
        for y in range(len(self._cells)):
            for x in range(len(self._cells[y])):
                cell = self._cells[y][x]


class PatternMenuRow:
    def __init__(
        self,
        x: int,
        y: int,
        w: int,
        pattern: Pattern,
        bgColor: Color,
        borderColor: Color,
    ) -> None:
        self.inactiveBgColor = bgColor
        self.bgColor = self.inactiveBgColor
        self.hoveredBgColor = GREY_LIGHT2
        self.pattern = pattern
        self.pattern.setBgColor(self.bgColor)
        self.padding = 5
        self.h = self.pattern.getHeight() + (self.padding * 2)
        self.x = x
        self.y = y
        self.w = w
        self.cursor = pygame.SYSTEM_CURSOR_ARROW

    def update(self) -> None:
        if self.hovered():
            self.bgColor = self.hoveredBgColor
            self.cursor = pygame.SYSTEM_CURSOR_HAND
            pygame.mouse.set_cursor(self.cursor)
        else:
            if self.cursor != pygame.SYSTEM_CURSOR_ARROW:
                self.cursor = pygame.SYSTEM_CURSOR_ARROW
                pygame.mouse.set_cursor(self.cursor)
            self.bgColor = self.inactiveBgColor
        self.pattern.setBgColor(self.bgColor)

    def draw(self, screen: Surface) -> None:
        surf = Surface((self.w, self.h))
        patternSurf = self.pattern.getSurface()
        patternHeight = self.pattern.getHeight()
        surf.fill(self.bgColor)
        surf.blit(patternSurf, (self.padding, self.padding))
        screen.blit(surf, (self.x, self.y))
        drawRectBorder(
            screen,
            self.x,
            self.y,
            self.w,
            self.h,
            GREY_DARK1,
        )

    def getHeight(self) -> int:
        return self.h

    def getPattern(self) -> Pattern:
        return self._pattern

    def setMenuHeight(self, height: int) -> None:
        self._menuH = height

    def setWidth(self, width: int) -> None:
        self._rect.width = width + (self._padding * 2)

    def hovered(self) -> bool:
        (mX, mY) = pygame.mouse.get_pos()
        if mY >= self._absY and mY <= self._absY + self._menuH:
            if (
                mX >= self._absX + self._rect.x
                and mX <= self._absX + self._rect.x + self._rect.width
            ) and (
                mY >= self._absY + self._rect.y - self._scrollY
                and mY <= self._absY + self._rect.y + self._rect.height - self._scrollY
            ):
                return True
        return False

    def clicked(self, event) -> bool:
        if event.type == MOUSEBUTTONUP and self.hovered():
            return True
        return False

    def eventHandler(self) -> Union[None, Pattern]:
        pass


# TODO
class PatternMenuScrollBar:
    def __init__(self) -> None:
        pass


class PatternMenu:
    def __init__(
        self, x: int, y: int, maxHeight: int = None, font: Font = None
    ) -> None:
        self._padding = 12
        self._maxHeight: Union[int, None] = maxHeight
        self._font = font
        self._bgColor = GREY_LIGHT1
        self._closeBtn = RectButton("X", Rect(x, y - 20, 20, 20), RED_LIGHT1)
        self._closeBtn.setFont(font)
        self._closeBtn.setHoverBackgroundColor(RED)
        self._enabled = False
        self.rows = []

        self.closeBtn.setHoverBackgroundColor(RED)

    def enable(self) -> None:
        self._enabled = True

    def enabled(self) -> bool:
        return self._enabled

    def disable(self) -> None:
        self._enabled = False

    def toggle(self) -> None:
        self._enabled = not self._enabled

    def setFont(self, font: Font) -> None:
        self._font = font
        self._closeBtn.setFont(font)

    def setMaxHeight(self, height: int) -> None:
        self._maxHeight = height
        if self._maxHeight > self._rect.height:
            self._rect.height = self._maxHeight

    def setPatterns(self, patterns: List[Pattern]) -> None:
        self.patterns = patterns
        self.rows.clear()
        yOffset = self.padding
        for pattern in patterns:
            pattern.setBgColor(self.bgColor)
            row = PatternMenuRow(
                self.x + self.padding,
                self.y + yOffset,
                self.w - (self.padding * 2),
                pattern,
                self.bgColor,
                BLACK,
            )
            self._rows.append(row)
            yOffset += row.getHeight() + self._padding

        innerHeight = yOffset - self._padding
        outerHeight = self.getHeight()

        self._rect.w = widest + (self._padding * 2)
        self._rect.h = outerHeight

        for row in self._rows:
            row.setWidth(widest)
            row.setMenuHeight(outerHeight)

        if self._scrollBarEnabled:
            self._rect.w += self._scrollBarWidth

        # self._closeBtn.setX(self._rect.x + self._rect.w - 15)

        self._rowsSurface = Surface((widest + (self._padding * 2), yOffset))
        self._rowsSurface.fill(self._bgColor)

        self._scrollBarHeight = (outerHeight / innerHeight) * outerHeight
        self._scrollBarRatio = innerHeight / outerHeight
        self._scrollBarRect = Rect(
            self._rect.x + (self._rect.w - self._scrollBarWidth),
            self._rect.y,
            self._scrollBarWidth,
            self._scrollBarHeight,
        )

    def getHeight(self) -> int:
        height = self.padding
        for row in self.rows:
            height += row.getHeight() + self.padding
        return height

    def update(self) -> None:
        if self._enabled:
            self.closeBtn.update()
            for row in self.rows:
                row.update()

    def eventHandler(self, event) -> bool:
        sbHalfHeight = self._scrollBarRect.height / 2
        menuHeight = self.getHeight()
        button = event.dict.get("button")
        (mX, mY) = pygame.mouse.get_pos()
        (x, y, w, h) = (self._rect.x, self._rect.y, self._rect.width, self._rect.height)
        if button == MOUSEBUTTON_LCLICK:
            # Close button
            if self._closeBtn.clicked(mX, mY):
                self.disable()
                return True
            # Scrollbar mouse event
            # If the mouse pos is in the scrollbar area
            elif (mX >= x + w - self._scrollBarRect.width) and (mX <= x + w):
                # If the mouse pos is somewhere in the middle with padding of 1/2 the scrollbars height on top / bottom.
                # Boundary check is needed to prevent the scrollbar from running past the top of the menu.
                if mY >= y + sbHalfHeight and mY <= y + (menuHeight - sbHalfHeight):
                    # Center the scrollbar to mouse y since we know there's more than half the scrollbars height worth of room above / below.
                    self._scrollBarRect.y = mY - self._scrollBarRect.height / 2
                # If there's not enough room, is the mouse y pos at the top?
                elif mY >= y and mY <= y + sbHalfHeight:
                    # Set the top of the scrollbar to the mouse y pos.
                    self._scrollBarRect.y = mY
                # If not the top then bottom?
                elif (mY >= y + menuHeight - sbHalfHeight) and mY <= y + menuHeight:
                    # set the bottom of the scrollbar to the mouse y pos
                    self._scrollBarRect.y = mY - self._scrollBarRect.height
                return True
            else:
                for row in self._rows:
                    if row.clicked(event):
                        return row.getPattern()
            if (mX >= x and mX <= x + w) and (mY >= y and mY <= y + h):
                return True
        # Scrollbar mouse scrolling
        elif button in [MOUSEBUTTON_SCROLL_UP, MOUSEBUTTON_SCROLL_DOWN]:
            scrollStep = 5
            if button == MOUSEBUTTON_SCROLL_DOWN:
                scrollBarBottom = self._scrollBarRect.y + self._scrollBarRect.h
                menuBottom = y + menuHeight
                if scrollBarBottom <= menuBottom - scrollStep:
                    self._scrollBarRect.y += scrollStep
                    for row in self._rows:
                        row._scrollY += scrollStep * self._scrollBarRatio
                elif scrollBarBottom < menuBottom:
                    rem = menuBottom - scrollBarBottom
                    if rem < scrollStep:
                        self._scrollBarRect.y = menuBottom - self._scrollBarRect.height
            elif button == MOUSEBUTTON_SCROLL_UP:
                if self._scrollBarRect.y >= y + scrollStep:
                    self._scrollBarRect.y -= scrollStep
                    for row in self._rows:
                        row._scrollY -= scrollStep * self._scrollBarRatio
                elif self._scrollBarRect.y > y:
                    self._scrollBarRect.y = y
            return True
        return False

    def draw(self, screen: Surface) -> None:
        if self._enabled:
            height = self.getHeight()
            rect = Rect(self.x, self.y, self.w, height)
            yOffset = self.padding

            draw.rect(screen, self.bgColor, rect)
            drawRectBorder(screen, self.x, self.y, self.w, height)

        rowsSurfaceArea = Rect(
            0,
            (self._scrollBarRect.y - self._rect.y) * self._scrollBarRatio,
            self._rowsSurface.get_size()[0],
            self.getHeight(),
        )

        self.closeBtn.draw(screen)
