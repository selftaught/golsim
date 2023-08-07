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
        self.rows: list = 0
        self.cols: list = 0
        self.name: str = name
        self.desc: str = ""  # TODO
        self.path: str = path
        self.type: PatternType = type
        self.cells: List[List] = []
        self.cellWidth = 10
        self.cellHeight = 10
        self.rowMaxLen = 0
        self.bgColor = GREY_LIGHT1
        self._load()

    def _load(self):
        with open(self.path) as file:
            lines = [line.rstrip() for line in file]
            self.rows = len(lines)
            y = 0
            for line in lines:
                if len(line) > self.rowMaxLen:
                    self.rowMaxLen = len(line)
                row = []
                x = 0
                for char in line:
                    cellState = CellState.DEAD if char == "0" else CellState.ALIVE
                    c = Cell(x, y, self.cellWidth, self.cellHeight, cellState)
                    row.append(c)
                    x += 1
                self.cells.append(row)
                y += 1
            self.cols = self.rowMaxLen

    def getCells(self) -> List[List]:
        return self.cells

    def getCols(self) -> int:
        return self.cols

    def getHeight(self) -> int:
        return self.cellHeight * len(self.cells)

    def getName(self) -> str:
        return self.name

    def getRows(self) -> int:
        return self.rows

    def getSurface(self) -> Surface:
        width = self.rowMaxLen * self.cellWidth
        height = len(self.cells) * self.cellHeight
        surf = Surface((width, height)).convert_alpha()
        surf.fill(self.bgColor)
        for y in range(len(self.cells)):
            for x in range(len(self.cells[y])):
                cell = self.cells[y][x]
                cell.draw(surf)
        return surf

    def getWidth(self) -> int:
        return self.cellWidth * self.cols

    def setBgColor(self, color) -> None:
        self.bgColor = color
        for y in range(len(self.cells)):
            for x in range(len(self.cells[y])):
                cell = self.cells[y][x]
                cell.setStateColor(CellState.DEAD, color)

    def setCellHeight(self, height: int) -> None:
        self.cellHeight = height
        for y in range(len(self.cells)):
            for x in range(len(self.cells[y])):
                cell = self.cells[y][x]
                cell.setHeight(height)

    def setCellWidth(self, width: int) -> None:
        self.cellWidth = width
        for y in range(len(self.cells)):
            for x in range(len(self.cells[y])):
                cell = self.cells[y][x]
                cell.setHeight(width)


class PatternMenuRow:
    def __init__(
        self,
        x: int,
        y: int,
        w: int,
        menuX: int,
        menuY: int,
        pattern: Pattern,
        bgColor: Color,
        borderColor: Color,
    ) -> None:
        self.inactiveBgColor = bgColor
        self.bgColor = self.inactiveBgColor
        self.hoveredBgColor = GREY_LIGHT2
        self.menuX: int = menuX
        self.menuY: int = menuY
        self.scrollY: int = 0
        self.pattern = pattern
        self.pattern.setBgColor(self.bgColor)
        self.padding = 0
        self.h = self.pattern.getHeight() + (self.padding * 2)
        self.x = x
        self.y = y
        self.w = w + (self.padding * 2)
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
        surf.fill(self.bgColor)
        surf.blit(self.pattern.getSurface(), (self.padding, self.padding))
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
        return self.pattern

    def hovered(self) -> bool:
        (mX, mY) = pygame.mouse.get_pos()
        if (mX >= self.menuX + self.x and mX <= self.menuX + self.x + self.w) and (
            mY >= self.menuY + self.y - self.scrollY and mY <= self.menuY + self.y + self.h - self.scrollY
        ):
            return True
        return False

    def clicked(self, event) -> bool:
        if event.type == MOUSEBUTTONUP and self.hovered():
            return True
        return False


