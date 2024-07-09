import pygame
from game.player import Player

class InputHandler:
    def __init__(self, player: Player):
        self.player = player

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                print(event.key)
                return event.key
        return None