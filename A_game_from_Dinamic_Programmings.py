
import random
import os

# Настройки игры
WIDTH = 70
PLATFORM_COUNT = 7

MAX_ENERGY = 100
ENERGY_REGEN = 10

K_HEIGHT = 2.0
K_DISTANCE = 0.5

MAX_HEIGHT_DIFF = 4
MAX_GAP = 12

PLAYER = "P"


class Platform:
    def __init__(self, x, height, width=5):
        self.x = x
        self.height = height
        self.width = width


class Game:
    def __init__(self):
        self.energy = MAX_ENERGY
        self.score = 0

        self.platforms = [
            Platform(i * 9, random.randint(0, 3))
            for i in range(PLATFORM_COUNT)
        ]

        self.platforms[0].height = 3
        self.player_idx = 0

        self.generate_platforms()

    def generate_platforms(self):
        while len(self.platforms) < PLATFORM_COUNT:
            prev = self.platforms[-1]

            gap = random.randint(5, MAX_GAP)
            height = prev.height + random.randint(
                -MAX_HEIGHT_DIFF, MAX_HEIGHT_DIFF
            )

            height = max(0, height)

            self.platforms.append(
                Platform(prev.x + gap, height)
            )

    def jump_cost(self, target_idx):
        current = self.platforms[self.player_idx]
        target = self.platforms[target_idx]

        h0 = current.height

        # Максимальная высота на всём интервале прыжка
        h_max = max(
            p.height
            for p in self.platforms[
                self.player_idx:target_idx + 1
            ]
        )

        distance = target.x - current.x

        vertical_cost = K_HEIGHT * max(0, h_max - h0)
        horizontal_cost = K_DISTANCE * distance

        return vertical_cost + horizontal_cost

    
    def render(self):
        os.system('cls' if os.name == 'nt' else 'clear')

        print("=" * WIDTH)
        print("ENERGY JUMPER")
        print(f"Score: {self.score} | Energy: {self.energy:.1f}/{MAX_ENERGY}")
        print("=" * WIDTH)

        # Координаты относительно текущей платформы
        origin_x = self.platforms[0].x

        # Видимая часть мира
        visible = self.platforms[:]

        # Масштабируем горизонтальные координаты,
        # чтобы все платформы помещались на экране
        max_x = max(p.x - origin_x for p in visible)
        scale = max(1.0, max_x / (WIDTH - 10))

        screen_platforms = []

        for i, p in enumerate(visible):
            sx = int((p.x - origin_x) / scale) + 2

            screen_platforms.append({
              "x": sx,
              "height": p.height,
              "width": max(2, int(p.width / scale)),
              "player": i == self.player_idx
            })

    # Вертикальное масштабирование пока не требуется
        max_h = max(p["height"] for p in screen_platforms)
        min_h = min(p["height"] for p in screen_platforms)

        for h in range(max_h, min_h - 1, -1):
            line = [' '] * WIDTH

            for p in screen_platforms:
                if p["height"] == h:
                    x = p["x"]

                    for dx in range(p["width"]):
                        if 0 <= x + dx < WIDTH:
                            line[x + dx] = '_'

                    if p["player"]:
                        player_x = x + p["width"] // 2

                        if 0 <= player_x < WIDTH:
                            line[player_x] = 'P'

            print(''.join(line))

            print("-" * WIDTH)

        print("Available platforms:")

        for i in range(self.player_idx, len(self.platforms)):
            cost = self.jump_cost(i) if i != self.player_idx else 0
            marker = " (CURRENT)" if i == self.player_idx else ""

            print(
                f"{i - self.player_idx}: "
                f"height={self.platforms[i].height}, "
                f"cost={cost:.1f}{marker}"
            )


    def make_jump(self, relative_idx):
        target_idx = self.player_idx + relative_idx

        if target_idx >= len(self.platforms):
            print("Invalid platform!")
            return False

        if relative_idx == 0:
            print("You are already here!")
            return False

        cost = self.jump_cost(target_idx)

        if cost > self.energy:
            print(f"Not enough energy! Required: {cost:.1f}")
            return False

        current = self.platforms[self.player_idx]
        target = self.platforms[target_idx]

        self.energy -= cost

        # Перемещаем игрока
        self.score += target.x - current.x

        # Удаляем пройденные платформы
        self.platforms = self.platforms[target_idx:]

        self.player_idx = 0

        # Генерируем новые платформы
        self.generate_platforms()

        # Восстанавливаем энергию
        self.energy = min(
            MAX_ENERGY,
            self.energy + ENERGY_REGEN
        )

        return True

    def run(self):
        while True:
            self.render()

            # Проверяем, есть ли вообще достижимые платформы
            available = [
                i for i in range(1, len(self.platforms))
                if self.jump_cost(i) <= self.energy
            ]

            if not available:
                print("\nGAME OVER! No reachable platforms.")
                print(f"Final score: {self.score}")
                break

            try:
                choice = int(input("\nChoose platform (0=current): "))
            except ValueError:
                continue

            if choice < 0 or choice >= len(self.platforms):
                print("Invalid choice!")
                input("Press Enter...")
                continue

            if not self.make_jump(choice):
                input("Press Enter...")


if __name__ == "__main__":
    Game().run()
