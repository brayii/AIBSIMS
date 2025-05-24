# bunny.py
import random

COLORS = ["white", "brown", "black", "spotted"]

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
