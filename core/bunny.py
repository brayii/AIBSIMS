import random
import pygame

class Bunny:
    def __init__(self, name, sex, x, y, age=0, mutant=False):
        self.name = name
        self.sex = sex  # 'M' or 'F'
        self.x = x
        self.y = y
        self.age = age
        self.is_mutant = mutant
        self.state = "IDLE"
        self.has_baby = False
        self.adult = False
        self.color = (255, 0, 0) if mutant else (0, 0, 255) if sex == 'M' else (255, 105, 180)

    
    def is_adult(self):
        return self.age >= 2

    def max_age(self):
        return 50 if self.is_mutant else 10
    
    def make_baby(self, x, y, grid):
        self.has_baby = True
        grid.total_bunny_births += 1
        is_mutant = False

        if grid.total_bunny_births > 0:
            ratio = grid.total_vampire_births / grid.total_bunny_births
            if ratio < 0.02 and random.random() < 0.02:
                is_mutant = True
                grid.total_vampire_births += 1

        return Bunny(
            name=f"{self.name}_baby",
            sex=random.choice(['F', 'M']),
            x=x,
            y=y,
            mutant=is_mutant
        )
    
    def update(self, grid, turn, logger=None):
        self.has_baby = False
        self.age += 1
        if self.age > self.max_age():
            grid.remove_bunny(self)
            if logger:
                logger.log(turn, "death", self, "natural causes", controller="FSM")

    def move(self, dx, dy, grid):
        """Move the bunny by (dx, dy) if the target cell is empty and in bounds."""
        nx, ny = self.x + dx, self.y + dy
        if grid.in_bounds(nx, ny) and grid.cells[nx][ny] is None:
            grid.cells[self.x][self.y] = None
            self.x, self.y = nx, ny
            grid.cells[nx][ny] = self
            
    def move_random(self, grid):
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        random.shuffle(directions)
        for dx, dy in directions:
            nx, ny = self.x + dx, self.y + dy
            if grid.in_bounds(nx, ny) and grid.cells[nx][ny] is None:
                grid.move_bunny(self, nx, ny)
                return
            
    def draw(self, screen, px, py):
        """Draw the bunny on the screen at position (px, py)."""
        # Draw a square for the bunny  
        size = 32
        padding = 4
        rect = pygame.Rect(px + padding, py + padding, size - 2 * padding, size - 2 * padding)

        # Determine fill color
        color = (255, 0, 0) if self.is_mutant else (0, 0, 255) if self.sex == 'M' else (255, 105, 180)
        pygame.draw.rect(screen, color, rect)

        # Juvenile indicator (gray ellipse)
        if not self.is_adult() and not self.is_mutant:
            pygame.draw.ellipse(screen, (200, 200, 200), rect.inflate(-10, -10))

        # Vampire indicator (white "X")
        if self.is_mutant:
            cx, cy = px + size // 2, py + size // 2
            pygame.draw.line(screen, (255, 255, 255), (cx - 6, cy - 6), (cx + 6, cy + 6), 2)
            pygame.draw.line(screen, (255, 255, 255), (cx + 6, cy - 6), (cx - 6, cy + 6), 2)
