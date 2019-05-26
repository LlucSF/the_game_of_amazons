
import copy
import networkx as nx
import pygame.freetype
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from .pygame_functions import *
from .BoardUtilities import BoardUtilities
from .Amazon import Amazon
from .Player import Player
import matplotlib.pyplot as plt
from matplotlib.pyplot import ion


class Game(BoardUtilities):
    def __init__(self, max_score, previous_scores, first_player, cells_per_side, list_of_names, load_game, saved_game):
        super().__init__()
        self.play_again = False
        self.royal_end = False
        self.end_game = False
        self.its_a_draw = False
        self.quit = False
        self.load_game = load_game
        self.max_score = max_score  # max score a player can reach
        self.saved_game = saved_game
        self.cells_per_side = cells_per_side
        self.surface_sz = 600  # surface is gonna be 600x600
        self.board_sz = 480  # board is gonna be 480x480
        self.margin = (self.surface_sz - self.board_sz)
        self.board_origin = self.margin / 2
        self.cell_size = self.board_sz / self.cells_per_side
        self.surface = None
        self.total_number_of_amazons = None
        self.number_of_amazons_per_player = None
        self.score_graph = nx.Graph()  # graph used to compute the final score at each ended round
        self.board_data = self.fill_new_board()

        # Amazon instances
        self.amazons = []
        amazon_id = 0
        for i in range(0, self.cells_per_side):
            for j in range(0, self.cells_per_side):
                if self.board_data[i][j] == 1:
                    self.amazons.append(Amazon(i, j, 1, amazon_id, self.margin, self.cell_size, self.cells_per_side))
                    amazon_id = amazon_id + 1
                if self.board_data[i][j] == 2:
                    self.amazons.append(Amazon(i, j, 2, amazon_id, self.margin, self.cell_size, self.cells_per_side))
                    amazon_id = amazon_id + 1
        self.total_number_of_amazons = amazon_id
        self.number_of_amazons_per_player = int(self.total_number_of_amazons / 2)

        # Player instances
        self.players = []
        for player in range(2):
            self.players.append(Player(list_of_names[player], previous_scores[player],
                                       player, self.number_of_amazons_per_player))
            for amazon in self.amazons:
                if amazon.player == (player+1):
                    self.players[player].amazons_ids.append(amazon.id)
        self.players[first_player].active = True

        # Creating amazons name dictionary
        self.amazon_names_book = []
        for player in self.players:
            for id in player.amazons_ids:
                self.amazon_names_book.append(str(str(player.name) + str(id)))
        print(self.amazon_names_book)

    # Exchanges the active players, refresh the immobilized amazon numbers and check if there's already a winner
    def next_turn(self):
        # Exchange the turn
        for player in self.players:
            if player.active:
                player.active = False
            else:
                player.active = True

        # Turn down all the shoot_done flags
        for amazon in self.amazons:
            amazon.shoot_done = False

        # Check for immobilized amazons
        self.check_immobilized_amazons()

        # Draw before check end game
        self.draw_board()
        self.royal_chamber_identifier()
        # Check is the game is over
        self.check_end_game()

    # Check if there's a player without movable amazons.
    def check_end_game(self):
        if self.players[0].number_of_amazons == 0 and self.players[1].number_of_amazons != 0:
            self.players[1].winner = True
            self.end_game = True
        elif self.players[1].number_of_amazons == 0 and self.players[0].number_of_amazons != 0:
            self.players[0].winner = True
            self.end_game = True
        elif self.players[1].number_of_amazons == 0 and self.players[0].number_of_amazons == 0:
            self.end_game = True
            self.its_a_draw = True

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
                print("Player", i.player, "now move", self.players[i.player-1].number_of_amazons, "amazons")

    # Starting function of the game.
    def start_and_play_new_game(self):
        pygame.init()  # Prepare the pygame module for use
        pygame.display.set_caption("LlucSF's Amazons")

        self.draw_board()

        while self.players[0].score < self.max_score and self.players[1].score < self.max_score and not self.quit:
            new_event = False  # Down the draw flag
            ev = pygame.event.poll()  # Look for any event

            if ev.type != pygame.NOEVENT:
                if ev.type == pygame.QUIT:
                    self.quit = True

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
                        self.reset_game()
                        self.draw_board()

                    if ev.key == pygame.K_s:
                        self.save_game()
                        break

            if new_event:
                self.draw_board()

            if self.royal_end:
                self.draw_winner_message()
                while not self.play_again:
                    ev = pygame.event.poll()
                    if ev.type != pygame.NOEVENT:
                        if ev.type == pygame.QUIT:
                            self.quit = True
                            break
                        if ev.type == pygame.KEYDOWN:
                            if ev.key == pygame.K_q:
                                self.quit = True
                                break
                            if ev.key == pygame.K_s:
                                self.save_game()
                                break
                            if ev.key == pygame.K_y:
                                self.play_again = True
                                self.reset_game()
                                self.draw_board()
                self.play_again = False

            if self.end_game:
                # Add score to the winner player
                for i in self.players:
                    if i.winner:
                        new_score = self.get_score_from_cells()
                        i.add_score(new_score)
                        self.draw_board()
                self.draw_winner_message()
                while not self.play_again:
                    ev = pygame.event.poll()
                    if ev.type != pygame.NOEVENT:
                        if ev.type == pygame.QUIT:
                            self.quit = True
                            break
                        if ev.type == pygame.KEYDOWN:
                            if ev.key == pygame.K_q:
                                self.quit = True
                                break
                            if ev.key == pygame.K_s:
                                self.save_game()
                                break
                            if ev.key == pygame.K_y:
                                self.play_again = True
                                self.reset_game()
                                self.draw_board()
                self.play_again = False

    # Returns a predefined board data and creates Amazon class instances.
    def fill_new_board(self):
        if self.load_game:
            board_data = copy.deepcopy(self.saved_game)
            self.cell_size = self.board_sz / self.cells_per_side
            self.load_game = False

        else:
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
                return print("Only 4x4, 6x6 ,8x8 and 10x10 games are allowed")

        return board_data

    # Draw all the graphics of the game
    def draw_board(self):
        # Define colours in rgb
        self.surface = screenSize(self.surface_sz, self.surface_sz, 50, 50)
        pygame.display.set_caption("The game of amazons")
        white, light_blue, turquoise, red = (255, 255, 255), (224, 255, 255), (95, 158, 160), (255, 0, 0)
        black, player1, player2, grey = (0, 0, 0), (182, 213, 59), (163, 97, 44), (175, 175, 175)

        # painting the surface, the contour of the board and creating the text elements
        self.surface.fill((205, 133, 63))
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

        text_surface.append(
            my_font.render("Max score:  " + str(self.max_score), False, (0, 0, 0)))
        text_surface.append(my_font.render("Press 'S' to save and quit the game. Game must be saved in a .txt file.",
                                           False, (0, 0, 0)))

        # painting the floor like a chess board
        for row in range(0, self.cells_per_side, 2):
            for col in range(0, self.cells_per_side, 2):
                small_rect = (
                    self.board_origin + (self.cell_size * col),
                    self.board_origin + (self.cell_size * row),
                    self.cell_size,
                    self.cell_size)
                self.surface.fill((188, 143, 143), small_rect)

        for row in range(1, self.cells_per_side + 1, 2):
            for col in range(1, self.cells_per_side + 1, 2):
                small_rect = (
                    self.board_origin + (self.cell_size * col),
                    self.board_origin + (self.cell_size * row),
                    self.cell_size,
                    self.cell_size)
                self.surface.fill((188, 143, 143), small_rect)

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

        # painting amazons and fire arrows
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
        self.surface.blit(text_surface[0], (self.margin-self.cell_size, 10))
        self.surface.blit(text_surface[1], (self.margin-self.cell_size, 30))
        self.surface.blit(text_surface[2], (int(round(self.surface_sz / 2)), 30))
        self.surface.blit(text_surface[3], (int(round(self.surface_sz / 2)), 10))
        self.surface.blit(text_surface[4], (self.margin-self.cell_size, self.board_sz+int(round(self.margin/1.5))))
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

    # Keeps iterating into the score graph searching for new nodes using the check_cell_surroundings function
    def cell_propagation_iterator(self, test_cell, empty_neighbors, graph):
        # Add the previous empty_neighbors to the graph
        graph.add_node(test_cell)
        graph.add_nodes_from(empty_neighbors)

        for empty_cell in empty_neighbors:
            graph.add_edge(test_cell, empty_cell)

        for new_row, new_col in empty_neighbors:
            # For each of them, it's empty neighbors are searched ...
            new_empty_neighbors = self.check_cell_surroundings(new_row, new_col)

            # ... and those already in the graph are discarded
            non_repeated_new_empty_neighbors = []
            for node in new_empty_neighbors:
                if not graph.has_node(node):
                    non_repeated_new_empty_neighbors.append(node)

            # With the neighbors not included in the graph (if any) a new iteration starts
            if len(non_repeated_new_empty_neighbors) != 0:
                self.cell_propagation_iterator((new_row, new_col), new_empty_neighbors, graph)
            else:
                for new_empty_cell in new_empty_neighbors:
                    graph.add_edge((new_row, new_col), new_empty_cell)

    # Score calculating function
    def get_score_from_cells(self):
        # First we search the winner player
        free_amazons = 0
        for player in self.players:
            if player.winner:
                for winner_amazon in player.amazons_ids:
                    if self.amazons[winner_amazon].can_move:
                        # For each amazon of the winner player that can move a iteration is started using it's neighbors
                        free_amazons += 1
                        row = self.amazons[winner_amazon].row
                        col = self.amazons[winner_amazon].column
                        empty_neighbors = self.check_cell_surroundings(row, col)
                        self.cell_propagation_iterator(str(player.name + " " + str(winner_amazon)),
                                                       empty_neighbors, self.score_graph)

        # Return the total number of nodes, which is the number of cells a winner player can still move into,
        # and that's exactly the definition of the score
        plt.clf()
        nx.draw(self.score_graph, with_labels=1)
        plt.show()
        return self.score_graph.number_of_nodes() - free_amazons

    # Prepares the game for new game
    def reset_game(self):
        self.score_graph = nx.Graph()
        self.end_game = False
        self.royal_end = False

        # If its a draw, the next turn will be for the player with lowest score
        if self.its_a_draw:
            self.its_a_draw = False
            min_score = self.max_score
            player_with_min_score = None
            for player in range(2):
                self.players[player].active = False
                self.players[player].winner = False
                self.players[player].number_of_amazons = self.number_of_amazons_per_player
                self.players[player].amazons_ids = []
                if self.players[player].score < min_score:
                    min_score = self.players[player].score
                    player_with_min_score = player
            self.players[player_with_min_score].active = True

        # Else, the looser starts
        else:
            for player in self.players:
                if player.winner:
                    player.active = False
                else:
                    player.active = True
                player.winner = False
                player.number_of_amazons = self.number_of_amazons_per_player
                player.amazons_ids = []

        # Fill the board with the default data
        self.board_data = self.fill_new_board()

        # Restarting amazons
        del self.amazons
        self.amazons = []
        amazon_id = 0
        for i in range(0, self.cells_per_side):
            for j in range(0, self.cells_per_side):
                if self.board_data[i][j] == 1:
                    self.amazons.append(Amazon(row=i, column=j, player=1, amazon_id=amazon_id, margin=self.margin,
                                               cell_size=self.cell_size, cell_per_side=self.cells_per_side))
                    amazon_id = amazon_id + 1

                if self.board_data[i][j] == 2:
                    self.amazons.append(Amazon(row=i, column=j, player=2, amazon_id=amazon_id, margin=self.margin,
                                               cell_size=self.cell_size, cell_per_side=self.cells_per_side))
                    amazon_id = amazon_id + 1

        # Assigning new amazon ids to players
        for player in range(2):
            for amazon in self.amazons:
                if amazon.player == (player + 1):
                    self.players[player].amazons_ids.append(amazon.id)

    # Save the game in a .txt file
    def save_game(self):
        Tk().withdraw()
        file_name = askopenfilename()
        if file_name:
            file = open(str(file_name), "w")
            file.writelines(str(self.cells_per_side) + "\n")
            for i in range(self.cells_per_side):
                tmp = []
                for j in range(self.cells_per_side):
                    tmp.append(str(str(self.board_data[i][j]) + " "))
                tmp.append("\n")
                file.writelines(tmp)
            file.writelines(str(self.players[0].name + " " + self.players[1].name + "\n"))
            file.writelines(str(self.max_score) + "\n")
            file.writelines(str(str(self.players[0].score) + " " + str(self.players[1].score) + "\n"))
            for i in range(2):
                if self.players[i].active:
                    file.writelines(str(i))

    # Creates the board graph and looks for royal chambers
    def royal_chamber_identifier(self):
        plt.clf()   # Clear plot
        ion()  # Keep the game running while figure is opened

        # Graph of the whole board in the current turn
        turn_graph = nx.Graph()
        # For each players amazon iterate and grow the graph
        for player in self.players:
            for id in player.amazons_ids:
                # First empty neighbors
                amazon_cell = (self.amazons[id].row, self.amazons[id].column)
                empty_neighbors = self.check_cell_surroundings(amazon_cell[0], amazon_cell[1])

                # Iterator
                self.cell_propagation_iterator(str(str(player.name) + str(id)),
                                               empty_neighbors,
                                               self.amazons[id].domain)

                # Compose the turn graph with each iterator graph
                turn_graph = nx.compose(turn_graph, self.amazons[id].domain)

        # Draw the turn graph
        # Creation of the positions dictionary
        pos = {}
        for n in turn_graph.nodes():
            if type(n) is str:
                for amazon in self.amazons:
                    if str(self.players[amazon.player-1].name + str(amazon.id)) == n:
                        page = (amazon.column, -amazon.row)
                        break
            else:
                page = (n[1], -n[0])
            pos[n] = page

        nx.draw(turn_graph, pos, with_labels=1)
        plt.show()
        number_sub_graphs = len(list(nx.connected_component_subgraphs(turn_graph)))
        print("Number of independent graphs: " + str(number_sub_graphs))

        # If there are more than one sub-graph check if those are royal chambers
        if number_sub_graphs > 1:
            # Get the sub-graphs
            sub_graphs = nx.connected_component_subgraphs(turn_graph)
            royal_chamber_counter = 0
            royal_chamber_ownership = []
            players_in_graph = []
            # For each sub-graph check if there are only one player
            for graph in sub_graphs:
                players_in_graph.clear()
                entry = None
                for entry in self.amazon_names_book:
                    for node in graph.nodes:
                        if node == entry:
                            players_in_graph.append(entry[:-1])
                if len(set(players_in_graph)) == 1:
                    royal_chamber_counter += 1
                    royal_chamber_ownership.append(players_in_graph[0])

            # If all the sub graphs are royal chambers the game ends
            if royal_chamber_counter == number_sub_graphs:
                players_scores = [0, 0]
                graph_index = 0
                sub_graphs = nx.connected_component_subgraphs(turn_graph)
                self.royal_end = True
                for graph in sub_graphs:
                    score = graph.number_of_nodes()
                    if royal_chamber_ownership[graph_index] == self.players[0].name:
                        players_scores[0] += score
                        graph_index += 1
                    elif royal_chamber_ownership[graph_index] == self.players[1].name:
                        players_scores[1] += score
                        graph_index += 1

                # Print the number of cells each player has
                print(str(str(self.players[0].name) + " has " +
                          str(players_scores[0] - self.number_of_amazons_per_player) + " cells."))
                print(str(str(self.players[1].name) + " has " +
                          str(players_scores[1] - self.number_of_amazons_per_player) + " cells."))

                # The highest scores the difference
                if players_scores[0] > players_scores[1]:
                    self.players[0].add_score(players_scores[0]-players_scores[1])
                    self.players[0].winner = True
                    self.players[1].winner = False
                elif players_scores[1] > players_scores[0]:
                    self.players[1].add_score(players_scores[1]-players_scores[0])
                    self.players[1].winner = True
                    self.players[0].winner = False
                else:
                    self.its_a_draw = True
                    self.players[0].winner = False
                    self.players[1].winner = False

        # Reset the turn_graph
        turn_graph.clear()

        # Clear amazons individual graphs
        for amazon in self.amazons:
            amazon.domain.clear()

    # Draws the winner message
    def draw_winner_message(self):
        # Message box
        message_origin = (self.surface_sz/5, self.surface_sz/3)
        message_sz = (3*self.surface_sz/5, 1*self.surface_sz/3)
        message_box = (message_origin[0], message_origin[1], message_sz[0], message_sz[1])
        pygame.draw.rect(self.surface, (205, 133, 63), message_box, 0)
        pygame.draw.rect(self.surface, (0, 0, 0), message_box, 1)

        continue_box = ((message_origin[0] + message_sz[0]/19),
                        (message_origin[1] + 5*message_sz[1]/9),
                        5*message_sz[0]/19,
                        3*message_sz[1]/9)
        pygame.draw.rect(self.surface, (188, 143, 143), continue_box, 0)
        pygame.draw.rect(self.surface, (50, 50, 50), continue_box, 1)

        save_and_quit_box = ((message_origin[0] + 7*message_sz[0]/19),
                             (message_origin[1] + 5*message_sz[1]/9),
                             5*message_sz[0]/19,
                             3*message_sz[1]/9)
        pygame.draw.rect(self.surface, (188, 143, 143), save_and_quit_box, 0)
        pygame.draw.rect(self.surface, (50, 50, 50), save_and_quit_box, 1)

        quit_box = ((message_origin[0] + 13*message_sz[0]/19),
                    (message_origin[1] + 5*message_sz[1]/9),
                    5*message_sz[0]/19,
                    3*message_sz[1]/9)
        pygame.draw.rect(self.surface, (188, 143, 143), quit_box, 0)
        pygame.draw.rect(self.surface, (50, 50, 50), quit_box, 1)

        my_big_font = pygame.font.SysFont('Comic Sans MS', 30)
        my_small_font = pygame.font.SysFont('Comic Sans MS', 15)
        text_surface = list()
        for player in self.players:
            if player.winner:
                text_surface.append(my_big_font.render(player.name + " is the winner!", False, (0, 0, 0)))
        text_surface.append(my_small_font.render(str("Continue [y]"), False, (0, 0, 0)))
        text_surface.append(my_small_font.render(str("Save [s]"), False, (0, 0, 0)))
        text_surface.append(my_small_font.render(str("Quit [q]"), False, (0, 0, 0)))

        self.surface.blit(text_surface[0],
                          (message_origin[0] + 2*message_sz[0]/19,
                           message_origin[1] + 2*message_sz[1]/9))

        self.surface.blit(text_surface[1],
                          (continue_box[0] + continue_box[2]/19,
                           continue_box[1] + 3*continue_box[3]/9))

        self.surface.blit(text_surface[2],
                          (save_and_quit_box[0] + 4*save_and_quit_box[2]/19,
                           save_and_quit_box[1] + 3*save_and_quit_box[3]/9))

        self.surface.blit(text_surface[3],
                          (quit_box[0] + 4*quit_box[2]/19,
                           quit_box[1] + 3*quit_box[3]/9))

        pygame.display.flip()

