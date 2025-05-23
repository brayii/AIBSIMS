# grid.py
from core.bunny import Bunny
import random

GRID_SIZE = 80

class Grid:
    def __init__(self):
        self.grid = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.bunnies = []
        self.spawn_initial_bunnies()

    def spawn_initial_bunnies(self, count=5):
        for _ in range(count):
            x, y = self.get_random_empty_tile()
            sex = random.choice(['M', 'F'])
            name = f"Bunny{len(self.bunnies)}"
            mutant = random.random() < 0.02
            bunny = Bunny(name, sex, x, y, mutant)
            self.grid[y][x] = bunny
            self.bunnies.append(bunny)

    def get_random_empty_tile(self):
        while True:
            x, y = random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1)
            if self.grid[y][x] is None:
                return x, y

    def display(self):
        for y in range(GRID_SIZE):
            row = ''
            for x in range(GRID_SIZE):
                bunny = self.grid[y][x]
                row += bunny.display_char() if bunny else '.'
            print(row)

