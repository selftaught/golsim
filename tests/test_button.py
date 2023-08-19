from gameoflife.button import BaseButton, RectButton, CircleButton, ButtonText
from gameoflife.colors import BLUE, GREY, RED
from pygame import Rect
from pygame.color import Color

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

    def getButton(self):
        return BaseButton(
            self.baseButtonText,
            self.baseButtonX,
            self.baseButtonY,
            self.baseButtonBgColor
        )

    def test_init(self):
        button = self.getButton()
        assert button.getX() == self.baseButtonX
        assert button.getY() == self.baseButtonY
        assert button.getBackgroundColor() == self.baseButtonBgColor
        assert button.getText() == self.baseButtonText

    def test_setX(self):
        button = self.getButton()
        newX = random.randint(0, 300)
        button.setX(newX)
        assert button.getX() == newX

    def test_setY(self):
        button = self.getButton()
        newY = random.randint(0, 300)
        button.setY(newY)
        assert button.getY() == newY

    def test_setFont(self):
        button = self.getButton()
        newFont = pygame.font.Font(None, 100)
        button.setFont(newFont)
        assert button.font is newFont

    def test_setBackgroundColor(self):
        button = self.getButton()
        button.setBackgroundColor(RED)
        assert button.getBackgroundColor() == RED

    def test_setHoverBackgroundColor(self):
        button = self.getButton()
        button.setHoverBackgroundColor(RED)
        assert button.getHoverBackgroundColor() == RED

    def test_setBorder(self):
        button = self.getButton()
        for b in [True, False]:
            button.setBorder(b)
            assert button.border == b

    def test_setBorderColor(self):
        button = self.getButton()
        button.setBorderColor(BLUE)
        assert button.getBorderColor() == BLUE

    def test_setText(self):
        button = self.getButton()
        button.setText(ButtonText.PATTERNS)
        assert button.getText() == ButtonText.PATTERNS

    def test_unimplementedDrawRaises(self):
        button = self.getButton()
        surf = pygame.surface.Surface((10, 10))
        with pytest.raises(NotImplementedError):
            button.draw(surf)

    def test_unimplementedClickedRaises(self):
        button = self.getButton()
        with pytest.raises(NotImplementedError):
            button.clicked(0, 0)

    def test_unimplementedUpdateRaises(self):
        button = self.getButton()
        with pytest.raises(NotImplementedError):
            button.update()


class TestCircleButton:
    circleButtonText : str = "X"
    circleButtonX : int = 50
    circleButtonY : int = 50
    circleButtonRadius : float = 4.0
    circleButtonBgColor : Color = GREY

    def getButton(self):
        return CircleButton(
            self.circleButtonText,
            self.circleButtonX,
            self.circleButtonY,
            self.circleButtonRadius,
            self.circleButtonBgColor
        )

    def test_init(self):
        button = self.getButton()
        assert button.getText() == self.circleButtonText
        assert button.getX() == self.circleButtonX
        assert button.getY() == self.circleButtonY
        assert button.getRadius() == self.circleButtonRadius
        assert button.getBackgroundColor() == self.circleButtonBgColor

    def test_radius(self):
        button = self.getButton()
        radius = 5.0
        button.setRadius(radius)
        assert button.getRadius() == radius

    def test_clicked(self):
        pass # TODO


class TestRectButton:
    rectButtonText : str = "Rect"
    rect = Rect(50, 50, 100, 30)
    rectButtonBgColor : Color = GREY

    def getButton(self):
        return RectButton(
            self.rectButtonText,
            bgColor=self.rectButtonBgColor
        )

    def test_init(self):
        button = self.getButton()
        assert button.getText() == self.rectButtonText
        assert button.getRect() == Rect(0, 0, 0, 0)
        assert button.getW() == 0
        assert button.getH() == 0
        assert button.getX() == 0
        assert button.getY() == 0
        assert button.getBackgroundColor() == self.rectButtonBgColor

    def test_height(self):
        button = self.getButton()
        height = 56
        button.setH(height)
        assert button.getH() == height

    def test_width(self):
        button = self.getButton()
        width = 120
        button.setW(width)
        assert button.getW() == width

    def test_clicked(self):
        pass # TODO

    def test_rect(self):
        button = self.getButton()
        button.setRect(self.rect)
        assert button.getRect() == self.rect
        assert button.getW() == self.rect.width
        assert button.getH() == self.rect.height
        assert button.getX() == self.rect.x
        assert button.getY() == self.rect.y
