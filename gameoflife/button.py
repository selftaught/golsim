import math
import pygame

from pygame import Surface, draw
from pygame.event import Event
from pygame.font import Font
from pygame.freetype import SysFont
from pygame.locals import MOUSEBUTTONDOWN
from pygame.rect import Rect
from typing import Union, Tuple

from gameoflife.color import Color
from gameoflife.draw import drawRectBorder
from gameoflife.mouse import MOUSEBUTTON_LCLICK
from gameoflife.tooltip import Tooltip



class ButtonID:
    CLEAR = "Clear"
    EXIT = "Exit"
    NEXT = "Next"
    RESET = "Reset"
    START = "Start"
    STOP = "Stop"
    PATTERNS = "Patterns"
    DRAW = "Draw"
    PAN = "Pan"
    SELECT = "Select"
    ZOOM_IN = "Zoom In"
    ZOOM_OUT = "Zoom Out"


class BaseButton:
    def __init__(
        self,
        id: str,
        x: int,
        y: int,
        event: Event,
        bgColor: pygame.Color = Color.GREY,
        border: bool = True,
        borderColor: pygame.Color = Color.BLACK,
        tooltip: bool = False,
    ) -> None:
        self._id = id
        self._x = x
        self._y = y
        self._currBgColor = bgColor
        self._bgColor = bgColor
        self._event = event
        self._hoverBgColor = bgColor
        self._hoverTextColor = None
        self._border = border
        self._borderColor = Color.BLACK
        self._cursor = pygame.SYSTEM_CURSOR_ARROW
        self._font = SysFont('Sans', 12)
        self._tooltip = None

        if tooltip:
            self._tooltip = Tooltip(self._id, self._font, (self._x, self._y), Color.GREY)

    def getBackgroundColor(self) -> Color:
        return self._bgColor

    def getBorderColor(self) -> Color:
        return self._borderColor

    def getEvent(self) -> Event:
        return self._event

    def getHoverBackgroundColor(self) -> Color:
        return self._hoverBgColor

    def getX(self) -> int:
        return self._x

    def getY(self) -> int:
        return self._y

    def getId(self) -> str:
        return self._id

    def setX(self, x: int) -> None:
        self._x = x

    def setY(self, y: int) -> None:
        self._y = y

    def setFont(self, font: Font) -> None:
        self._font = font
        if self._tooltip:
            self._tooltip.setFont(font)

    def setBackgroundColor(self, bgColor: Color) -> None:
        self._bgColor = bgColor

    def setHoverBackgroundColor(self, bgColor: Color) -> None:
        self._hoverBgColor = bgColor

    def setBorder(self, border: bool) -> None:
        self._border = border

    def setBorderColor(self, color: Color):
        self._borderColor = color

    def setId(self, id: str) -> None:
        self._id = id

    def clicked(self, mouseX: int, mouseY: int) -> bool:
        raise NotImplementedError("button clicked() not implemented!")

    def draw(self, screen: Surface) -> None:
        raise NotImplementedError("button draw() not implemented!")

    def eventHandler(self, event:Event):
        raise NotImplementedError("button eventHandler() not implemented!")

    def hovered(self) -> None:
        raise NotImplementedError("button eventHandler() not implemented!")

    def update(self) -> None:
        raise NotImplementedError("button update() not implemented!")


class CircleButton(BaseButton):
    def __init__(
        self,
        id: str,
        x: int,
        y: int,
        event: Event,
        radius: float,
        bgColor: pygame.Color = Color.GREY,
        border: bool = True,
        borderColor: pygame.Color = Color.BLACK,
        tooltip: bool = False
    ) -> None:
        super().__init__(id, x, y, event, bgColor, border, borderColor, tooltip)
        self._radius: float = radius

    def getRadius(self) -> float:
        return self._radius

    def setRadius(self, radius: float) -> None:
        self._radius = radius

    def clicked(self, mouseX: int, mouseY: int) -> bool:
        sqMouseX = (mouseX - self._x) ** 2
        sqMouseY = (mouseY - self._y) ** 2
        if math.sqrt(sqMouseX + sqMouseY) < self._radius:
            return True
        return False

    def draw(self, surface:Surface) -> None:
        ftFont = SysFont('sans', 24)
        draw.circle(surface, self._currBgColor, (self._x, self._y), self._radius, 0)
        if self._border:
            draw.circle(surface, self._borderColor, (self._x, self._y), self._radius, 1)
        fontRect = ftFont.get_rect(self._id)
        textX = self._x - int(fontRect.width / 2)
        textY = self._y - int(fontRect.height / 2) + 1
        ftFont.render_to(surface, (textX, textY), self._id)

    def update(self) -> None:
        (mX, mY) = pygame.mouse.get_pos()
        sqMouseX = (mX - self._x) ** 2
        sqMouseY = (mY - self._y) ** 2
        if math.sqrt(sqMouseX + sqMouseY) < self._radius:
            self._cursor = pygame.SYSTEM_CURSOR_HAND
            pygame.mouse.set_cursor(self._cursor)
            self._currBgColor = self._hoverBgColor
        else:
            if self._cursor != pygame.SYSTEM_CURSOR_ARROW:
                self._cursor = pygame.SYSTEM_CURSOR_ARROW
                pygame.mouse.set_cursor(self._cursor)
            if self._currBgColor != self._bgColor:
                self._currBgColor = self._bgColor


