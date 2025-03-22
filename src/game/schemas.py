import pygame
from pydantic import BaseModel
from pygame.event import Event


class PlayerState(BaseModel):
    x_change: float = 0
    y_change: float = 0
    key_right: int = 0
    key_left: int = 0
    key_up: int = 0
    key_down: int = 0
    passed: float = 0
    score: int = 0
    progress: float = 0

    def calculate_delta_x(self):
        if self.x_change != 0 and self.key_right - self.key_left == 0:
            # Settle momentum if no x keys are pressed
            self.x_change = round(
                self.x_change - ((self.x_change / abs(self.x_change)) / 4),
                3,
            )
        else:
            # INCREASE X SPEED
            self.x_change = max(
                min(
                    self.x_change + ((self.key_right - self.key_left) / 2),
                    5,
                ),
                -5,
            )

    def calculate_delta_y(self):
        if self.y_change != 0 and self.key_down - self.key_up == 0:
            # Settle momentum if no y keys are pressed
            self.y_change = round(
                self.y_change - ((self.y_change / abs(self.y_change)) / 10),
                3,
            )
        else:
            # INCREASE Y SPEED
            self.y_change = max(
                min(
                    self.y_change + ((self.key_down - self.key_up) / 2),
                    4,
                ),
                -4,
            )

    def calculate_delta(self):
        self.calculate_delta_x()
        self.calculate_delta_y()


class GameState(BaseModel):
    paused: bool = True
    exit: bool = False
    highscore: int = 0
    difficulty: float = 2
    player: PlayerState = PlayerState()
    opponents: list[int] = list(range(5))

    def process_event(self, event):
        match event:
            # Game State Events
            case (
                Event(type=pygame.QUIT) | Event(type=pygame.KEYUP, key=pygame.K_ESCAPE)
            ):
                self.exit = True
            case Event(type=pygame.KEYUP, key=pygame.K_SPACE):
                self.paused = not self.paused
            case Event(type=pygame.KEYUP, key=pygame.K_UP) if self.paused:
                self.paused = False

            # Player input
            case Event(
                type=pygame.KEYDOWN | pygame.KEYUP as event_type,
                key=pygame.K_LEFT,
            ):
                self.player.key_left = 1 if event_type == pygame.KEYDOWN else 0
            case Event(
                type=pygame.KEYDOWN | pygame.KEYUP as event_type,
                key=pygame.K_RIGHT,
            ):
                self.player.key_right = 1 if event_type == pygame.KEYDOWN else 0
            case Event(
                type=pygame.KEYDOWN | pygame.KEYUP as event_type,
                key=pygame.K_UP,
            ):
                self.player.key_up = 1 if event_type == pygame.KEYDOWN else 0
            case Event(
                type=pygame.KEYDOWN | pygame.KEYUP as event_type,
                key=pygame.K_DOWN,
            ):
                self.player.key_down = 1 if event_type == pygame.KEYDOWN else 0
