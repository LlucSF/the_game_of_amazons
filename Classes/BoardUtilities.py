
import pygame
import pygame.freetype
from math import trunc


class BoardUtilities:  # global class containing general utilites for other classes
    def get_cell_from_click(self):
        # Get mouse position and transform it into row/column
        x_mouse, y_mouse = pygame.mouse.get_pos()
        row = (y_mouse - round(self.margin / 2)) / self.cell_size
        column = (x_mouse - round(self.margin / 2)) / self.cell_size

        # check if the cell is out of the board
        if row > 0 and trunc(row) < self.cells_per_side:
            row = trunc(row)
        else:
            print("You are clicking out of the board!")
            return False

        if column > 0 and trunc(column) < self.cells_per_side:
            column = trunc(column)
        else:
            print("You are clicking out of the board!")
            return False
        return row, column

