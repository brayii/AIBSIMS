# core/grid.py
import random
from core.bunny import Bunny

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
            self.add_bunny(bunny, x, y)

    def add_bunny(self, bunny, x, y):
        bunny.x = x
        bunny.y = y
        bunny.grid = self
        self.grid[y][x] = bunny
        self.bunnies.append(bunny)

    def remove_bunny(self, bunny):
        if self.grid[bunny.y][bunny.x] == bunny:
            self.grid[bunny.y][bunny.x] = None
        if bunny in self.bunnies:
            self.bunnies.remove(bunny)

    def move_bunny(self, bunny, new_x, new_y):
        if self.is_in_bounds(new_x, new_y) and self.grid[new_y][new_x] is None:
            self.grid[bunny.y][bunny.x] = None
            self.grid[new_y][new_x] = bunny
            bunny.x, bunny.y = new_x, new_y

    def get_random_empty_tile(self):
        while True:
            x, y = random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1)
            if self.grid[y][x] is None:
                return x, y

    def get_adjacent_empty_tiles(self, x, y):
        dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        return [(x+dx, y+dy) for dx, dy in dirs
                if self.is_in_bounds(x+dx, y+dy) and self.grid[y+dy][x+dx] is None]

    def get_adjacent_bunnies(self, x, y):
        dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        return [(x+dx, y+dy, self.grid[y+dy][x+dx])
                for dx, dy in dirs
                if self.is_in_bounds(x+dx, y+dy) and self.grid[y+dy][x+dx] is not None]

    def is_in_bounds(self, x, y):
        return 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE

    def display(self):
        for y in range(GRID_SIZE):
            row = ''
            for x in range(GRID_SIZE):
                bunny = self.grid[y][x]
                row += bunny.display_char() if bunny else '.'
            print(row)
