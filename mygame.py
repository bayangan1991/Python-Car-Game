#!/usr/bin/python3
import random

import pygame
from pydantic import BaseModel
from pygame.event import Event

import objects
from colour import Colour
from objects import Vector

# Global Declare
DISPLAY_WIDTH = 500
DISPLAY_HEIGHT = 600
H_LANES = (75, 170, 255, 325, 418)
V_LANES = (-120, -120, -120, -120, -120)
DISPLAY = Vector(DISPLAY_WIDTH, DISPLAY_HEIGHT)

# Create Pygame Window
DISPLAY_WINDOW = pygame.display.set_mode(DISPLAY.origin())
GAME_CLOCK = pygame.time.Clock()
pygame.init()
pygame.display.set_caption("PyRacing")


class PlayerState(BaseModel):
    x_change: float = 0
    y_change: float = 0
    key_right: int = 0
    key_left: int = 0
    key_up: int = 0
    key_down: int = 0
    passed: float = 0
    score: int = 0
    dif: float = 2
    dif_mod: float = 0


class GameState(BaseModel):
    paused: bool = True
    exit: bool = False
    highscore: int = 0
    player: PlayerState = PlayerState()
    opponents: list[int] = list(range(5))


def game_loop(game_display):
    state = GameState()

    # Load background
    for x in range(2):
        bg = objects.Background(
            "assets/fullroad.png",
            Vector(500, 600),
            Vector(500, 600),
        )
        bg.offset = 600 * x

    # Load Player Car
    player = objects.Car("assets/racecar1.png", Vector(120, 120), Vector(64, 100))
    player.name = "player"

    # Set Stating position
    start_pos = (DISPLAY / 2) - (player.box / 2)
    player.position = start_pos

    # Load Opponents
    for x in range(5):
        new_opponent = objects.Opponent(
            "assets/racecar2.png",
            Vector(120, 120),
            Vector(64, 100),
        )
        new_opponent.speed = 0
        new_opponent.hoffset = H_LANES[x] - (new_opponent.box_width / 2)
        new_opponent.voffset = V_LANES[x]
        new_opponent.setpos(Vector(new_opponent.hoffset, new_opponent.voffset))
        new_opponent.name = f"opp{x:d}"

    # GameLoop
    while not state.exit:
        # Read Events
        for event in pygame.event.get():
            match event:
                # Game State Events
                case (
                    Event(type=pygame.QUIT)
                    | Event(type=pygame.KEYUP, key=pygame.K_ESCAPE)
                ):
                    state.exit = True
                case Event(type=pygame.KEYUP, key=pygame.K_SPACE):
                    state.paused = not state.paused

                # Player input
                case Event(
                    type=pygame.KEYDOWN | pygame.KEYUP as event_type,
                    key=pygame.K_LEFT,
                ):
                    state.player.key_left = 1 if event_type == pygame.KEYDOWN else 0
                case Event(
                    type=pygame.KEYDOWN | pygame.KEYUP as event_type,
                    key=pygame.K_RIGHT,
                ):
                    state.player.key_right = 1 if event_type == pygame.KEYDOWN else 0
                case Event(
                    type=pygame.KEYDOWN | pygame.KEYUP as event_type,
                    key=pygame.K_UP,
                ):
                    state.player.key_up = 1 if event_type == pygame.KEYDOWN else 0
                case Event(
                    type=pygame.KEYDOWN | pygame.KEYUP as event_type,
                    key=pygame.K_DOWN,
                ):
                    state.player.key_down = 1 if event_type == pygame.KEYDOWN else 0

        # Start running cars
        while len(state.opponents) > 2:
            chosen = random.choice(state.opponents)
            state.opponents.remove(chosen)
            objects.Opponent.collection.members[chosen].speed = (
                random.random() * 2
            ) + 0.5

        # Run Simulation
        if not state.paused:
            # ADJUST MOVE DELTA
            if (
                state.player.x_change != 0
                and state.player.key_right - state.player.key_left == 0
            ):
                # DECREASE X SPEED
                state.player.x_change = round(
                    state.player.x_change
                    - ((state.player.x_change / abs(state.player.x_change)) / 4),
                    3,
                )
            else:
                # INCREASE X SPEED
                state.player.x_change = max(
                    min(
                        state.player.x_change
                        + ((state.player.key_right - state.player.key_left) / 2),
                        5,
                    ),
                    -5,
                )

            if (
                state.player.y_change != 0
                and state.player.key_down - state.player.key_up == 0
            ):
                # DECREASE Y SPEED
                state.player.y_change = round(
                    state.player.y_change
                    - ((state.player.y_change / abs(state.player.y_change)) / 10),
                    3,
                )
            else:
                # INCREASE Y SPEED
                state.player.y_change = max(
                    min(
                        state.player.y_change
                        + ((state.player.key_down - state.player.key_up) / 2),
                        4,
                    ),
                    -4,
                )

            # CHECK POSITION
            car_pos = player.position

            car_new_x = car_pos.x + state.player.x_change
            car_new_y = car_pos.y + state.player.y_change

            for i, o in enumerate(objects.Opponent.collection.members):
                o.move(Vector(0, (state.player.dif + state.player.dif_mod) * o.speed))
                if o.position.y > DISPLAY_HEIGHT:
                    o.speed = 0
                    o.setpos(Vector(o.position.x, -o.box_height))
                    state.opponents.append(i)
                    state.player.score += 1
                collided = player.has_collided(o)
                if collided[0]:
                    if collided[1] != 0:
                        x = -1 if o.center.y > player.center.y else 1
                        state.player.y_change = (
                            (state.player.dif + state.player.dif_mod) * o.speed
                        ) * x
                    if collided[1] > collided[2]:
                        x = -1 if o.center.x > player.center.x else 1
                        state.player.x_change = x * (abs(state.player.x_change) + 0.5)

            # CHECK AND CHANGE X POSITION
            if car_new_x > DISPLAY_WIDTH - player.box_width + (
                player.width / 2
            ) or car_new_x < -(player.width / 2):
                state.player.x_change = 0

            # CHECK FOR Y CONDITIONS
            if car_new_y > DISPLAY_HEIGHT - player.height:
                # PLAYER HIT BOTTOM OF SCREEN : DISPLAY SCORE AND RESET
                state.highscore = max(state.player.score, state.highscore)
                message_text = f"Score: {state.player.score:d}/{state.highscore:d}"
                message = objects.TextObject(
                    message_text,
                    "freesansbold.ttf",
                    40,
                    Colour.Red,
                    DISPLAY / 2,
                )
                message.drawcenter = True
                message.draw(game_display)
                pygame.display.update()
                player.set_angle(0)
                player.setpos(start_pos)
                pygame.time.wait(2000)
                del message
                for opponent in objects.Opponent.collection.members:
                    opponent.setpos(Vector(opponent.hoffset, opponent.voffset))
                state.paused = True
                state.player = PlayerState()
                pygame.event.clear()
            elif car_new_y <= 0:
                # PLAYER HIT TOP OF SCREEN
                state.player.y_change = 1

            # MOVE PLAYER
            player.move(
                Vector(
                    state.player.x_change,
                    state.player.y_change
                    + ((state.player.dif + state.player.dif_mod) / 2)
                    + (abs(state.player.key_right - state.player.key_left) / 2),
                ),
            )

            # MOVE OPPONENTS
            for b in objects.Background.collection.members:
                b.setpos(
                    Vector(
                        0,
                        ((state.player.passed * 2.5) % DISPLAY_HEIGHT) - b.offset,
                    ),
                )

            # INCREMENT PASSED TIME AND INCREASE DIFFICULTY
            state.player.passed += state.player.dif + state.player.dif_mod
            state.player.dif_mod = round(
                min(3.9, state.player.dif_mod + 0.002),
                3,
            )

        # DRAW TO FRAME
        objects.Sprite.All.draw(game_display)

        # UPDATE DISPLAY
        pygame.display.update()
        GAME_CLOCK.tick(60)


# START GAME LOOP
game_loop(DISPLAY_WINDOW)
pygame.quit()
