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
        self.state = "IDLE"  # initial FSM state for adult females
        self.has_baby = False  # Tracks recent birth
        self.color = (255, 0, 0) if mutant else (0, 0, 255) if sex == 'M' else (255, 105, 180)

    def is_adult(self):
        return self.age >= 2

    def max_age(self):
        return 50 if self.is_mutant else 10

    def make_baby(self, x, y):
        """Create a new Bunny at position (x, y) with inherited properties."""
        self.has_baby = True
        is_mutant = random.random() < 0.02  # 2% spontaneous vampire birth
        return Bunny(
            name=f"{self.name}_baby",
            sex=random.choice(['F', 'M']),
            x=x,
            y=y,
            mutant=is_mutant
        )

    
    def update(self, grid, turn, logger=None):
        self.has_baby = False  # Clear after each turn
        self.age += 1
        if self.age > self.max_age():
            grid.remove_bunny(self)
            if logger:
                logger.log(turn, "death", self, "natural causes", controller="FSM")

    def move_random(self, grid):
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        random.shuffle(directions)
        for dx, dy in directions:
            nx, ny = self.x + dx, self.y + dy
            if 0 <= nx < grid.GRID_WIDTH and 0 <= ny < grid.GRID_HEIGHT and grid.cells[nx][ny] is None:
                grid.move_bunny(self, nx, ny)
                return

    def draw(self, screen, px, py):
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
