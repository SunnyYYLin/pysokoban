import pygame
import logging
from enum import Enum, auto
from typing import Dict

class Event(Enum):
    START = auto()
    RESTART = auto()
    CONTINUE = auto()
    PAUSE = auto()
    EXIT = auto()
    ASK_AI = auto()
    GENERATE = auto()

_key_event = {
    pygame.K_ESCAPE: Event.PAUSE,
    pygame.K_RETURN: Event.START,
    pygame.K_r: Event.RESTART,
    pygame.K_a: Event.ASK_AI,
    pygame.K_BACKSPACE: Event.EXIT
}

class InputHandler:
    def __init__(self, key_actions: dict, key_events: dict = _key_event):
        self.key_actions = key_actions
        self.key_events = key_events
        pass

    def handle_inputs(self, text_rect: Dict[pygame.Surface, pygame.Rect],
                      text_event: Dict[pygame.Surface, Event]):
        while True:
            for event in pygame.event.get():
                # if click on the close button, quit the game
                if event.type == pygame.QUIT:
                    return Event.EXIT
                # if click on any of the text buttons, return the corresponding event
                for text, ev in text_event.items():
                    if event.type == pygame.MOUSEBUTTONDOWN \
                        and text_rect[text].collidepoint(pygame.mouse.get_pos()):
                        logging.info(f"Selected {ev.name}")
                        return ev
                # if key pressed, return the corresponding action
                if event.type == pygame.KEYDOWN:
                    if event.key in self.key_events:
                        logging.info(f"Selected {self.key_events[event.key].name}")
                        return self.key_events[event.key]
                    elif event.key in self.key_actions:
                        logging.info(f"Pressed {self.key_actions[event.key].name}")
                        return self.key_actions[event.key]
                    else:
                        logging.warning(f"Invalid key pressed: {event.key}")
