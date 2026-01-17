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
        self.color = (255, 0, 0) if mutant else (0, 0, 255) if sex == 'M' else (255, 105, 180)

    
    def is_adult(self):
        return self.age >= 2

    def max_age(self):
        return 50 if self.is_mutant else 10
    
    def make_baby(self, x, y, grid):        pass 


    
    def update(self, grid, turn, logger=None):
        pass



    def move(self, dx, dy, grid):
        pass

            
    def draw(self, screen, px, py):
        pass
