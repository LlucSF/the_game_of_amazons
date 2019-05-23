
from copy import deepcopy
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from .pygame_functions import screenSize, makeLabel, makeTextBox, showLabel, showTextBox, textBoxInput, changeLabel
from .Game import Game
import pygame


class Menu:
    def __init__(self):
        self.max_score = 25
        self.player_names = ["Kiwi", "Coco"]
        self.player_scores = [0, 0]
        self.cells_per_side = 8
        self.active_player = 0
        self.textbox_1 = None
        self.textbox_2 = None
        self.textbox_3 = None
        self.menu_surface = None

    def draw_menu(self):
        pygame.init()  # Prepare the pygame module for use
        self.menu_surface = screenSize(405, 295)
        pygame.display.set_caption("The game of amazons")
        pygame.display.update()

        self.menu_surface.fill((205, 133, 63))
        my_font = pygame.font.SysFont('Arial', 26)
        my_normal_font = pygame.font.SysFont('Arial', 20)
        my_little_font = pygame.font.SysFont('Arial', 20)

        # Cells per side check_boxes
        x_box1 = (20, 40, 20, 20)
        x_box2 = (80, 40, 20, 20)
        x_box3 = (140, 40, 20, 20)
        x_box4 = (200, 40, 20, 20)
        pygame.draw.rect(self.menu_surface, (188, 143, 143), x_box1, 0)
        pygame.draw.rect(self.menu_surface, (188, 143, 143), x_box2, 0)
        pygame.draw.rect(self.menu_surface, (188, 143, 143), x_box3, 0)
        pygame.draw.rect(self.menu_surface, (188, 143, 143), x_box4, 0)
        pygame.draw.rect(self.menu_surface, (50, 50, 50), x_box1, 2)
        pygame.draw.rect(self.menu_surface, (50, 50, 50), x_box2, 2)
        pygame.draw.rect(self.menu_surface, (50, 50, 50), x_box3, 2)
        pygame.draw.rect(self.menu_surface, (50, 50, 50), x_box4, 2)
        text_x_boxes = my_normal_font.render("Board size:", False, (0, 0, 0))
        text_x_box1 = my_little_font.render("4x4", False, (0, 0, 0))
        text_x_box2 = my_little_font.render("6x6", False, (0, 0, 0))
        text_x_box3 = my_little_font.render("8x8", False, (0, 0, 0))
        text_x_box4 = my_little_font.render("10x10", False, (0, 0, 0))
        self.menu_surface.blit(text_x_boxes, (20, 5))
        self.menu_surface.blit(text_x_box1, (45, 38))
        self.menu_surface.blit(text_x_box2, (105, 38))
        self.menu_surface.blit(text_x_box3, (165, 38))
        self.menu_surface.blit(text_x_box4, (225, 38))

        if self.cells_per_side == 4:
            pygame.draw.circle(self.menu_surface, (182, 213, 59), (31, 50), 7)

        if self.cells_per_side == 6:
            pygame.draw.circle(self.menu_surface, (182, 213, 59), (91, 50), 7)

        if self.cells_per_side == 8:
            pygame.draw.circle(self.menu_surface, (182, 213, 59), (151, 50), 7)

        if self.cells_per_side == 10:
            pygame.draw.circle(self.menu_surface, (182, 213, 59), (211, 50), 7)

        # Max score
        text_max_score = my_normal_font.render("Max score:", False, (0, 0, 0))
        self.menu_surface.blit(text_max_score, (20, 200))
        self.textbox_3 = makeTextBox(20, 230, 60, 0, str(self.max_score), 15, 22)
        showTextBox(self.textbox_3)

        # Load game button
        button1 = (225, 100, 160, 75)
        text_button1 = my_font.render("Load game", False, (0, 0, 0))
        pygame.draw.rect(self.menu_surface, (188, 143, 143), button1, 0)
        pygame.draw.rect(self.menu_surface, (50, 50, 50), button1, 2)
        self.menu_surface.blit(text_button1, (240, 120))

        # New game button
        button2 = (225, 200, 160, 75)
        text_button2 = my_font.render("New game", False, (0, 0, 0))
        pygame.draw.rect(self.menu_surface, (188, 143, 143), button2, 0)
        pygame.draw.rect(self.menu_surface, (50, 50, 50), button2, 2)
        self.menu_surface.blit(text_button2, (240, 220))

        # Player name inputs
        text_text_boxes = my_normal_font.render("Players names:", False, (0, 0, 0))
        self.menu_surface.blit(text_text_boxes, (20, 70))
        self.textbox_1 = makeTextBox(20, 100, 160, 0, self.player_names[0], 15, 22)
        self.textbox_2 = makeTextBox(20, 150, 160, 0, self.player_names[1], 15, 22)
        showTextBox(self.textbox_1)
        showTextBox(self.textbox_2)

    def menu_gui(self):
        while True:
            ev = pygame.event.poll()  # Look for any event
            if ev.type == pygame.MOUSEBUTTONUP and ev.button == 1:
                mouse_x, mouse_y = pygame.mouse.get_pos()

                # Board size check boxes
                if 60 > mouse_y > 40:
                    if 40 > mouse_x > 20:
                        self.cells_per_side = 4
                        self.draw_menu()

                    if 100 > mouse_x > 80:
                        self.cells_per_side = 6
                        self.draw_menu()

                    if 160 > mouse_x > 140:
                        self.cells_per_side = 8
                        self.draw_menu()

                    if 220 > mouse_x > 200:
                        self.cells_per_side = 10
                        self.draw_menu()

                # New game
                if (226+160) > mouse_x > 225 and (200+75) > mouse_y > 200:
                    new_game = Game(max_score=self.max_score, previous_scores=self.player_scores,
                                    first_player=self.active_player, cells_per_side=self.cells_per_side,
                                    list_of_names=self.player_names,load_game=False,saved_game=None)
                    new_game.start_and_play_new_game()
                    self.draw_menu()

                # Load game
                if (226+160) > mouse_x > 225 and (100+75) > mouse_y > 100:
                    self.load_previous_game()
                    self.draw_menu()

                # Player 1 textbox
                if 180 > mouse_x > 20 and 140 > mouse_y > 100:
                    text_input1 = deepcopy(textBoxInput(self.textbox_1))
                    self.player_names[0] = text_input1
                    self.draw_menu()

                # Player 2 text box
                if 180 > mouse_x > 20 and 190 > mouse_y > 150:
                    text_input2 = deepcopy(textBoxInput(self.textbox_2))
                    self.player_names[1] = text_input2
                    self.draw_menu()

                # Max score text box
                if (60+20) > mouse_x > 20 and 270 > mouse_y > 230:
                    text_input3 = deepcopy(textBoxInput(self.textbox_3))
                    self.max_score = int(text_input3)
                    self.draw_menu()

            if ev.type == pygame.QUIT:
                pygame.quit()
                break

    def load_previous_game(self):
        # Prepare the read file module
        Tk().withdraw()
        file_name = askopenfilename()
        if file_name:
            file = open(str(file_name), "r")

            # Read the cells per side
            index = file.readline()
            index = int(index.strip())
            self.cells_per_side = index

            # Read all the board data list
            loaded_board_data = []
            for i in range(0, index):
                tmp = file.readline()
                tmp = tmp.strip()
                tmp = tmp.split()
                tmp2 = []
                for j in range(0, index):
                    tmp2.append(int(tmp[j]))
                loaded_board_data.append(tmp2)

            # Read names
            tmp = file.readline()
            tmp = tmp.strip()
            tmp = tmp.split()
            self.player_names = [str(tmp[0]), str(tmp[1])]

            # Read max score
            tmp = file.readline()
            tmp = tmp.strip()
            tmp = tmp.split()
            self.max_score = int(tmp[0])

            # Read current scores
            tmp = file.readline()
            tmp = tmp.strip()
            tmp = tmp.split()
            self.player_scores = [int(tmp[0]), int(tmp[1])]

            # Read active player
            tmp = file.readline()
            tmp = tmp.strip()
            tmp = tmp.split()
            tmp = int(tmp[0])
            self.active_player = tmp

            # Create a new game instance
            loaded_game = Game(max_score=self.max_score, previous_scores=self.player_scores,
                               first_player=self.active_player, cells_per_side=self.cells_per_side,
                               list_of_names=self.player_names, load_game=True, saved_game=loaded_board_data)
            loaded_game.start_and_play_new_game()
            return True
        return False

    def run(self):
        self.draw_menu()
        self.menu_gui()
