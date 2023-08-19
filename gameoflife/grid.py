import pygame
from gameoflife.colors import GREY_LIGHT1


class Grid:
    def __init__(
        self, cols: int, rows: int, colWidth: int, rowHeight: int, enabled: bool = True
    ):
        self.cols = cols
        self.colWidth = colWidth
        self.rows = rows
        self.rowHeight = rowHeight
        self.enabled = enabled

    def isEnabled(self) -> bool:
        return self.enabled

    def toggle(self) -> bool:
        self.enabled = not self.enabled
        return self.enabled

    def setEnabled(self, enabled) -> None:
        self.enabled = enabled

    def draw(self, screen: pygame.Surface):
        if self.enabled:
            for x in range(1, self.cols):
                line_start_x = x * self.colWidth
                line_start_y = 0
                line_end_x = x * self.colWidth
                line_end_y = self.rows * self.rowHeight
                pygame.draw.line(
                    screen,
                    GREY_LIGHT1,
                    (line_start_x, line_start_y),
                    (line_end_x, line_end_y),
                    1,
                )

            for y in range(1, self.rows):
                line_start_x = 0
                line_start_y = y * self.rowHeight
                line_end_x = self.cols * self.colWidth
                line_end_y = y * self.rowHeight
                pygame.draw.line(
                    screen,
                    GREY_LIGHT1,
                    (line_start_x, line_start_y),
                    (line_end_x, line_end_y),
                    1,
                )
