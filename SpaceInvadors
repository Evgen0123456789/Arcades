
import os
import sys
import time
import random
import threading
import queue

import numpy as np


# =========================
# Configuration
# =========================

WIDTH = 40
HEIGHT = 20
FPS = 10

PLAYER_Y = HEIGHT - 2

ALIEN_POINTS = np.array([0, 10, 20, 30])


# =========================
# Game state
# =========================

class Game:

    def __init__(self):

        # Independent game layers
        self.aliens = np.zeros((HEIGHT, WIDTH), dtype=np.int8)

        self.player_bullets = np.zeros(
            (HEIGHT, WIDTH), dtype=np.int8
        )

        self.enemy_bullets = np.zeros(
            (HEIGHT, WIDTH), dtype=np.int8
        )

        # Player
        self.player_x = WIDTH // 2
        self.lives = 3

        # Statistics
        self.score = 0
        self.next_extra_life = 100

        # Alien movement
        self.alien_direction = 1
        self.tick = 0

        self.running = True
        self.won = False

        self.spawn_aliens()

    # =========================
    # Initialization
    # =========================

    def spawn_aliens(self):

        for y in range(3):

            for x in range(5, WIDTH - 5, 4):

                # Different alien classes
                self.aliens[y * 2 + 1, x] = 3 - y

    # =========================
    # Player
    # =========================

    def move_player(self, direction):

        self.player_x += direction

        self.player_x = np.clip(
            self.player_x, 0, WIDTH - 1
        )

    def shoot(self):

        y = PLAYER_Y - 1

        if self.player_bullets[y, self.player_x] == 0:

            self.player_bullets[y, self.player_x] = 1

    # =========================
    # Bullet movement
    # =========================

    def move_bullets(self):

        # Player bullets move upwards
        self.player_bullets[:-1, :] = (
            self.player_bullets[1:, :]
        )

        self.player_bullets[-1, :] = 0

        # Enemy bullets move downwards
        self.enemy_bullets[1:, :] = (
            self.enemy_bullets[:-1, :]
        )

        self.enemy_bullets[0, :] = 0

    # =========================
    # Collision detection
    # =========================

    def check_collisions(self):

        # Player bullets vs aliens
        hits = (
            (self.player_bullets > 0) &
            (self.aliens > 0)
        )

        if np.any(hits):

            self.score += int(
                ALIEN_POINTS[self.aliens[hits]].sum()
            )

            self.aliens[hits] = 0
            self.player_bullets[hits] = 0

        # Enemy bullets vs player
        if self.enemy_bullets[PLAYER_Y, self.player_x]:

            self.enemy_bullets[PLAYER_Y, self.player_x] = 0

            self.lose_life()

        # Extra lives
        while self.score >= self.next_extra_life:

            self.lives += 1
            self.next_extra_life += 100

        # Check victory
        if not np.any(self.aliens):

            self.won = True
            self.running = False

    # =========================
    # Alien movement
    # =========================

    def move_aliens(self):

        xs = np.where(self.aliens > 0)[1]

        if len(xs) == 0:
            return

        direction = self.alien_direction

        left = xs.min()
        right = xs.max()

        # Check horizontal boundaries
        if (
            left + direction < 0 or
            right + direction >= WIDTH
        ):

            # Move down
            self.aliens[1:, :] = self.aliens[:-1, :]
            self.aliens[0, :] = 0

            self.alien_direction *= -1

            # Aliens have reached the player
            if np.any(self.aliens[PLAYER_Y:, :] > 0):

                self.aliens[PLAYER_Y:, :] = 0
                self.lose_life()

        else:

            # Move horizontally
            if direction > 0:

                self.aliens[:, 1:] = self.aliens[:, :-1]
                self.aliens[:, 0] = 0

            else:

                self.aliens[:, :-1] = self.aliens[:, 1:]
                self.aliens[:, -1] = 0

    # =========================
    # Enemy shooting
    # =========================

    def enemy_shoot(self):

        if random.random() > 0.06:
            return

        columns = np.where(
            np.any(self.aliens > 0, axis=0)
        )[0]

        if len(columns) == 0:
            return

        x = random.choice(columns)

        # Find the lowest alien in this column
        y = np.where(self.aliens[:, x] > 0)[0].max()

        if y + 1 < HEIGHT:

            self.enemy_bullets[y + 1, x] = 1

    # =========================
    # Life management
    # =========================

    def lose_life(self):

        self.lives -= 1

        if self.lives <= 0:

            self.lives = 0
            self.running = False

    # =========================
    # Game update
    # =========================

    def update(self):

        self.tick += 1

        self.move_bullets()

        self.check_collisions()

        if not self.running:
            return

        # Aliens move periodically
        move_period = max(2, 6 - self.score // 150)

        if self.tick % move_period == 0:

            self.move_aliens()

        if not self.running:
            return

        self.enemy_shoot()

        self.check_collisions()

    # =========================
    # Rendering
    # =========================

    def render(self):

        screen = np.full(
            (HEIGHT, WIDTH), ' ', dtype='<U1'
        )

        # Aliens
        screen[self.aliens == 1] = 'w'
        screen[self.aliens == 2] = 'W'
        screen[self.aliens == 3] = 'M'

        # Bullets
        screen[self.player_bullets > 0] = '|'
        screen[self.enemy_bullets > 0] = '!'

        # Player
        screen[PLAYER_Y, self.player_x] = 'A'

        # Draw screen
        output = [
            '+' + '-' * WIDTH + '+'
        ]

        for row in screen:

            output.append(
                '|' + ''.join(row) + '|'
            )

        output.append(
            '+' + '-' * WIDTH + '+'
        )

        output.append(
            f" SCORE: {self.score}    LIVES: {self.lives}"
        )

        sys.stdout.write('\033[H')
        sys.stdout.write('\n'.join(output))
        sys.stdout.flush()


# =========================
# Keyboard input
# =========================

def start_keyboard_reader():

    keys = queue.Queue()
    stop = threading.Event()

    if os.name == 'nt':

        import msvcrt

        def reader():

            while not stop.is_set():

                if msvcrt.kbhit():

                    key = msvcrt.getch()

                    if key in (b'\x00', b'\xe0'):
                        msvcrt.getch()
                        continue

                    keys.put(key.decode(
                        errors='ignore'
                    ).lower())

                else:

                    time.sleep(0.01)

        restore = lambda: None

    else:

        import termios
        import tty

        fd = sys.stdin.fileno()

        old_settings = termios.tcgetattr(fd)

        tty.setcbreak(fd)

        def reader():

            while not stop.is_set():

                key = sys.stdin.read(1)

                if key:
                    keys.put(key.lower())

        def restore():

            termios.tcsetattr(
                fd,
                termios.TCSADRAIN,
                old_settings
            )

    thread = threading.Thread(
        target=reader,
        daemon=True
    )

    thread.start()

    return keys, stop, restore


# =========================
# Main loop
# =========================

def main():

    game = Game()

    keys, stop, restore = start_keyboard_reader()

    sys.stdout.write('\033[?25l\033[2J')
    sys.stdout.flush()

    try:

        while game.running:

            # Process keyboard events
            while not keys.empty():

                key = keys.get_nowait()

                if key == 'a':
                    game.move_player(-1)

                elif key == 'd':
                    game.move_player(1)

                elif key == ' ':
                    game.shoot()

                elif key == 'q':
                    game.running = False

            # Update game state
            game.update()

            # Draw frame
            game.render()

            time.sleep(1 / FPS)

    except KeyboardInterrupt:

        pass

    finally:

        stop.set()
        restore()

        sys.stdout.write('\033[?25h')
        sys.stdout.write('\n')

    if game.won:

        print("YOU WIN!")

    elif game.lives == 0:

        print("GAME OVER!")

    else:

        print("GAME STOPPED")

    print(f"Final score: {game.score}")


if __name__ == '__main__':

    main()
