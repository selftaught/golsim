import pygame

from gameoflife.colors import BLACK

class Button:
    def __init__(self, text:str, font:pygame.font, x:int, y:int, w:int, h:int) -> None:
        self.text = text
        self.rect = pygame.Rect(x, y, w, h)

    def draw(self, screen:pygame.Surface):
        pygame.draw.rect(screen, BLACK, self.rect)