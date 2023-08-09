import pygame

from gameoflife.button import CircleButton
from gameoflife.cell import Cell, CellState
from gameoflife.colors import (
    BLACK,
    GREY,
    GREY_DARK1,
    GREY_LIGHT1,
    GREY_LIGHT2,
    RED,
    RED_LIGHT1,
    WHITE,
)
from gameoflife.constvars import *
from gameoflife.helpers import drawRectBorder
from pygame import Surface, draw, Rect, Color
from pygame.font import Font
from pygame.locals import MOUSEBUTTONUP
from typing import Union, List


class PatternType:
    StillLife: int = 1
    Oscillator: int = 2
    Spacehship: int = 3
    FlipFlop: int = 4
    Methuselah: int = 5


class Pattern:
    def __init__(self, name: str, path: str, type: PatternType) -> None:
        self._rows: int = 0
        self._cols: int = 0
        self._name: str = name
        self._desc: str = ""  # TODO
        self._path: str = path
        self._type: PatternType = type
        self._cells: List[List] = []
        self._cellWidth = 10
        self._cellHeight = 10
        self._bgColor = GREY_LIGHT1
        self._load()

    def _load(self):
        with open(self._path) as file:
            lines = [line.rstrip() for line in file]
            self._rows = len(lines)
            y = 0
            longestRow = 0
            for line in lines:
                if len(line) > longestRow:
                    longestRow = len(line)
                row = []
                x = 0
                for char in line:
                    cellState = CellState.DEAD if char == "0" else CellState.ALIVE
                    c = Cell(x, y, self._cellWidth, self._cellHeight, cellState)
                    row.append(c)
                    x += 1
                self._cells.append(row)
                y += 1
            self._cols = longestRow

    def getCells(self) -> List[List]:
        return self._cells

    def getCols(self) -> int:
        return self._cols

    def getHeight(self) -> int:
        return self._cellHeight * len(self._cells)

    def getName(self) -> str:
        return self._name

    def getRows(self) -> int:
        return self._rows

    def getSurface(self) -> Surface:
        width = self._cols * self._cellWidth
        height = len(self._cells) * self._cellHeight
        surf = Surface((width, height)).convert_alpha()
        surf.fill(self._bgColor)
        for y in range(len(self._cells)):
            for x in range(len(self._cells[y])):
                cell = self._cells[y][x]
                cell.draw(surf)
        return surf

    def getWidth(self) -> int:
        return self._cellWidth * self._cols

    def setBgColor(self, color) -> None:
        self._bgColor = color
        for y in range(len(self._cells)):
            for x in range(len(self._cells[y])):
                cell = self._cells[y][x]
                cell.setStateColor(CellState.DEAD, color)

    def setCellHeight(self, height: int) -> None:
        self._cellHeight = height
        for y in range(len(self._cells)):
            for x in range(len(self._cells[y])):
                cell = self._cells[y][x]
                cell.setHeight(height)

    def setCellWidth(self, width: int) -> None:
        self._cellWidth = width
        for y in range(len(self._cells)):
            for x in range(len(self._cells[y])):
                cell = self._cells[y][x]
                cell.setHeight(width)


