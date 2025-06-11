# bunny.py
import random
import pygame

COLORS = ["white", "brown", "black", "spotted"]
TILE_SIZE = 32  # Match this with the grid tile size

COLOR_MAP = {
    "white": (255, 255, 255),
    "brown": (139, 69, 19),
    "black": (30, 30, 30),
    "spotted": (180, 180, 180)
}

def get_bunny_color(bunny):
    base_color = COLOR_MAP.get(bunny.color, (200, 200, 200))
    if bunny.is_mutant:
        return (128, 0, 128)  # Vampire bunny: purple
    elif bunny.sex == 'M':
        return (0, 128, 255) if bunny.is_adult() else (100, 100, 255)
    else:
        return (255, 105, 180) if bunny.is_adult() else (255, 182, 193)

def draw_bunny_icon(screen, x, y, color):
    pygame.draw.rect(screen, color, (x + 6, y + 6, TILE_SIZE - 12, TILE_SIZE - 12))

class Bunny:
    def __init__(self, name, sex, x, y, mutant=False, age=0):
        self.name = name
        self.sex = sex  # 'M' or 'F'
        self.color = random.choice(COLORS)
        self.age = age
        self.is_mutant = mutant
        self.x = x
        self.y = y
        self.use_rl = False
        self.grid = None

    def is_adult(self):
        return self.age >= 2

    def max_age(self):
        return 50 if self.is_mutant else 10

    def display_char(self):
        if self.is_mutant:
            return 'X'
        return ('M' if self.is_adult() else 'm') if self.sex == 'M' else ('F' if self.is_adult() else 'f')

    def update(self, grid, turn, logger=None):
        self.age += 1
        if self.age > self.max_age():
            if logger:
                logger.log(turn, "death", self, "natural causes", controller="FSM")
            grid.remove_bunny(self)
            return

        if not self.is_mutant and not self.is_adult() and random.random() < 0.02:
            self.is_mutant = True
            if logger:
                logger.log(turn, "mutation", self, "juvenile mutation", controller="FSM")

        self.move_random(grid)

    def move_random(self, grid):
        options = grid.get_adjacent_empty_tiles(self.x, self.y)
        if options:
            nx, ny = random.choice(options)
            grid.move_bunny(self, nx, ny)

    def draw(self, surface, x, y):
        color = get_bunny_color(self)
        draw_bunny_icon(surface, x, y, color)

