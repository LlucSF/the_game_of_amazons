# -*- coding: utf-8 -*-
"""
Created on Tue May  7 17:01:15 2019

@author: LlucSF 
"""

import pygame
import pygame.freetype
from .BoardUtilities import BoardUtilities



class Amazon(BoardUtilities):
    def __init__(self, row, column, player, amazon_id, margin, cell_size, cell_per_side):
        self.row = row
        self.column = column
        self.player = player
        self.id = amazon_id
        self.margin = margin
        self.cell_size = cell_size
        self.cells_per_side = cell_per_side
        self.active = False
        self.r_shoot = False
        self.shoot_done = False
        self.can_move = True

    def move_amazon(self, board_data):
        waiting_new_click = True
        while waiting_new_click:
            ev = pygame.event.poll()
            if ev.type == pygame.MOUSEBUTTONUP:
                pos = self.get_cell_from_click()
                if pos:
                    if self.is_move_legal(board_data, pos) == 1:
                        waiting_new_click = False
                        self.r_shoot = True  # make amazon ready to shoot
                        board_data = self.overwrite_board(board_data, pos)
                    elif self.is_move_legal(board_data, pos) == 2:  # Player wants to move another amazon
                        self.active = False
                        return board_data
        return board_data

    def shoot_fire_arrow(self, board_data, board_before_move, pre_pos_amz):
        waiting_new_click = True
        while waiting_new_click:
            ev = pygame.event.poll()
            if ev.type == pygame.MOUSEBUTTONUP:
                pos = self.get_cell_from_click()
                if pos:
                    if self.is_move_legal(board_data, pos) == 1:
                        waiting_new_click = False
                        self.active = False
                        self.r_shoot = False
                        self.shoot_done = True
                        board_data = self.overwrite_board(board_data, pos)
                    elif self.is_move_legal(board_data, pos) == 2:
                        self.active = False
                        self.r_shoot = False
                        self.row = pre_pos_amz[0]
                        self.column = pre_pos_amz[1]
                        return board_before_move
        return board_data

    def is_move_legal(self, board_data, new_pos):
        row_diff = new_pos[0] - self.row
        col_diff = new_pos[1] - self.column
        if col_diff < 0:
            step_col = -1
        else:
            step_col = 1

        if row_diff < 0:
            step_row = -1
        else:
            step_row = 1

        if row_diff == 0 and col_diff == 0:
            self.active = False
            return 2  # 2 means unselected

        if abs(row_diff) == abs(col_diff):
            for i in range(1, abs(row_diff) + 1):
                if board_data[self.row + (i * step_row)][self.column + (i * step_col)] != 0:
                    return 0
                return 1

        if row_diff == 0 and col_diff != 0:
            for i in range(self.column + step_col, new_pos[1] + step_col, step_col):
                if board_data[self.row][i] != 0:
                    return 0
            return 1

        if row_diff != 0 and col_diff == 0:
            for i in range(self.row + step_row, new_pos[0] + step_row, step_row):
                if board_data[i][self.column] != 0:
                    return 0
            return 1
        return 0

    def overwrite_board(self, board_data, new_pos):
        if self.r_shoot:
            board_data[new_pos[0]][new_pos[1]] = self.player
            board_data[self.row][self.column] = 0
            self.row = new_pos[0]
            self.column = new_pos[1]
        if self.shoot_done:
            board_data[new_pos[0]][new_pos[1]] = 3
        return board_data



