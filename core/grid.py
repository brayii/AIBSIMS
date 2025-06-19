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
        self.bunnies = []
        self.cells = [[None for _ in range(GRID_HEIGHT)] for _ in range(GRID_WIDTH)]
        self.spawn_initial_bunnies()
        self.female_heatmap = FemaleHeatmap(self.GRID_WIDTH, self.GRID_HEIGHT)


    def get_bunny_at(self, x, y):
        """Safe access: return the bunny at (x, y) or None if out-of-bounds or empty."""
        if not self.in_bounds(x, y):
            return None
        try:
            return self.cells[y][x]  # [row][col]
        except IndexError:
            return None

    def nearest_vampire_distance(self, x, y):
        """Return the Manhattan distance to the nearest vampire from (x, y), or None if none found."""
        min_dist = None
        for bx in range(self.GRID_WIDTH):
            for by in range(self.GRID_HEIGHT):
                bunny = self.cells[bx][by]
                if bunny is not None and getattr(bunny, "is_mutant", False):
                    dist = abs(bx - x) + abs(by - y)
                    if min_dist is None or dist < min_dist:
                        min_dist = dist
        return min_dist

    def get_adjacent_offsets(self):
        return [
            (0, -1),
            (0, 1),
            (-1, 0),
            (1, 0),
        ]
    
    def in_bounds(self, x, y):
        """Return True if (x, y) is within the grid bounds."""
        return 0 <= x < self.GRID_WIDTH and 0 <= y < self.GRID_HEIGHT


    def spawn_initial_bunnies(self):
        # Spawn two female-male pairs near each other        
        pairs = [("F", "M"), ("F", "M")]
        for i, (s1, s2) in enumerate(pairs):
            x, y = random.randint(0, self.GRID_WIDTH - 2), random.randint(0, self.GRID_HEIGHT - 2)
            b1 = Bunny(name=f"B{i*2}", sex=s1, x=x, y=y, age=3)
            b2 = Bunny(name=f"B{i*2+1}", sex=s2, x=x+1, y=y, age=3)
            self.place_bunny(b1, x, y)
            self.place_bunny(b2, x+1, y=y)


        # Optional: Add 1 juvenile for mutation testing
        jx, jy = random.randint(0, self.GRID_WIDTH - 1), random.randint(0, self.GRID_HEIGHT - 1)
        if self.cells[jx][jy] is None:
            juvenile = Bunny(name="J100", sex=random.choice(['M', 'F']), x=jx, y=jy, age=0)
            self.place_bunny(juvenile, jx, jy)


    def place_bunny(self, bunny, x, y):
        bunny.x, bunny.y = x, y
        self.bunnies.append(bunny)
        self.cells[x][y] = bunny

    def move_bunny(self, bunny, new_x, new_y):
        self.cells[bunny.x][bunny.y] = None
        bunny.x, bunny.y = new_x, new_y
        self.cells[new_x][new_y] = bunny

    def add_bunny(self, bunny):
        if self.in_bounds(bunny.x, bunny.y) and self.cells[bunny.x][bunny.y] is None:
            self.cells[bunny.x][bunny.y] = bunny
            self.bunnies.append(bunny)

    def remove_bunny(self, bunny):
        if self.cells[bunny.x][bunny.y] == bunny:
            self.cells[bunny.x][bunny.y] = None
        if bunny in self.bunnies:
            self.bunnies.remove(bunny)

    def get_adjacent_empty_tiles(self, x, y):
        directions = [(-1,0), (1,0), (0,-1), (0,1)]
        return [
            (nx, ny)
            for dx, dy in directions
            if 0 <= (nx := x + dx) < GRID_WIDTH and 0 <= (ny := y + dy) < GRID_HEIGHT
            and self.cells[nx][ny] is None
        ]

    def find_adjacent_entities(self, x, y):
        adjacent = []
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT:
                entity = self.cells[nx][ny]
                if entity:
                    adjacent.append(entity)
        return adjacent
    def get_adjacent_bunnies(self, x, y):
        """Return a list of bunnies adjacent (N, S, E, W) to (x, y)."""
        neighbors = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT:
                bunny = self.cells[nx][ny]
                if bunny is not None:
                    neighbors.append(bunny)
        return neighbors
    
    def move_toward(self, bunny, tx, ty):
        dx = 1 if tx > bunny.x else -1 if tx < bunny.x else 0
        dy = 1 if ty > bunny.y else -1 if ty < bunny.y else 0
        options = [(bunny.x + dx, bunny.y), (bunny.x, bunny.y + dy)]
        for nx, ny in options:
            if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT and self.cells[nx][ny] is None:
                self.move_bunny(bunny, nx, ny)
                return
        bunny.move_random(self)  # fallback

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
    
    def get_all_bunnies(self):
        return list(self.bunnies)


    @property
    def GRID_WIDTH(self):
        return GRID_WIDTH

    @property
    def GRID_HEIGHT(self):
        return GRID_HEIGHT
    
    @property
    def TILE_SIZE(self):
        return TILE_SIZE

# --- Female Heatmap for Mating Strategy ---

class FemaleHeatmap:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.data = [[0.0 for _ in range(height)] for _ in range(width)]

    def decay(self):
        for x in range(self.width):
            for y in range(self.height):
                self.data[x][y] *= 0.95

    def update_from_sightings(self, bunnies):
        for b in bunnies:
            if b.sex == 'F' and b.is_adult() and not b.is_mutant:
                self.data[b.x][b.y] += 1.0

    def best_tile(self):
        flat = [((x, y), self.data[x][y]) for x in range(self.width) for y in range(self.height)]
        return max(flat, key=lambda kv: kv[1])[0]


    def best_tile_value(self):
        x, y = self.best_tile()
        return self.data[x][y]
