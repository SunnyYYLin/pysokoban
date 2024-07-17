import pygame
from game.problem import SokobanAction

_key_actions = {
    pygame.K_UP: SokobanAction.UP,
    pygame.K_DOWN: SokobanAction.DOWN,
    pygame.K_LEFT: SokobanAction.LEFT,
    pygame.K_RIGHT: SokobanAction.RIGHT,
    pygame.K_ESCAPE: SokobanAction.PAUSE
}

class InputHandler:
    """
    Handles user input events.

    Attributes:
        None

    Methods:
        __init__(): Initializes the InputHandler object.
        handle_events(): Handles the events generated by the user.
    """

    def __init__(self):
        """
        Initializes the InputHandler object.
        """
        pass

    def handle_events(self) -> SokobanAction|None:
        """
        Handles the events generated by the user.

        Returns:
            int or None: The key code of the key pressed by the user, or None if no key was pressed.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                try:
                    return _key_actions[event.key]
                except:
                    return None
        return None
