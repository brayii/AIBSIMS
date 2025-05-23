# bunny.py
import random

COLORS = ["white", "brown", "black", "spotted"]

class Bunny:
    def __init__(self, name, sex, x, y, mutant=False, age=0):
        self.name = name
        self.sex = sex  # 'M' or 'F'
        self.color = random.choice(COLORS)
        self.age = age
        self.is_mutant = mutant
        self.x = x
        self.y = y

    def is_adult(self):
        return self.age >= 2

    def max_age(self):
        return 50 if self.is_mutant else 10

    def display_char(self):
        if self.is_mutant:
            return 'X'
        if self.sex == 'M':
            return 'M' if self.is_adult() else 'm'
        else:
            return 'F' if self.is_adult() else 'f'
