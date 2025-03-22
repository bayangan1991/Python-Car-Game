import random
import time

import pygame

from .colour import Colour
from .constants import DISPLAY, DISPLAY_HEIGHT, DISPLAY_WIDTH, H_LANES, V_LANES
from .objects import Background, Car, Opponent, Sprite, TextObject, Vector
from .schemas import GameState, PlayerState


def game_loop(game_display):
    game_clock = pygame.time.Clock()
    state = GameState()
    # Load background
    for direction in range(2):
        bg = Background(
            "assets/fullroad.png",
            Vector(500, 600),
            Vector(500, 600),
        )
        bg.offset = 600 * direction

    # Load Player Car
    player = Car("red", Vector(120, 120), Vector(64, 100))
    player.name = "player"

    # Set Stating position
    start_pos = (DISPLAY / 2) - (player.box / 2)
    player.position = start_pos

    # Load Opponents
    for direction in range(len(state.opponents)):
        new_opponent = Opponent(
            Vector(120, 120),
            Vector(64, 100),
        )
        new_opponent.speed = 0
        new_opponent.hoffset = H_LANES[direction] - (new_opponent.box_width / 2)
        new_opponent.voffset = V_LANES[direction]
        new_opponent.setpos(Vector(new_opponent.hoffset, new_opponent.voffset))
        new_opponent.name = f"opp{direction:d}"
        new_opponent.draw_random()

    # OnScreen Objects
    score_text = TextObject(
        font="freesansbold.ttf",
        fontsize=20,
        colour=Colour.Red,
        pos=Vector(40, DISPLAY.y - 50),
        align="midleft",
    )
    time_text = TextObject(
        font="freesansbold.ttf",
        fontsize=20,
        colour=Colour.Red,
        pos=Vector(40, DISPLAY.y - 20),
        align="midleft",
    )
    high_score_text = TextObject(
        font="freesansbold.ttf",
        fontsize=20,
        colour=Colour.Red,
        pos=Vector(DISPLAY.x - 40, DISPLAY.y - 50),
        align="midright",
    )
    high_time_text = TextObject(
        font="freesansbold.ttf",
        fontsize=20,
        colour=Colour.Red,
        pos=Vector(DISPLAY.x - 40, DISPLAY.y - 20),
        align="midright",
    )

    timer = None
    # GameLoop
    while not state.exit:
        # Read events and update game state
        for event in pygame.event.get():
            state.process_event(event)

        # Choose a random car in the queue
        # and give it a down speed
        while len(state.opponents) > 2:
            chosen = random.choice(state.opponents)
            state.opponents.remove(chosen)
            Opponent.collection.members[chosen].speed = (random.random() * 2) + 0.4

        # Run Simulation
        if not state.paused:
            timer = time.monotonic_ns()
            state.player.calculate_delta()

            # CHECK POSITION
            car_pos = player.position
            car_new_x = car_pos.x + state.player.x_change
            car_new_y = car_pos.y + state.player.y_change

            for i, opponent in enumerate(Opponent.collection.members):
                # Update opponent position
                opponent.move(
                    Vector(
                        0,
                        (state.difficulty + state.player.progress) * opponent.speed,
                    ),
                )

                # Check if opponent left the screen
                if opponent.position.y > DISPLAY_HEIGHT:
                    opponent.speed = 0
                    opponent.setpos(Vector(opponent.position.x, -opponent.box_height))
                    state.opponents.append(i)
                    state.player.score += 1
                    opponent.draw_random()

                # Check if the player has collided with an opponent
                # and bounce based on current speed and difficulty
                collided, collide_x, collide_y = player.has_collided(opponent)
                if collided:
                    if collide_x != 0:
                        direction = -1 if opponent.center.y > player.center.y else 1
                        state.player.y_change = (
                            (state.difficulty + state.player.progress) * opponent.speed
                        ) * direction
                    if collide_x > collide_y:
                        direction = -1 if opponent.center.x > player.center.x else 1
                        state.player.x_change = direction * abs(
                            state.player.x_change * 0.75
                        )

            # CHECK AND CHANGE X POSITION
            # and clamp to screen width
            if car_new_x > DISPLAY_WIDTH - player.box_width + (
                player.width / 2
            ) or car_new_x < -(player.width / 2):
                state.player.x_change = 0

            # CHECK FOR Y CONDITIONS
            # and clamp to screen height
            if car_new_y > DISPLAY_HEIGHT - player.height:
                # PLAYER HIT BOTTOM OF SCREEN : DISPLAY SCORE AND RESET
                state.high_score = max(state.player.score, state.high_score)
                state.high_time = max(state.player.time, state.high_time)

                pygame.display.update()
                player.set_angle(0)
                player.setpos(start_pos)
                for opponent in Opponent.collection.members:
                    opponent.setpos(Vector(opponent.hoffset, opponent.voffset))
                pygame.time.wait(1000)
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
                    + ((state.difficulty + state.player.progress) / 2)
                    + (abs(state.player.key_right - state.player.key_left) / 2),
                ),
            )

            # MOVE OPPONENTS
            for b in Background.collection.members:
                b.setpos(
                    Vector(
                        0,
                        ((state.player.passed * 2.5) % DISPLAY_HEIGHT) - b.offset,
                    ),
                )

            # INCREMENT PASSED TIME AND INCREASE DIFFICULTY
            state.player.passed += state.difficulty + state.player.progress
            state.player.progress = round(
                min(3.9, state.player.score * 0.08),
                3,
            )
        # DRAW TO FRAME
        Sprite.All.draw(game_display)

        # Draw Text to the screen
        score_text.text = f"Score | {state.player.score:d}"
        score_text.draw(game_display)

        total_seconds, remainder = divmod(state.player.time, 1_000_000_000)
        minutes, seconds = divmod(total_seconds, 60)
        milliseconds = remainder // 10_000_000
        time_text.text = f"Time | {minutes:02d}:{seconds:02d}:{milliseconds:02d}"
        time_text.draw(game_display)

        if state.high_score:
            high_score_text.text = f" {state.high_score:d} | High"
            high_score_text.draw(game_display)

        if state.high_time:
            total_seconds, remainder = divmod(state.high_time, 1_000_000_000)
            minutes, seconds = divmod(total_seconds, 60)
            milliseconds = remainder // 10_000_000
            high_time_text.text = (
                f" {minutes:02d}:{seconds:02d}:{milliseconds:02d} | Best"
            )
            high_time_text.draw(game_display)

        # UPDATE DISPLAY
        pygame.display.update()
        game_clock.tick(60)

        if not state.paused and timer:
            state.player.time += time.monotonic_ns() - timer


def run_game():
    display_window = pygame.display.set_mode(DISPLAY.origin())
    pygame.init()
    pygame.display.set_caption("PyRacing")

    # START GAME LOOP
    game_loop(display_window)
    pygame.quit()
