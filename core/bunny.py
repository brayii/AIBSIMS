import random
import pygame

class Bunny:
    def __init__(self, sex, x=0, y=0, age=0, mutant=False, color=None):
        
        name = ["Fluffy", "Thumper", "Coco", "BunBun", "Hopper", "Nibbles", "Snowball", "Midnight"]
        self.name = random.choice(name)

        self.id = random.randint(1000, 9999)  # Unique identifier for logging

        self.sex = sex  # 'M' or 'F'
       
        self.x = x
        self.y = y
        self.age = age
        self.is_mutant = mutant

        colors = [
            (139, 69, 19), # brown
            (255, 255, 255), # white
            (192, 192, 192) # gray
         ]
        if self.is_mutant:
            self.color = (255, 0, 0)  # red for mutants
        else:
            if color is not None:
                self.color = color
            else:  
                self.color = random.choice(colors)
                

    
    def is_adult(self):
        return self.age >= 2

    def max_age(self):
        return 50 if self.is_mutant else 10
    
    def make_baby(self, motherColor, x, y): 
        baby = Bunny(random.choice(['M', 'F']), x=x, y=y, age=0, mutant=False if random.random() > 0.02 else True, color=motherColor)
        baby.id = random.randint(1000, 9999)  # Unique identifier for logging
        return baby
        
    def bunny_death(self, grid):
        if self.age > self.max_age():
            # grid.cells[self.y][self.x] = None
            # grid.bunnies.remove(self)
            return grid.remove_bunny(self)
        else:
            return False

    def update(self, grid):
        self.age += 1
        
        # if self.age > self.max_age():
        #     # Bunny dies of old age
        #     grid.cells[self.y][self.x] = None
        #     grid.bunnies.remove(self) 


    def move(self, dx, dy, grid):
        new_x = self.x + dx
        new_y = self.y + dy
        if grid.is_empty(new_x, new_y):
            grid.cells[self.y][self.x] = None # Update grid cell
            self.x = new_x
            self.y = new_y
            grid.cells[new_y][new_x] = self
            return True
        return False

    def draw_male_marker(self, screen, px, py):
        font = pygame.font.SysFont(None, 24) 
        text_surface = font.render("M", True, (0, 0, 255)) # blue for
        text_rect = text_surface.get_rect(center=(px + 16, py + 16)) 
        screen.blit(text_surface, text_rect)

    def draw_female_marker(self, screen, px, py):
        font = pygame.font.SysFont(None, 24) 
        text_surface = font.render("F", True, (255, 192, 203)) # pink for
        text_rect = text_surface.get_rect(center=(px + 16, py + 16)) 
        screen.blit(text_surface, text_rect)

    def draw_mutant_marker(self, screen, px, py):
        font = pygame.font.SysFont(None, 24) 
        text_surface = font.render("X", True, (255, 255, 255)) # white for
        text_rect = text_surface.get_rect(center=(px + 16, py + 16)) 
        screen.blit(text_surface, text_rect)    

    def draw_baby_marker(self, screen, px, py):
        size = 32
        padding = 8
        rect = pygame.Rect(px + padding, py + padding, size - 2 * padding, size - 2 * padding)
        pygame.draw.ellipse(screen, (255, 255, 0), rect)  # yellow for babies   


    def draw(self, screen, px, py):
        # Draw a square for the bunny
        size = 32
        padding = 4
        rect = pygame.Rect(px + padding, py + padding, size - 2 * padding, size - 2 * padding)
        pygame.draw.rect(screen, self.color, rect)         
        
        # Male indicator (blue M)
        if self.sex == 'M':
            self.draw_male_marker(screen, px, py)
            # font = pygame.font.SysFont(None, 24) 
            # text_surface = font.render("M", True, (0, 0, 255)) # blue for Males 
            # text_rect = text_surface.get_rect(center=rect.center) 
            # screen.blit(text_surface, text_rect)
        # Female indicator (pink F)
        elif self.sex == 'F':
            self.draw_female_marker(screen, px, py)
            # font = pygame.font.SysFont(None, 24) 
            # text_surface = font.render("F", True, (255, 192, 203)) # pink for Females 
            # text_rect = text_surface.get_rect(center=rect.center) 
            # screen.blit(text_surface, text_rect)
        # mutant indicator (white X for mutants)
        elif self.is_mutant:
            self.draw_mutant_marker(screen, px, py)
            # font = pygame.font.SysFont(None, 24) 
            # text_surface = font.render("X", True, (255, 255, 255)) # white for mutants
            # text_rect = text_surface.get_rect(center=rect.center) 
            # screen.blit(text_surface, text_rect)
        # elif not self.is_adult():
        #     self.draw_baby_marker(screen, px, py)
            # size = 32
            # padding = 8
            # rect = pygame.Rect(px + padding, py + padding, size - 2 * padding, size - 2 * padding)
            # pygame.draw.ellipse(screen, (255, 255, 0), rect)  # yellow for babies
        else:
            pass # No indicator

        if not self.is_adult():
            # Draw a smaller ellipse in the center to indicate a baby
            self.draw_baby_marker(screen, px, py)
            # pygame.draw.ellipse(screen, (255, 255, 0), rect.inflate(-size // 2, -size // 2))  # yellow for babies
    
    def get_features(self, grid):
        # Example feature extraction for SL model
        features = {
            "x": self.x,
            "y": self.y,
            "age": self.age,
            "is_adult": int(self.is_adult()),
            "is_mutant": int(self.is_mutant),
            "sex": 1 if self.sex == 'M' else 0
        }
        return features
