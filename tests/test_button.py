from gameoflife.button import BaseButton, RectButton, CircleButton, ButtonText
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

    def getBaseButton(self):
        return BaseButton(
            self.baseButtonText,
            self.baseButtonX,
            self.baseButtonY,
            self.baseButtonW,
            self.baseButtonBgColor
        )

    def test_init(self):
        bb = self.getBaseButton()
        assert bb.x == self.baseButtonX
        assert bb.y == self.baseButtonY
        assert bb.w == self.baseButtonW
        assert bb.bgColor == self.baseButtonBgColor
        assert bb.text == self.baseButtonText

    def test_setX(self):
        bb = self.getBaseButton()
        newX = random.randint(0, 300)
        bb.setX(newX)
        assert bb.x == newX

    def test_setY(self):
        bb = self.getBaseButton()
        newY = random.randint(0, 300)
        bb.setY(newY)
        assert bb.y == newY

    def test_setW(self):
        bb = self.getBaseButton()
        newW = random.randint(0, 300)
        bb.setW(newW)
        assert bb.w == newW

    def test_setFont(self):
        bb = self.getBaseButton()
        newFont = pygame.font.Font(None, 100)
        bb.setFont(newFont)
        assert bb.font is newFont

    def test_setBackgroundColor(self):
        bb = self.getBaseButton()
        bb.setBackgroundColor(RED)
        assert bb.bgColor == RED

    def test_setHoverBackgroundColor(self):
        bb = self.getBaseButton()
        bb.setBackgroundColor(RED)
        assert bb.bgColor == RED

    def test_setBorder(self):
        bb = self.getBaseButton()
        for b in [True, False]:
            bb.setBorder(b)
            assert bb.border == b

    def test_setText(self):
        bb = self.getBaseButton()
        bb.setText(ButtonText.PATTERNS)
        assert bb.getText() == ButtonText.PATTERNS

    def test_unimplementedDrawRaises(self):
        bb = self.getBaseButton()
        surf = pygame.surface.Surface((10, 10))
        with pytest.raises(NotImplementedError):
            bb.draw(surf)

    def test_unimplementedClickedRaises(self):
        bb = self.getBaseButton()
        with pytest.raises(NotImplementedError):
            bb.clicked(0, 0)

    def test_unimplementedUpdateRaises(self):
        bb = self.getBaseButton()
        with pytest.raises(NotImplementedError):
            bb.update()


class TestCircleButton:
    pass


class TestRectButton:
    pass