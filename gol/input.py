from pygame.cursors import Cursor
from pygame.event import Event
from pygame.font import Font
from pygame.rect import Rect
from pygame.surface import Surface
from typing import Dict, List, Tuple, Union
import pygame

from gol.button import BaseButton, ButtonID, RectButton
from gol.color import Color
from gol.draw import drawRectBorder
from gol.mouse import MB_LCLICK, MB_DOWN


class InputMode:
    DRAW = ButtonID.DRAW
    PAN = ButtonID.PAN
    SELECT = ButtonID.SELECT
    ZOOM_IN = ButtonID.ZOOM_IN
    ZOOM_OUT = ButtonID.ZOOM_OUT


class InputModeManager:
    def __init__(self, btnWidth:int=30, btnHeight:int=30, btnMargin:int=10, btnStartX:int=0, btnStartY:int=0, font:Font=None) -> None:
        self._btnMargin = btnMargin
        self._btnHeight = btnHeight
        self._btnWidth = btnWidth
        self._btnStartX = btnStartX
        self._btnStartY = btnStartY
        self._buttons:List[BaseButton] = []
        self._mode:Union[str, None] = None
        self._cursors:Dict = {}
        self._font:Font = font


    def addMode(self, mode:str, event:Event, imagePath:str=None, active:bool=False) -> None:
        btnX = (len(self._buttons) * self._btnWidth + self._btnMargin) + self._btnStartX
        rect = Rect(btnX, self._btnStartY, self._btnWidth, self._btnHeight)
        button = RectButton(mode, event, rect, imagePath=imagePath, border=False, bgColor=None, tooltip=True)
        button.setFont(self._font)
        image = pygame.image.load(imagePath)
        self._buttons.append(button)
        self._cursors[mode] = Cursor((15, 5), image)
        if active:
            self._mode = mode
            pygame.mouse.set_visible(False)


    def cursorSurface(self) -> Cursor:
        if self._mode in self._cursors:
            return self._cursors[self._mode].data[1]
        return None


    def eventHandler(self, event:Event) -> bool:
        eventButton = event.dict.get("button")
        # handles switching between input modes based on where the mouse clicks
        if event.type == MB_DOWN and eventButton == MB_LCLICK:
            for btn in self._buttons:
                if btn.clicked():
                    self._mode = btn.getId()
                    return True
        return False


    def draw(self, surface:Surface) -> None:
        modeRect = None
        for btn in self._buttons:
            btnId = btn.getId()
            btn.draw(surface)
            if btnId == self._mode:
                modeRect = btn.getRect()
        if modeRect:
            drawRectBorder(surface, modeRect, Color.GREEN)


    def mode(self) -> str:
        return self._mode


    def update(self) -> None:
        for btn in self._buttons:
            btn.update()


    def setBtnWidth(self, width:int):
        self._btnWidth = width


    def setBtnHeight(self, height:int):
        self._btnHeight = height


    def setBtnStartX(self, x:int) -> None:
        self._btnStartX = x


    def setBtnStartY(self, y:int) -> None:
        self._btnStartY = y


    def setBtnStartCoords(self, coords:Tuple[int, int]) -> None:
        self._btnStartX = coords[0]
        self._btnStartY = coords[1]