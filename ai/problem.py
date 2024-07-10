class SokobanProblem():
    def __init__(self, game):
        self.level = game.level
        self.player = game.player
        
    def initial_state(self):
        self.State = Level