class PatternMenu:
    def __init__(self, x: int, y: int, maxHeight:int=None) -> None:
        self.padding = 12
        self.x: int = x
        self.y: int = y
        self.w: int = 0
        self.rowWidth: int = 0
        self.maxHeight: Union[int, None] = maxHeight
        self.font = None
        self.bgColor = GREY_LIGHT1
        self.closeBtn = CircleButton("X", self.x + self.w, self.y, 10, RED_LIGHT1)
        self.closeBtn.setHoverBackgroundColor(RED)
        self._enabled = False
        self.rows = []

        self.innerSurface = None # Initialized after patterns are set. We don't know the height until then

        # Scroll bar
        self.scrollBarEnabled = True
        self.scrollBarWidth = 15
        self.scrollBarHeight = 30 # TBD.. depends on the inner scrollable content height
        self.scrollBarColor = GREY_DARK1
        self.scrollBarRect = None
        self.scrollBarRatio = 1

    def enable(self) -> None:
        self._enabled = True

    def enabled(self) -> bool:
        return self._enabled

    def disable(self) -> None:
        self._enabled = False

    def toggle(self) -> None:
        self._enabled = not self._enabled

    def setFont(self, font: Font) -> None:
        self.font = font
        self.closeBtn.setFont(font)

    def setMaxHeight(self, height:int) -> None:
        self.maxHeight = height

    def setPatterns(self, patterns: List[Pattern]) -> None:
        self.patterns = patterns
        self.rows.clear()
        yOffset = self.padding
        widest = None
        for pattern in patterns:
            patternWidth = pattern.getWidth()
            if widest is None or patternWidth > widest:
                widest = patternWidth
            pattern.setBgColor(self.bgColor)
            row = PatternMenuRow(
                self.padding,
                yOffset,
                self.rowWidth,
                self.x,
                self.y,
                pattern,
                self.bgColor,
                BLACK,
            )
            self.rows.append(row)
            yOffset += row.getHeight() + self.padding

        outerHeight = self.getHeight()
        innerHeight = yOffset - self.padding

        self.innerSurface = Surface((widest + (self.padding * 2), yOffset))
        self.innerSurface.fill(self.bgColor)

        self.scrollBarHeight = (outerHeight / innerHeight) * outerHeight
        self.scrollBarRatio = innerHeight / outerHeight
        self.scrollBarRect = Rect(self.x + (self.w - self.scrollBarWidth), self.y, self.scrollBarWidth, self.scrollBarHeight)

        print(f'scrollBarHeight: {self.scrollBarHeight}')
        print(f'scrollBarRatio: {self.scrollBarRatio}')
        print(f'innerHeight: {innerHeight}, outerHeight: {outerHeight}')

    def setPatternRowWidth(self, patternRowWidth:int) -> None:
        self.w = patternRowWidth + (self.padding * 2)
        if self.scrollBarEnabled:
            self.w += self.scrollBarWidth
        self.rowWidth = patternRowWidth
        self.closeBtn.setX(self.x + self.w)

    def getHeight(self) -> int:
        height = self.padding
        for row in self.rows:
            height += row.getHeight() + self.padding
        if self.maxHeight and height > self.maxHeight:
            return self.maxHeight
        return height

    def update(self) -> None:
        if self.enabled():
            self.closeBtn.update()
            for row in self.rows:
                row.update()

    def eventHandler(self, event) -> bool:
        if self.enabled():
            sbHalfHeight = self.scrollBarRect.height / 2
            menuHeight = self.getHeight()
            buttonCode = event.dict.get('button')
            (mX, mY) = pygame.mouse.get_pos()
            if buttonCode == MOUSEBUTTON_LCLICK:
                if self.closeBtn.clicked(mX, mY):
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                    self._enabled = False
                    return True
                # Scrollbar mouse event
                # If the mouse pos is in the scrollbar area
                elif (mX >= self.x + self.w - self.scrollBarRect.width) and (mX <= self.x + self.w):
                    # If the mouse pos is somewhere in the middle with padding of 1/2 the scrollbars height on top / bottom.
                    # Boundary check is needed to prevent the scrollbar from running past the top of the menu.
                    if (mY >= self.y + sbHalfHeight and mY <= self.y + (menuHeight - sbHalfHeight)):
                        # Center the scrollbar to mouse y since we know there's more than half the scrollbars height worth of room above / below.
                        self.scrollBarRect.y = mY - self.scrollBarRect.height / 2
                    # If there's not enough room, is the mouse y pos at the top?
                    elif mY >= self.y and mY <= self.y + sbHalfHeight:
                        # Don't center the scrollbar this time. It will overflow if centered. Set the top of the
                        # scrollbar to the mouse y pos.
                        self.scrollBarRect.y = mY
                    # If not the top then must be the bottom
                    elif (mY >= self.y + menuHeight - sbHalfHeight) and mY <= self.y + menuHeight:
                        # set the bottom of the scrollbar to the mouse y pos
                        self.scrollBarRect.y = mY - self.scrollBarRect.height
                    return True
                else:
                    for row in self.rows:
                        if row.clicked(event):
                            return row.getPattern()
                if (mX >= self.x and mX <= self.x + self.w) and (
                    mY >= self.y and mY <= self.y + self.getHeight()
                ):
                    return True
            # Scrollbar mouse wheel event
            elif buttonCode in [MOUSEBUTTON_SCROLL_UP, MOUSEBUTTON_SCROLL_DOWN]:
                scrollStep = 5
                if buttonCode == MOUSEBUTTON_SCROLL_DOWN:
                    scrollBarBottom = self.scrollBarRect.y + self.scrollBarRect.h
                    menuBottom = self.y + menuHeight
                    if scrollBarBottom <= menuBottom - scrollStep:
                        self.scrollBarRect.y += scrollStep
                        for row in self.rows:
                            row.scrollY += scrollStep * self.scrollBarRatio # TODO: create getting and setter member function in patternmenurow to update scrollx instead of directly.
                            print(row.scrollY)
                    elif scrollBarBottom < menuBottom:
                        rem = menuBottom - scrollBarBottom
                        if rem < scrollStep:
                            self.scrollBarRect.y = menuBottom - self.scrollBarRect.height
                elif buttonCode == MOUSEBUTTON_SCROLL_UP:
                    scrollBarTop = self.scrollBarRect.y
                    if self.scrollBarRect.y >= self.y + scrollStep:
                        self.scrollBarRect.y -= scrollStep
                        for row in self.rows:
                            row.scrollY -= scrollStep * self.scrollBarRatio # TODO: create getting and setter member function in patternmenurow to update scrollx instead of directly.
                            print(row.scrollY)
                    elif self.scrollBarRect.y > self.y:
                        self.scrollBarRect.y = self.y
                return True
        return False

    def draw(self, screen: Surface) -> None:
        if self.enabled():
            height = self.getHeight()
            rect = Rect(self.x, self.y, self.w, height)
            draw.rect(screen, self.bgColor, rect)

            for row in self.rows:
                row.draw(self.innerSurface)

            innerBlitY = (self.scrollBarRect.y - self.y) * self.scrollBarRatio

            if self.scrollBarRect.y + self.scrollBarRect.height == self.y + self.getHeight():
                innerBlitY += self.padding

            screen.blit(self.innerSurface, (self.x, self.y), Rect(0, innerBlitY, self.innerSurface.get_size()[0], self.getHeight()))

            drawRectBorder(screen, self.x, self.y, self.w, height)

            if self.scrollBarEnabled:
                lineStartPos = (self.scrollBarRect.x, self.y)
                lineEndPos = (self.scrollBarRect.x, self.y + height)
                draw.rect(screen, self.scrollBarColor, self.scrollBarRect)
                draw.line(screen, BLACK, lineStartPos, lineEndPos)

            self.closeBtn.draw(screen)
