# core/grid.py

import pygame
from core.bunny import Bunny

TILE_SIZE = 32
GRID_WIDTH = 20
GRID_HEIGHT = 15
SCREEN_WIDTH = TILE_SIZE * GRID_WIDTH
SCREEN_HEIGHT = TILE_SIZE * GRID_HEIGHT

BG_COLOR = (30, 30, 30)
GRID_COLOR = (60, 60, 60)

class Grid:
    def __init__(self, screen):
        self.screen = screen
        self.bunnies = []
        self.cells = [[None for _ in range(GRID_HEIGHT)] for _ in range(GRID_WIDTH)]
        self.spawn_initial_bunnies()

    def spawn_initial_bunnies(self):
        # Example: place 5 random bunnies
        import random
        for i in range(5):
            x, y = random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1)
            bunny = Bunny(name=f"B{i}", sex=random.choice(['M', 'F']), x=x, y=y)
            self.place_bunny(bunny, x, y)

    def place_bunny(self, bunny, x, y):
        bunny.x, bunny.y = x, y
        self.bunnies.append(bunny)
        self.cells[x][y] = bunny

    def move_bunny(self, bunny, new_x, new_y):
        self.cells[bunny.x][bunny.y] = None
        bunny.x, bunny.y = new_x, new_y
        self.cells[new_x][new_y] = bunny

    def remove_bunny(self, bunny):
        self.cells[bunny.x][bunny.y] = None
        if bunny in self.bunnies:
            self.bunnies.remove(bunny)

    def get_adjacent_empty_tiles(self, x, y):
        candidates = [
            (x+dx, y+dy)
            for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]
            if 0 <= x+dx < GRID_WIDTH and 0 <= y+dy < GRID_HEIGHT
        ]
        return [(cx, cy) for cx, cy in candidates if self.cells[cx][cy] is None]

    def draw_grid(self):
        for x in range(0, SCREEN_WIDTH, TILE_SIZE):
            pygame.draw.line(self.screen, GRID_COLOR, (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, TILE_SIZE):
            pygame.draw.line(self.screen, GRID_COLOR, (0, y), (SCREEN_WIDTH, y))

    def draw_entities(self):
        for bunny in self.bunnies:
            px = bunny.x * TILE_SIZE
            py = bunny.y * TILE_SIZE
            bunny.draw(self.screen, px, py)

    def update(self):
        self.screen.fill(BG_COLOR)
        self.draw_grid()
        self.draw_entities()
        pygame.display.flip()
