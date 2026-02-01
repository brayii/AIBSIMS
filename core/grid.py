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
        self.bunnies = []
        
        # Initialize with some bunnies
        # colors = [
        #     (139, 69, 19), # brown
        #     (255, 255, 255), # white
        #     (192, 192, 192) # gray
        #  ]

        # self.bunnies.append(Bunny(sex="M", x=10, y=10))
        # self.cells[10][10] = self.bunnies[-1]   
        # self.bunnies.append(Bunny(sex="F", x=11, y=10))
        # self.cells[10][11] = self.bunnies[-1]

        # pairs = [("F", "M"), ("F", "M")]
        # for i, (s1, s2) in enumerate(pairs):
        #     x, y = random.randint(0, GRID_WIDTH - 2), random.randint(0, GRID_HEIGHT - 2)
        #     # b1 = Bunny(sex=s1, x=x, y=y)
        #     # b2 = Bunny(sex=s2, x=x+1, y=y)
        #     c1, c2 = random.sample(colors, 2) # always two different colors
        #     self.place_bunny(Bunny(sex=s1, x=x, y=y, color=c1), x, y)
        #     self.place_bunny(Bunny(sex=s2, x=x+1, y=y, color=c2), x+1, y)
        # 
        # if self.is_empty(x+1, y+1): 
        #     self.place_bunny(Bunny(sex=random.choice(['M', 'F']), x=x+1, y=y+1), x+1, y+1)
        # else:
        #     pass            
           

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
    
    def get_adjacent_bunnies(self, x, y):
        # print adjacent positions for debugging
        adjacent = []
        adjacent_bunnies = []
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if self.in_bounds(nx, ny):
                adjacent.append((nx, ny))
                #print(f"Adjacent position: ({nx},{ny})")
        for bunny in self.bunnies:
            if (bunny.x, bunny.y) in adjacent:
                #print(f"Found adjacent bunny at ({bunny.x},{bunny.y})")
                adjacent_bunnies.append(bunny)
        return adjacent_bunnies
       
    def place_bunny(self, bunny, x, y):
        if self.is_empty(x, y):
            bunny.x = x
            bunny.y = y
            self.cells[y][x] = bunny
            self.bunnies.append(bunny)
            return True
        return False
    
    def remove_bunny(self, bunny):
        if bunny in self.bunnies:
            self.cells[bunny.y][bunny.x] = None
            self.bunnies.remove(bunny)
            return True
        return False

    def draw_grid(self):
        for x in range(0, SCREEN_WIDTH, TILE_SIZE):
            pygame.draw.line(self.screen, GRID_COLOR, (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, TILE_SIZE):
            pygame.draw.line(self.screen, GRID_COLOR, (0, y), (SCREEN_WIDTH, y))


    def update(self):
        self.screen.fill(BG_COLOR)
        
        for bunny in self.bunnies:            
            px = bunny.x * TILE_SIZE
            py = bunny.y * TILE_SIZE
            bunny.draw(self.screen, px, py)           

        self.draw_grid()      
        pygame.display.flip()

