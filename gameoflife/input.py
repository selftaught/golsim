from pygame.event import Event
from pygame.locals import MOUSEBUTTONDOWN
from pygame.rect import Rect
from pygame.surface import Surface
from typing import List, Tuple, Union

from gameoflife.button import BaseButton, ButtonID, RectButton
from gameoflife.colors import GREEN
from gameoflife.draw import drawRectBorder
from gameoflife.mouse import MOUSEBUTTON_LCLICK


class InputMode:
    DRAW = ButtonID.DRAW
    PAN = ButtonID.PAN

class InputModeManager:
    def __init__(self, btnWidth:int=30, btnHeight:int=30, btnMargin:int=10, btnStartX:int=0, btnStartY:int=0) -> None:
        self._btnMargin = btnMargin
        self._btnHeight = btnHeight
        self._btnWidth = btnWidth
        self._btnStartX = btnStartX
        self._btnStartY = btnStartY
        self._buttons:List[BaseButton] = []
        self._mode:Union[str, None] = None

    def addMode(self, mode:str, event:Event, imagePath:str=None, active:bool=False) -> None:
        btnX = (len(self._buttons) * self._btnWidth + self._btnMargin) + self._btnStartX
        rect = Rect(btnX, self._btnStartY, self._btnWidth, self._btnHeight)
        button = RectButton(mode, event, rect, imagePath=imagePath, border=False)
        self._buttons.append(button)
        if active:
            self._mode = mode

    def eventHandler(self, event:Event) -> bool:
        eventButton = event.dict.get("button")
        if event.type == MOUSEBUTTONDOWN and eventButton == MOUSEBUTTON_LCLICK:
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
            drawRectBorder(surface, modeRect, GREEN)

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