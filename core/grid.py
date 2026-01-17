# core/grid.py

import pygame
import random
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
        self.cells = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

    def is_empty(self, x, y):
        # STANDARDIZED
        return self.in_bounds(x, y) and self.cells[y][x] is None


    def get_adjacent_offsets(self):
        return [(0, -1), (0, 1), (-1, 0), (1, 0)]

    def in_bounds(self, x, y):
        return 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT


    def get_adjacent_empty_tiles(self, x, y):
        empty = []
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if self.is_empty(nx, ny):
                empty.append((nx, ny))
        return empty



    def draw_grid(self):
        for x in range(0, SCREEN_WIDTH, TILE_SIZE):
            pygame.draw.line(self.screen, GRID_COLOR, (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, TILE_SIZE):
            pygame.draw.line(self.screen, GRID_COLOR, (0, y), (SCREEN_WIDTH, y))


    def update(self):
        self.screen.fill(BG_COLOR)

        self.draw_grid()
      
        pygame.display.flip()

