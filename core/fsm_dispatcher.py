# core/fsm_dispatcher.py

import random
from core.bunny import Bunny

class FSMDispatcher:
    def __init__(self):
        self.mode = "FSM"  # Future use: "RL" or "HYBRID"

    def update_bunny(self, bunny, grid, turn, logger):
        if bunny.is_mutant:
            return self.vampire_behavior(bunny, grid, turn, logger)
        elif not bunny.is_adult():
            return self.juvenile_behavior(bunny, grid, turn, logger)
        elif bunny.sex == 'F':
            return self.adult_female_behavior(bunny, grid, turn, logger)
        else:
            return self.adult_male_behavior(bunny, grid, turn, logger)

    def juvenile_behavior(self, bunny, grid, turn, logger):
        if not bunny.is_mutant and random.random() < 0.02:
            bunny.is_mutant = True
            if logger:
                logger.log(turn, "mutation", bunny, "juvenile mutation", controller="FSM")
        bunny.move_random(grid)

    def adult_male_behavior(self, bunny, grid, turn, logger):
        neighbors = grid.find_adjacent_entities(bunny.x, bunny.y)
        for other in neighbors:
            if other.sex == 'F' and other.is_adult() and not other.is_mutant:
                grid.move_toward(bunny, other.x, other.y)
                return
        bunny.move_random(grid)

    def adult_female_behavior(self, bunny, grid, turn, logger):
        neighbors = grid.find_adjacent_entities(bunny.x, bunny.y)
        can_breed = any(b.sex == 'M' and b.is_adult() and not b.is_mutant for b in neighbors)
        if can_breed:
            empty_tiles = grid.get_adjacent_empty_tiles(bunny.x, bunny.y)
            if empty_tiles:
                nx, ny = random.choice(empty_tiles)
                baby = Bunny(
                    name=f"J{random.randint(1000,9999)}",
                    sex=random.choice(['M', 'F']),
                    x=nx, y=ny,
                    age=0,
                    mutant=False
                )
                baby.color = bunny.color
                grid.place_bunny(baby, nx, ny)
                if logger:
                    logger.log(turn, "birth", baby, f"born to {bunny.name}", controller="FSM")
        bunny.move_random(grid)

    def vampire_behavior(self, bunny, grid, turn, logger):
        targets = [b for b in grid.find_adjacent_entities(bunny.x, bunny.y) if not b.is_mutant]
        if targets:
            victim = random.choice(targets)
            if not victim.is_mutant:
                victim.is_mutant = True
                if logger:
                    logger.log(turn, "infection", victim, f"bitten by {bunny.name}", controller="FSM")
        bunny.move_random(grid)
