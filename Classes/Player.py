

class Player:
    def __init__(self, player_name, player_score, player_number, number_of_amazons):
        self.score = player_score
        self.active = False
        self.number = player_number
        self.name = player_name
        self.amazons_ids = []
        self.number_of_amazons = number_of_amazons
        self.winner = False

    def add_score(self, new_score):
        self.score = self.score + new_score

