#!/usr/bin/python3
import random
import time

import pygame
from pygame.event import Event

import objects
from colour import Colour
from objects import Vector

# Global Declare
DISPLAY_WIDTH = 500
DISPLAY_HEIGHT = 600
DISPLAY = Vector(DISPLAY_WIDTH, DISPLAY_HEIGHT)

# Create Pygame Window
DISPLAY_WINDOW = pygame.display.set_mode(DISPLAY.t())
GAME_CLOCK = pygame.time.Clock()
pygame.init()
pygame.display.set_caption("PyRacing")


def game_loop(game_display):
    game_exit = False
    game_paused = True

    h_lanes = [75, 170, 255, 325, 418]
    v_lanes = [-120, -120, -120, -120, -120]
    lane_speeds = [0, 0, 0, 0, 0]
    score = 0
    x_change = 0
    y_change = 0
    key_right = 0
    key_left = 0
    key_up = 0
    key_down = 0
    passed = 0
    dif = 2
    dif_mod = 0
    score = 0
    highscore = 0
    opponents = list(range(5))

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
        new_opponent.speed = lane_speeds[x]
        new_opponent.hoffset = h_lanes[x] - (new_opponent.box_width / 2)
        new_opponent.voffset = v_lanes[x]
        new_opponent.setpos(Vector(new_opponent.hoffset, new_opponent.voffset))
        new_opponent.name = f"opp{x:d}"

    # GameLoop
    while not game_exit:
        # Read Events
        for event in pygame.event.get():
            match event:
                # Game State Events
                case Event(type=pygame.QUIT):
                    game_exit = True
                case Event(type=pygame.KEYUP, key=pygame.K_SPACE):
                    game_paused = not game_paused
                case Event(type=pygame.KEYUP, key=pygame.K_ESCAPE):
                    game_exit = True

                # Player input
                case Event(
                    type=pygame.KEYDOWN | pygame.KEYUP as event_type,
                    key=pygame.K_LEFT,
                ):
                    key_left = 1 if event_type == pygame.KEYDOWN else 0
                case Event(
                    type=pygame.KEYDOWN | pygame.KEYUP as event_type,
                    key=pygame.K_RIGHT,
                ):
                    key_right = 1 if event_type == pygame.KEYDOWN else 0
                case Event(
                    type=pygame.KEYDOWN | pygame.KEYUP as event_type,
                    key=pygame.K_UP,
                ):
                    key_up = 1 if event_type == pygame.KEYDOWN else 0
                case Event(
                    type=pygame.KEYDOWN | pygame.KEYUP as event_type,
                    key=pygame.K_DOWN,
                ):
                    key_down = 1 if event_type == pygame.KEYDOWN else 0

        # Start running cars
        while len(opponents) > 2:
            chosen = random.choice(opponents)
            opponents.remove(chosen)
            objects.Opponent.collection.members[chosen].speed = (
                random.random() * 2
            ) + 0.5

        # Run Simulation
        if not game_paused:
            # ADJUST MOVE DELTA
            if x_change != 0 and key_right - key_left == 0:
                # DECREASE X SPEED
                x_change = round(x_change - ((x_change / abs(x_change)) / 4), 3)
            else:
                # INCREASE X SPEED
                x_change = max(min(x_change + ((key_right - key_left) / 2), 5), -5)

            if y_change != 0 and key_down - key_up == 0:
                # DECREASE Y SPEED
                y_change = round(y_change - ((y_change / abs(y_change)) / 10), 3)
            else:
                # INCREASE Y SPEED
                y_change = max(min(y_change + ((key_down - key_up) / 2), 4), -4)

            # CHECK POSITION
            car_pos = player.position

            car_new_x = car_pos.x + x_change
            car_new_y = car_pos.y + y_change

            for i, o in enumerate(objects.Opponent.collection.members):
                o.move(Vector(0, (dif + dif_mod) * o.speed))
                if o.position.y > DISPLAY_HEIGHT:
                    o.speed = 0
                    o.setpos(Vector(o.position.x, -o.box_height))
                    opponents.append(i)
                    score += 1
                collided = player.has_collided(o)
                if collided[0]:
                    if collided[1] != 0:
                        x = -1 if o.center.y > player.center.y else 1
                        y_change = ((dif + dif_mod) * o.speed) * x
                    if collided[1] > collided[2]:
                        x = -1 if o.center.x > player.center.x else 1
                        x_change = x * (abs(x_change) + 0.5)

            # CHECK AND CHANGE X POSITION
            if car_new_x > DISPLAY_WIDTH - player.box_width + (
                player.width / 2
            ) or car_new_x < -(player.width / 2):
                x_change = 0

            # CHECK FOR Y CONDITIONS
            if car_new_y > DISPLAY_HEIGHT - player.height:
                # PLAYER HIT BOTTOM OF SCREEN : DISPLAY SCORE AND RESET
                highscore = max(score, highscore)
                message_text = f"Score: {score:d}/{highscore:d}"
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
                x_change = 0
                y_change = 0
                dif_mod = 0
                passed = 0
                time.sleep(2)
                del message
                score = 0
                for opponent in objects.Opponent.collection.members:
                    opponent.setpos(Vector(opponent.hoffset, opponent.voffset))
                game_paused = True
            elif car_new_y <= 0:
                # PLAYER HIT TOP OF SCREEN
                y_change = 1

            # MOVE PLAYER
            player.move(
                Vector(
                    x_change,
                    y_change + ((dif + dif_mod) / 2) + (abs(key_right - key_left) / 2),
                ),
            )

            # MOVE OPPONENTS
            for b in objects.Background.collection.members:
                b.setpos(Vector(0, ((passed * 2.5) % DISPLAY_HEIGHT) - b.offset))

            # INCREMENT PASSED TIME AND INCREASE DIFFICULTY
            passed += dif + dif_mod
            dif_mod = round(min(3.9, dif_mod + 0.002), 3)

        # DRAW TO FRAME
        objects.Sprite.All.draw(game_display)

        # UPDATE DISPLAY
        pygame.display.update()
        GAME_CLOCK.tick(60)


# START GAME LOOP
game_loop(DISPLAY_WINDOW)
pygame.quit()
