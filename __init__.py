

from Classes.Game import Game


names = ["Júlia", "Lluc"]
scores = [0, 0]
max_score = 20
first_player = 2
cells_per_side = 10

my_game = Game(max_score, scores, first_player - 1, cells_per_side)
my_game.draw_menu()
