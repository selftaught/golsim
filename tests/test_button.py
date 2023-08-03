from gameoflife.button import BaseButton, RectButton, CircleButton, ButtonID
from gameoflife.colors import GREY, RED

import pygame
import pytest
import random

pygame.init()

class TestBaseButton:
    baseButtonX = 0
    baseButtonY = 0
    baseButtonW = 100
    baseButtonBgColor = GREY
    baseButtonText = "Base Button"

    def _baseButton(self):
        return BaseButton(
            self.baseButtonText,
            self.baseButtonX,
            self.baseButtonY,
            self.baseButtonW,
            self.baseButtonBgColor
        )

    def test_init(self):
        bb = self._baseButton()
        assert bb.x == self.baseButtonX
        assert bb.y == self.baseButtonY
        assert bb.w == self.baseButtonW
        assert bb.bgColor == self.baseButtonBgColor
        assert bb.text == self.baseButtonText

    def test_getID(self):
        bb = self._baseButton()
        bb.setID(ButtonID.EXIT)
        assert bb.getID() == ButtonID.EXIT

    def test_setX(self):
        bb = self._baseButton()
        newX = random.randint(0, 300)
        bb.setX(newX)
        assert bb.x == newX

    def test_setY(self):
        bb = self._baseButton()
        newY = random.randint(0, 300)
        bb.setY(newY)
        assert bb.y == newY

    def test_setW(self):
        bb = self._baseButton()
        newW = random.randint(0, 300)
        bb.setW(newW)
        assert bb.w == newW

    def test_setFont(self):
        bb = self._baseButton()
        newFont = pygame.font.Font(None, 100)
        bb.setFont(newFont)
        assert bb.font is newFont

    def test_setBackgroundColor(self):
        bb = self._baseButton()
        bb.setBackgroundColor(RED)
        assert bb.bgColor == RED

    def test_setHoverBackgroundColor(self):
        bb = self._baseButton()
        bb.setBackgroundColor(RED)
        assert bb.bgColor == RED

    def test_setBorder(self):
        bb = self._baseButton()
        for b in [True, False]:
            bb.setBorder(b)
            assert bb.border == b

    def test_setText(self):
        bb = self._baseButton()
        newText = "0xc0decafe"
        bb.setText(newText)
        assert bb.text == newText

    def test_setID(self):
        bb = self._baseButton()
        bb.setID(ButtonID.STOP)
        assert bb.id == ButtonID.STOP
        bb.setID(ButtonID.START)
        assert bb.id == ButtonID.START

    def test_unimplementedDrawRaises(self):
        bb = self._baseButton()
        surf = pygame.surface.Surface((10, 10))
        with pytest.raises(NotImplementedError):
            bb.draw(surf)

    def test_unimplementedClickedRaises(self):
        bb = self._baseButton()
        with pytest.raises(NotImplementedError):
            bb.clicked(0, 0)

    def test_unimplementedUpdateRaises(self):
        bb = self._baseButton()
        with pytest.raises(NotImplementedError):
            bb.update()


class TestCircleButton:
    pass


class TestRectButton:
    pass