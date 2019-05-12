# -*- coding: utf-8 -*-
"""
Created on Tue May  7 17:01:15 2019

@author: LlucSF 
"""

import pygame
import pygame.freetype
import copy
import networkx as nx
from math import trunc
from numpy import zeros


class BoardUtilities:  # global class containing general utilites for other classes
    def get_cell_from_click(self):
        # Get mouse position and transform it into row/column
        x_mouse, y_mouse = (pygame.mouse.get_pos())
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


class Player:
    def __init__(self, player_name, player_score, player_number, number_of_amazons):
        self.score = player_score
        self.active = False
        self.number = player_number
        self.name = player_name
        self.amazons_IDs = []
        self.number_of_amazons = number_of_amazons
        self.looser = False

    def add_score(self, new_score):
        self.score = self.score + new_score


class Game(BoardUtilities):
    def __init__(self, max_score, list_of_names, previous_scores, first_player, cells_per_side, load_game, saved_game):
        self.play_again = False
        self.max_score = max_score
        self.cells_per_side = cells_per_side
        self.surface_sz = 600  # surface is gonna be 600x600
        self.board_sz = 480  # board is gonna be 480x480
        self.margin = (self.surface_sz - self.board_sz)
        self.board_origin = self.margin / 2
        self.cell_size = self.board_sz / self.cells_per_side
        self.surface = pygame.display.set_mode((self.surface_sz, self.surface_sz))
        self.total_number_of_amazons = self.cells_per_side - 2
        self.number_of_amazons_per_player = int(self.total_number_of_amazons/2)
        self.end_game = False
        # two players, first_player starts
        self.players = []
        for i in range(2):
            self.players.append(Player(list_of_names[i], previous_scores[i], i, self.number_of_amazons_per_player))
        self.players[first_player].active = True
        # game's amazon instances list
        self.amazons = []
        if load_game:
            self.board_data = saved_game
        else:
            self.board_data, self.board_names = self.fill_new_board()

    # Exchanges the active players, refresh the immobilized amazon numbers and check if there's already a winner
    def next_turn(self):  # Exchange the turn
        for player in self.players:
            if player.active:
                player.active = False
            else:
                player.active = True

        for amazon in self.amazons:
            amazon.shoot_done = False

        self.check_immobilized_amazons()
        self.check_end_game()

    # Check if there's a player without movable amazons.
    def check_end_game(self):
        for i in self.players:
            if i.number_of_amazons == 0:
                i.looser = True
                self.end_game = True

    # Check if there's any new immobilized amazon in the current turn or any of them can move again.
    def check_immobilized_amazons(self):
        for i in self.amazons:
            if len(self.check_cell_surroundings(i.row, i.column)) == 0:
                if i.can_move:
                    i.can_move = False
                    self.players[i.player-1].number_of_amazons -= 1
                    print("Amazon", str(i.id), "of player", i.player, "can't move")
                    print("Player", i.player, "can still move", self.players[i.player-1].number_of_amazons, "amazons")

            elif not i.can_move:
                i.can_move = True
                self.players[i.player-1].number_of_amazons += 1
                print("Amazon", str(i.id), "of player", i.player, "can move again!")
                print("Player", i.player, "now move", self.players[i.player - 1].number_of_amazons, "amazons")

    # Starting function of the game.
    def start_and_play_new_game(self):
        pygame.init()  # Prepare the pygame module for use
        pygame.display.set_caption("LlucSF's Amazons")

        self.draw_board()

        while self.players[0].score < self.max_score or self.players[1].score < self.max_score:  # while no winner
            new_event = False  # Down the draw flag
            ev = pygame.event.poll()  # Look for any event
            if ev.type != pygame.NOEVENT:
                if ev.type == pygame.QUIT:  # Window close button clicked?
                    # self.save_data()
                    break  # ... leave game loop

                if ev.type == pygame.MOUSEBUTTONUP:
                    clicked_cell = self.get_cell_from_click()
                    if clicked_cell:
                        amz_id = self.amazon_in_cell(clicked_cell[0], clicked_cell[1])
                        if amz_id >= 0:
                            if self.players[self.amazons[amz_id].player - 1].active and self.amazons[amz_id].can_move:
                                new_event = True
                                self.amazons[amz_id].active = True
                                board_before_move = copy.deepcopy(self.board_data)
                                pre_pos_amz = (self.amazons[amz_id].row, self.amazons[amz_id].column)
                                self.draw_board()  # redraw to show the active amazon
                                self.board_data = self.amazons[amz_id].move_amazon(
                                    self.board_data)  # check if the move is legal and overwrites the board
                                if self.amazons[amz_id].r_shoot:  # player has move it
                                    self.draw_board()  # redraw to show the ready to shoot amazon
                                    self.board_data = self.amazons[amz_id].shoot_fire_arrow(self.board_data,
                                                                                            board_before_move,
                                                                                            pre_pos_amz)
                                    if self.amazons[amz_id].shoot_done:
                                        self.next_turn()

                if ev.type == pygame.KEYDOWN:
                    new_event = True
                    if ev.key == pygame.K_r:
                        print("Game reset!")
                        self.board_data = self.fill_new_board()
                    if ev.key == pygame.K_s:
                        self.players[0].score += 1
                        self.players[1].score += 1
                        self.draw_board()
            if new_event:
                self.draw_board()

            if self.end_game:
                for i in self.players:
                    if not i.looser:
                        print(i.name, "is the winner!")
                        new_score = self.get_score_from_cells()
                        print(new_score)
                        i.add_score(new_score)
                        if self.play_again:
                            self.fill_new_board()
                            self.start_and_play_new_game()
                        break
                break

        while True:
            ev = pygame.event.poll()  # Look for any event
            if ev.type != pygame.NOEVENT:
                if ev.type == pygame.QUIT:  # Window close button clicked?
                    break
        pygame.quit()  # Once we leave the loop, close the window.

    # Returns a predefined board data and creates Amazon class instances.
    def fill_new_board(self):
        # Load the initial board for each allowed number of cells_per_side
        if self.cells_per_side == 4:
            board_data = [[0, 0, 1, 0],
                          [0, 0, 0, 0],
                          [0, 0, 0, 0],
                          [0, 2, 0, 0]]

        elif self.cells_per_side == 6:
            board_data = [[0, 0, 0, 1, 0, 0],
                          [0, 0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 1],
                          [2, 0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0],
                          [0, 0, 2, 0, 0, 0]]

        elif self.cells_per_side == 8:
            board_data = [[0, 0, 0, 1, 0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0, 0, 1],
                          [1, 0, 0, 0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0, 0, 2],
                          [2, 0, 0, 0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 2, 0, 0, 0]]

        elif self.cells_per_side == 10:
            board_data = [[0, 0, 0, 1, 0, 0, 1, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                          [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                          [2, 0, 0, 0, 0, 0, 0, 0, 0, 2],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                          [0, 0, 0, 2, 0, 0, 2, 0, 0, 0]]

        else:
            return print("Only 6x6 ,8x8 and 10x10 games are allowed")

        board_names = zeros((self.cells_per_side, self.cells_per_side))
        name_cnt = 0
        for row in range(0, self.cells_per_side):
            for col in range(0, self.cells_per_side):
                board_names[row][col] = name_cnt
                name_cnt += 1

        # fill the amazon instances with the board data
        amzn_id = 0
        for i in range(self.cells_per_side):
            for j in range(self.cells_per_side):
                if board_data[i][j] == 1:
                    self.amazons.append(Amazon(i, j, 1, amzn_id, self.margin, self.cell_size, self.cells_per_side))
                    self.players[0].amazons_IDs.append(amzn_id)
                    amzn_id = amzn_id + 1
                if board_data[i][j] == 2:
                    self.amazons.append(Amazon(i, j, 2, amzn_id, self.margin, self.cell_size, self.cells_per_side))
                    self.players[0].amazons_IDs.append(amzn_id)
                    amzn_id = amzn_id + 1

        return board_data, board_names

    # Draw all the graphics of the game
    def draw_board(self):
        # define colours in rgb
        white, light_blue, turquoise, red = (255, 255, 255), (224, 255, 255), (95, 158, 160), (255, 0, 0)
        black, player1, player2, grey = (0, 0, 0), (182, 213, 59), (163, 97, 44), (175, 175, 175)

        # painting the surface, the contour of the board and creating the text elements
        self.surface.fill(white)
        board_contour = (self.board_origin - 1, self.board_origin - 1, self.board_sz + 2, self.board_sz + 2)
        pygame.draw.rect(self.surface, black, board_contour, 1)

        my_font = pygame.font.SysFont('Comic Sans MS', 15)
        text_surface = list()
        text_surface.append(
            my_font.render(str(self.players[0].name) + "'s score:  " + str(self.players[0].score), False, (0, 0, 0)))
        text_surface.append(
            my_font.render(str(self.players[1].name) + "'s score:  " + str(self.players[1].score), False, (0, 0, 0)))

        for i in self.players:
            if i.active:
                if i.number == 0:
                    text_surface.append(my_font.render(str(i.name) + "'s turn. Kiwi amazons move.", False, (0, 0, 0)))
                else:
                    text_surface.append(my_font.render(str(i.name) + "'s turn. Coco amazons move.", False, (0, 0, 0)))

        # painting the floor like a chess board
        for row in range(0, self.cells_per_side, 2):
            for col in range(0, self.cells_per_side, 2):
                small_rect = (
                    self.board_origin + (self.cell_size * col),
                    self.board_origin + (self.cell_size * row),
                    self.cell_size,
                    self.cell_size)
                self.surface.fill(grey, small_rect)

        for row in range(1, self.cells_per_side + 1, 2):
            for col in range(1, self.cells_per_side + 1, 2):
                small_rect = (
                    self.board_origin + (self.cell_size * col),
                    self.board_origin + (self.cell_size * row),
                    self.cell_size,
                    self.cell_size)
                self.surface.fill(grey, small_rect)

        for row in range(0, self.cells_per_side, 2):
            for col in range(1, self.cells_per_side + 1, 2):
                small_rect = (
                    self.board_origin + (self.cell_size * col),
                    self.board_origin + (self.cell_size * row),
                    self.cell_size,
                    self.cell_size)
                self.surface.fill(white, small_rect)

        for row in range(1, self.cells_per_side, 2):
            for col in range(0, self.cells_per_side, 2):
                small_rect = (
                    self.board_origin + (self.cell_size * col),
                    self.board_origin + (self.cell_size * row),
                    self.cell_size,
                    self.cell_size)
                self.surface.fill(white, small_rect)

        # painting amazons and fires
        for column in range(self.cells_per_side):
            for row in range(self.cells_per_side):
                if self.board_data[row][column] == 1:
                    amazon = (int(self.board_origin + (self.cell_size * column) + round(self.cell_size / 2)),
                              int(self.board_origin + (self.cell_size * row) + round(self.cell_size / 2)))
                    pygame.draw.circle(self.surface, player1, amazon, round(self.cell_size / 3))

                if self.board_data[row][column] == 2:
                    amazon = (int(self.board_origin + (self.cell_size * column) + round(self.cell_size / 2)),
                              int(self.board_origin + (self.cell_size * row) + round(self.cell_size / 2)))
                    pygame.draw.circle(self.surface, player2, amazon, round(self.cell_size / 3))

                if self.board_data[row][column] == 3:
                    l1_s = (self.board_origin + (self.cell_size * column) + (self.cell_size/5),
                            self.board_origin + (self.cell_size * row) + (self.cell_size/5))

                    l1_e = (self.board_origin + (self.cell_size * column) + (4*self.cell_size/5),
                            self.board_origin + (self.cell_size * row) + (4*self.cell_size/5))

                    l2_s = (self.board_origin + (self.cell_size * column) + (4*self.cell_size/5),
                            self.board_origin + (self.cell_size * row) + (self.cell_size/5))

                    l2_e = (self.board_origin + (self.cell_size * column) + (self.cell_size/5),
                            self.board_origin + (self.cell_size * row) + (4*self.cell_size/5))

                    pygame.draw.line(self.surface, red, l1_s, l1_e, 5)
                    pygame.draw.line(self.surface, red, l2_s, l2_e, 5)

        # painting active amazons different
        for i in range(self.total_number_of_amazons):
            if self.amazons[i].active:
                amazon = (int(self.board_origin + (self.cell_size * self.amazons[i].column) + round(self.cell_size/2)),
                          int(self.board_origin + (self.cell_size * self.amazons[i].row) + round(self.cell_size/2)))
                pygame.draw.circle(self.surface, black, amazon, round(self.cell_size / 3) + 2, 2)
                pygame.draw.circle(self.surface, black, amazon, round(self.cell_size / 6) + 2, 2)
                if self.amazons[i].r_shoot:
                    pygame.draw.circle(self.surface, red, amazon, round(self.cell_size / 3) + 2, 2)
                    pygame.draw.circle(self.surface, red, amazon, round(self.cell_size / 6) + 2, 2)

        # Now the surface is ready, tell pygame to display it!
        self.surface.blit(text_surface[0], (10, 10))
        self.surface.blit(text_surface[1], (10, 30))
        self.surface.blit(text_surface[2], (int(round(self.surface_sz / 2)), 10))
        pygame.display.flip()

    # For a given cell_row and cell_column, checks if there's an amazon,
    def amazon_in_cell(self, cell_row, cell_column):
        for i in self.amazons:
            if i.row == cell_row and i.column == cell_column and i.can_move:
                return i.id
        return -1

    # Checks the surroundings of a cell.
    # Returns a list of the surrounding empty cells if any, else returns logic False
    def check_cell_surroundings(self, cell_row, cell_column):

        # List containing the empty cells surrounding cell (cell_row, cell_column)
        empty_cells = []

        # Establishing the neighborhood indexes of the cell
        if cell_row != 0:
            up_row = cell_row - 1
        else:
            up_row = 0

        if cell_row != self.cells_per_side - 1:
            down_row = cell_row + 1
        else:
            down_row = self.cells_per_side - 1

        if cell_column != 0:
            left_column = cell_column - 1
        else:
            left_column = 0

        if cell_column != self.cells_per_side - 1:
            right_column = cell_column + 1
        else:
            right_column = self.cells_per_side - 1

        # Check for each cell in the neighborhood if its empty, if true then append it to the list
        for row in range(up_row, down_row + 1):
            for col in range(left_column, right_column + 1):
                if self.board_data[row][col] == 0:
                    empty_cells.append((row, col))
        return empty_cells

    # Score calculating function
    def get_score_from_cells(self):
        for player in self.players:
            if not player.looser:
                score_graph = nx.Graph()
                graph_size = 0
                for winner_amazon in player.amazons_IDs:
                    if self.amazons[winner_amazon].can_move:
                        is_graph_growing = True
                        row = self.amazons[winner_amazon].row
                        col = self.amazons[winner_amazon].column
                        while is_graph_growing:
                            empty_neighbors = self.check_cell_surroundings(row, col)
                            for neighbor_row, neighbor_col in empty_neighbors:
                                # score_graph.add_node(int(self.board_names[neighbor_row][neighbor_col]))
                                score_graph.add_node((neighbor_row, neighbor_col))
                                if graph_size < score_graph.number_of_nodes():
                                    graph_size = score_graph.number_of_nodes()
                                else:
                                    is_graph_growing = False

        return graph_size

###############################################################################################################
###############################################################################################################
###############################################################################################################


def main(names, scores, max_score, cells_per_side, first_player, load_game, saved_game):
    my_game = Game(max_score, names, scores, first_player - 1, cells_per_side, load_game, saved_game)
    my_game.start_and_play_new_game()
    return "Bye"


def score_counting_test(names, scores, max_score, cells_per_side, first_player, load_game, saved_game):
    my_game = Game(max_score, names, scores, first_player - 1, cells_per_side, load_game, saved_game)
    my_game.start_and_play_new_game()
    return"Test done"


name = ["Júlia", "Lluc"]
score = [0, 0]
main(name, score, 10, 4, 2, False, None)