class RectButton(BaseButton):
    def __init__(
        self,
        id: str,
        event:Event,
        rect:Rect = Rect(0, 0, 0, 0),
        bgColor: pygame.Color = Color.GREY,
        border: bool = True,
        borderColor: pygame.Color = Color.BLACK,
        imagePath: str = None,
        tooltip: bool = False,
    ) -> None:
        super().__init__(id, rect.x, rect.y, event, bgColor, border, borderColor, tooltip)
        self._rect = rect
        self._currBgColor = bgColor
        self._surface = None
        if imagePath:
            image = pygame.image.load(imagePath)
            self._surface = image
            #self._surface = pygame.transform.scale(image, (rect.width, rect.height))

    def getRect(self) -> Rect:
        return self._rect

    def getH(self) -> int:
        return self._rect.height

    def getW(self) -> int:
        return self._rect.width

    def getX(self) -> int:
        return self._rect.x

    def getY(self) -> int:
        return self._rect.y

    def setRect(self, rect: Rect):
        self._rect = rect

    def setW(self, width:int) -> None:
        self._rect.width = width

    def setH(self, height:int) -> None:
        self._rect.height = height

    def clicked(self, mouseX:Union[None, int]=None, mouseY:Union[None, int]=None) -> bool:
        if not mouseX or not mouseY:
            (mouseX, mouseY) = pygame.mouse.get_pos()
        if self._rect.collidepoint((mouseX, mouseY)):
            return True
        return False

    def draw(self, surface:Surface) -> None:
        if self._currBgColor:
            draw.rect(surface, self._currBgColor, self._rect)

        if self._surface:
            surface.blit(self._surface, (self._x, self._y))
        else:
            fontRect = self._font.get_rect(self._id)
            textX = self._rect.x + ((self._rect.width / 2) - (fontRect.width / 2))
            textY = self._rect.y + ((self._rect.height / 2) - (fontRect.height / 2))
            self._font.render_to(surface, (textX, textY), self._id)

        if self._border:
            drawRectBorder(surface, self._rect, self._borderColor)

        if self._tooltip:
            self._tooltip.draw(surface)

    def eventHandler(self, event:Event):
        buttonCode = event.dict.get("button")
        if event.type == MOUSEBUTTONDOWN and buttonCode == MOUSEBUTTON_LCLICK:
            if self.clicked():
                pygame.event.post(self._event)

    def hovered(self) -> bool:
        (mX, mY) = pygame.mouse.get_pos()
        if self._rect.collidepoint(mX, mY):
            return True

    def update(self) -> None:
        if self._tooltip:
            if self.hovered():
                self._tooltip.enable()
            else:
                self._tooltip.disable()

        if self._rect.collidepoint(pygame.mouse.get_pos()):
            self._cursor = pygame.SYSTEM_CURSOR_HAND
            self._currBgColor = self._hoverBgColor
            pygame.mouse.set_cursor(self._cursor)
        else:
            if self._cursor != pygame.SYSTEM_CURSOR_ARROW:
                self._cursor = pygame.SYSTEM_CURSOR_ARROW
                pygame.mouse.set_cursor(self._cursor)
            if self._currBgColor != self._bgColor:
                self._currBgColor = self._bgColor


class ToggleRectButton(RectButton):
    def __init__(
        self,
        id: str,
        onDisable:Tuple[str, Event],
        onEnable:Tuple[str, Event],
        rect:Rect = Rect(0, 0, 0, 0),
        bgColor: pygame.Color = Color.GREY,
        border: bool = True,
        borderColor: pygame.Color = Color.BLACK,
    ) -> None:
        super().__init__(id, None, rect, bgColor, border, borderColor)
        self._rect = rect
        self._currBgColor = bgColor
        self._surface = None
        self._onDisable = onDisable
        self._onEnable = onEnable
        self._enabled = False

    def eventHandler(self, event:Event):
        buttonCode = event.dict.get("button")
        if event.type == MOUSEBUTTONDOWN and buttonCode == MOUSEBUTTON_LCLICK:
            if self.clicked():
                self.toggle()

    def toggle(self):
        self._enabled = not self._enabled
        if self._enabled:
            pygame.event.post(self._onEnable[1])
            self._id = self._onEnable[0]
        else:
            pygame.event.post(self._onDisable[1])
            self._id = self._onDisable[0]
