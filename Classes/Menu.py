
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import copy
from .pygame_functions import *
from.Game import Game


class Menu:
    def __init__(self):
        self.max_score = 25
        self.player_names = ["Kiwi", "Coco"]
        self.player_names_label = ["Coco", "Kiwi"]
        self.player_scores = [0, 0]
        self.cells_per_side = 8
        self.active_player = 0
        self.textbox_1 = None
        self.textbox_2 = None
        self.wordlabel_1 = None
        self.wordlabel_2 = None

    def draw_menu(self):
        pygame.init()  # Prepare the pygame module for use
        pygame.display.set_caption("LlucSF's Amazons")
        menu_surface = screenSize(600, 200)
        pygame.display.update()

        menu_surface.fill((255, 255, 255))
        my_font = pygame.font.SysFont('Arial', 26)
        my_normal_font = pygame.font.SysFont('Arial', 22)
        my_little_font = pygame.font.SysFont('Arial', 20)

        # Cells per side check_boxes
        x_box1 = (20, 40, 20, 20)
        x_box2 = (80, 40, 20, 20)
        x_box3 = (140, 40, 20, 20)
        x_box4 = (200, 40, 20, 20)
        if self.cells_per_side == 4:
            pygame.draw.circle(menu_surface, (0, 255, 0), (31, 50), 7)

        if self.cells_per_side == 6:
            pygame.draw.circle(menu_surface, (0, 255, 0), (91, 50), 7)

        if self.cells_per_side == 8:
            pygame.draw.circle(menu_surface, (0, 255, 0), (151, 50), 7)

        if self.cells_per_side == 10:
            pygame.draw.circle(menu_surface, (0, 255, 0), (211, 50), 7)

        pygame.draw.rect(menu_surface, (50, 50, 50), x_box1, 2)
        pygame.draw.rect(menu_surface, (50, 50, 50), x_box2, 2)
        pygame.draw.rect(menu_surface, (50, 50, 50), x_box3, 2)
        pygame.draw.rect(menu_surface, (50, 50, 50), x_box4, 2)
        text_x_boxes = my_normal_font.render("Board size:", False, (0, 0, 0))
        text_x_box1 = my_little_font.render("4x4", False, (0, 0, 0))
        text_x_box2 = my_little_font.render("6x6", False, (0, 0, 0))
        text_x_box3 = my_little_font.render("8x8", False, (0, 0, 0))
        text_x_box4 = my_little_font.render("10x10", False, (0, 0, 0))
        menu_surface.blit(text_x_boxes, (20, 5))
        menu_surface.blit(text_x_box1, (45, 38))
        menu_surface.blit(text_x_box2, (105, 38))
        menu_surface.blit(text_x_box3, (165, 38))
        menu_surface.blit(text_x_box4, (225, 38))

        # Max score
        text_max_score = my_normal_font.render("Max score:", False, (0, 0, 0))
        menu_surface.blit(text_max_score, (280, 5))

        # Load game button
        button1 = (420, 20, 160, 75)
        text_button1 = my_font.render("Load game", False, (0, 0, 0))
        pygame.draw.rect(menu_surface, (190, 190, 190), button1, 0)
        pygame.draw.rect(menu_surface, (50, 50, 50), button1, 2)
        menu_surface.blit(text_button1, (449, 40))

        # New game button
        button2 = (420, 105, 160, 75)
        text_button2 = my_font.render("New game", False, (0, 0, 0))
        pygame.draw.rect(menu_surface, (190, 190, 190), button2, 0)
        pygame.draw.rect(menu_surface, (50, 50, 50), button2, 2)
        menu_surface.blit(text_button2, (448, 125))

        # Player name inputs
        self.textbox_1 = makeTextBox(20, 90, 160, 0, "Player 1 name:", 15, 24)
        self.textbox_2 = makeTextBox(20, 140, 160, 0, "Player 2 name:", 15, 24)
        showTextBox(self.textbox_1)
        showTextBox(self.textbox_2)
        self.wordlabel_1 = makeLabel(self.player_names_label[0], 22, xpos=190, ypos=100, background="white")
        self.wordlabel_2 = makeLabel(self.player_names_label[1], 22, xpos=190, ypos=150, background="white")
        showLabel(self.wordlabel_1)
        showLabel(self.wordlabel_2)

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
                if 580 > mouse_x > 420 and 180 > mouse_y > 105:
                    new_game = Game(max_score=self.max_score, previous_scores=self.player_scores,
                                    first_player=self.active_player, cells_per_side=self.cells_per_side,
                                    list_of_names=self.player_names)
                    new_game.start_and_play_new_game()
                    break

                # Load game
                if 580 > mouse_x > 420 and 95 > mouse_y > 20:
                    self.load_previous_game()
                    break

                # Player 1 textbox
                if 180 > mouse_x > 20 and 130 > mouse_y > 90:
                    text_input1 = copy.deepcopy(textBoxInput(self.textbox_1))
                    self.player_names[0] = text_input1
                    self.player_names_label[0] = text_input1
                    changeLabel(self.wordlabel_1, "                                           ")
                    self.wordlabel_1 = makeLabel(str(text_input1)[:19], 22, 190, 100, background="white")
                    showLabel(self.wordlabel_1)

                # Player 2 text box
                if 180 > mouse_x > 20 and 180 > mouse_y > 140:
                    text_input2 = copy.deepcopy(textBoxInput(self.textbox_2))
                    self.player_names[1] = text_input2
                    self.player_names_label[1] = text_input2
                    changeLabel(self.wordlabel_2, "                                           ")
                    self.wordlabel_2 = makeLabel(str(text_input2)[:19], 22, 190, 150, background="white")
                    showLabel(self.wordlabel_2)

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
            print(loaded_board_data)

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
                               list_of_names=self.player_names)

            # Activate the load_game flag and fill the board with the loaded data
            loaded_game.load_game = True
            loaded_game.saved_game = loaded_board_data
            loaded_game.board_data = loaded_game.fill_new_board()
            loaded_game.load_game = False   # Deactivate the flag
            loaded_game.start_and_play_new_game()