class PatternMenuRow:
    def __init__(
        self,
        x: int,
        y: int,
        absX: int,
        absY: int,
        pattern: Pattern,
        bgColor: Color,
        borderColor: Color,
    ) -> None:
        self._absX: int = absX
        self._absY: int = absY
        self._bgColor = bgColor
        self._cursor = pygame.SYSTEM_CURSOR_ARROW
        self._hoveredBgColor = GREY_LIGHT2
        self._inactiveBgColor = bgColor
        self._menuH: int = 0
        self._padding = 0
        self._pattern = pattern
        self._pattern.setBgColor(self._bgColor)
        self._rect = Rect(x, y, 0, self._pattern.getHeight() + (self._padding * 2))
        self._scrollY: int = 0

    def update(self) -> None:
        if self.hovered():
            self._bgColor = self._hoveredBgColor
            self._cursor = pygame.SYSTEM_CURSOR_HAND
            pygame.mouse.set_cursor(self._cursor)
        else:
            if self._cursor != pygame.SYSTEM_CURSOR_ARROW:
                self._cursor = pygame.SYSTEM_CURSOR_ARROW
                pygame.mouse.set_cursor(self._cursor)
            self._bgColor = self._inactiveBgColor
        self._pattern.setBgColor(self._bgColor)

    def draw(self, screen: Surface) -> None:
        surf = Surface((self._rect.w, self._rect.h))
        surf.fill(self._bgColor)
        surf.blit(self._pattern.getSurface(), (self._padding, self._padding))
        screen.blit(surf, (self._rect.x, self._rect.y))
        drawRectBorder(screen, self._rect, GREY_DARK1)

    def getHeight(self) -> int:
        return self._rect.height

    def getPattern(self) -> Pattern:
        return self._pattern

    def setMenuHeight(self, height:int) -> None:
        self._menuH = height

    def setWidth(self, width:int) -> None:
        self._rect.width = width + (self._padding * 2)

    def hovered(self) -> bool:
        (mX, mY) = pygame.mouse.get_pos()
        if mY >= self._absY and mY <= self._absY + self._menuH:
            if (mX >= self._absX + self._rect.x and mX <= self._absX + self._rect.x + self._rect.width) and (
                mY >= self._absY + self._rect.y - self._scrollY and mY <= self._absY + self._rect.y + self._rect.height - self._scrollY
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
    def __init__(self, x: int, y: int, maxHeight:int=None) -> None:
        self._padding = 12
        self._maxHeight: Union[int, None] = maxHeight
        self._font = None
        self._bgColor = GREY_LIGHT1
        self._closeBtn = CircleButton("X", x, y, 10, RED_LIGHT1)
        self._closeBtn.setHoverBackgroundColor(RED)
        self._enabled = False
        self._rect = Rect(x, y, 0, 0)
        self._rows = []
        self._rowsSurface = None
        self._scrollBarEnabled = True
        self._scrollBarWidth = 15
        self._scrollBarHeight = None
        self._scrollBarColor = GREY_DARK1
        self._scrollBarRect = None
        self._scrollBarRatio = 1

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

    def setMaxHeight(self, height:int) -> None:
        self._maxHeight = height
        if self._maxHeight > self._rect.height:
            self._rect.height = self._maxHeight

    def setPatterns(self, patterns: List[Pattern]) -> None:
        self._patterns = patterns
        self._rows.clear()

        yOffset = self._padding
        widest = None
        for pattern in patterns:
            patternWidth = pattern.getWidth()
            if widest is None or patternWidth > widest:
                widest = patternWidth
            pattern.setBgColor(self._bgColor)
            row = PatternMenuRow(
                self._padding,
                yOffset,
                self._rect.x,
                self._rect.y,
                pattern,
                self._bgColor,
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

        self._closeBtn.setX(self._rect.x + self._rect.w)

        self._rowsSurface = Surface((widest + (self._padding * 2), yOffset))
        self._rowsSurface.fill(self._bgColor)

        self._scrollBarHeight = (outerHeight / innerHeight) * outerHeight
        self._scrollBarRatio = innerHeight / outerHeight
        self._scrollBarRect = Rect(self._rect.x + (self._rect.w - self._scrollBarWidth), self._rect.y, self._scrollBarWidth, self._scrollBarHeight)

    def getHeight(self) -> int:
        height = self._padding
        for row in self._rows:
            height += row.getHeight() + self._padding
        if self._maxHeight and height > self._maxHeight:
            return self._maxHeight
        return height

    def update(self) -> None:
        self._closeBtn.update()
        for row in self._rows:
            row.update()

    def eventHandler(self, event) -> bool:
        sbHalfHeight = self._scrollBarRect.height / 2
        menuHeight = self.getHeight()
        buttonCode = event.dict.get('button')
        (mX, mY) = pygame.mouse.get_pos()
        (x, y, w, h) = (self._rect.x, self._rect.y, self._rect.width, self._rect.height)
        if buttonCode == MOUSEBUTTON_LCLICK:
            if self._closeBtn.clicked(mX, mY):
                self.disable()
                return True
            # Scrollbar mouse event
            # If the mouse pos is in the scrollbar area
            elif (mX >= x + w - self._scrollBarRect.width) and (mX <= x + w):
                # If the mouse pos is somewhere in the middle with padding of 1/2 the scrollbars height on top / bottom.
                # Boundary check is needed to prevent the scrollbar from running past the top of the menu.
                if (mY >= y + sbHalfHeight and mY <= y + (menuHeight - sbHalfHeight)):
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
            if (mX >= x and mX <= x + w) and (
                mY >= y and mY <= y + h
            ):
                return True
        # Scrollbar mouse scrolling
        elif buttonCode in [MOUSEBUTTON_SCROLL_UP, MOUSEBUTTON_SCROLL_DOWN]:
            scrollStep = 5
            if buttonCode == MOUSEBUTTON_SCROLL_DOWN:
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
            elif buttonCode == MOUSEBUTTON_SCROLL_UP:
                scrollBarTop = self._scrollBarRect.y
                if self._scrollBarRect.y >= y + scrollStep:
                    self._scrollBarRect.y -= scrollStep
                    for row in self._rows:
                        row._scrollY -= scrollStep * self._scrollBarRatio
                elif self._scrollBarRect.y > y:
                    self._scrollBarRect.y = y
            return True
        return False

    def draw(self, screen: Surface) -> None:
        draw.rect(screen, self._bgColor, self._rect)

        for row in self._rows:
            row.draw(self._rowsSurface)

        rowsSurfaceArea = Rect(0, (self._scrollBarRect.y - self._rect.y) * self._scrollBarRatio, self._rowsSurface.get_size()[0], self.getHeight())

        screen.blit(self._rowsSurface, (self._rect.x, self._rect.y), rowsSurfaceArea)

        drawRectBorder(screen, self._rect)

        if self._scrollBarEnabled:
            lineStartPos = (self._scrollBarRect.x, self._rect.y)
            lineEndPos = (self._scrollBarRect.x, self._rect.y + self._rect.height)
            draw.rect(screen, self._scrollBarColor, self._scrollBarRect)
            draw.line(screen, BLACK, lineStartPos, lineEndPos)

        self._closeBtn.draw(screen)
