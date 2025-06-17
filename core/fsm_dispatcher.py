# core/fsm_dispatcher.py

from core.rl_agent import BunnyRLAgent
import random

# ✅ Female reward function — GLOBAL SCOPE
def reward_func_female(bunny, grid):
    if not bunny.is_adult() or bunny.sex != 'F':
        return 0  # only applies to adult females

    reward = 1  # survived a turn

    neighbors = grid.get_adjacent_bunnies(bunny.x, bunny.y)
    empty_tiles = grid.get_adjacent_empty_tiles(bunny.x, bunny.y)

    num_males = sum(1 for b in neighbors if b.sex == 'M' and b.is_adult() and not b.is_mutant)
    num_vampires = sum(1 for b in neighbors if b.is_mutant)

    if num_males > 0:
        reward += 2  # mating opportunity

    if len(empty_tiles) == 0:
        reward -= 5  # no space to breed

    if num_vampires > 0:
        reward -= 20  # dangerous neighborhood

    if bunny.age > bunny.max_age():
        reward -= 50  # death penalty

    return reward


class FSMDispatcher:
    def __init__(self, mode="FSM"):
        self.mode = mode  # "FSM" or "RL"
        self.rl_agents = {}

    def update_bunny(self, bunny, grid, turn, logger=None):
        if self.mode == "RL":
            if bunny.sex == 'F' and bunny.is_adult():
                if bunny.name not in self.rl_agents:
                    self.rl_agents[bunny.name] = BunnyRLAgent(bunny)
                self.rl_agents[bunny.name].step(grid, turn, logger, reward_func_female)
                return

            # All other bunnies fallback to FSM
            if bunny.is_mutant:
                self.vampire_behavior(bunny, grid, turn, logger)
            elif not bunny.is_adult():
                self.juvenile_behavior(bunny, grid, turn, logger)
            elif bunny.sex == "M":
                self.adult_male_behavior(bunny, grid, turn, logger)
            else:
                self.adult_female_behavior(bunny, grid, turn, logger)

        else:
            # FSM mode
            if bunny.is_mutant:
                self.vampire_behavior(bunny, grid, turn, logger)
            elif not bunny.is_adult():
                self.juvenile_behavior(bunny, grid, turn, logger)
            elif bunny.sex == "M":
                self.adult_male_behavior(bunny, grid, turn, logger)
            else:
                self.adult_female_behavior(bunny, grid, turn, logger)

    def juvenile_behavior(self, bunny, grid, turn, logger):
        if random.random() < 0.02:
            bunny.is_mutant = True
            if logger:
                logger.log(turn, "mutation", bunny, "vampire")
            return
        bunny.move_random(grid)

    def adult_female_behavior(self, bunny, grid, turn, logger):
        neighbors = grid.get_adjacent_bunnies(bunny.x, bunny.y)
        can_breed = any(
            b.sex == 'M' and b.is_adult() and not b.is_mutant for b in neighbors
        )
        if can_breed:
            empty_tiles = grid.get_adjacent_empty_tiles(bunny.x, bunny.y)
            if empty_tiles:
                nx, ny = random.choice(empty_tiles)
                baby = bunny.make_baby(nx, ny)
                grid.place_bunny(baby, nx, ny)
                if logger:
                    logger.log(turn, "birth", baby, f"by {bunny.name}")
        bunny.move_random(grid)

    def adult_male_behavior(self, bunny, grid, turn, logger):
        neighbors = grid.get_adjacent_bunnies(bunny.x, bunny.y)
        females = [b for b in neighbors if b.sex == 'F' and b.is_adult() and not b.is_mutant]
        if females:
            target = random.choice(females)
            grid.move_toward(bunny, target.x, target.y)
        else:
            bunny.move_random(grid)

    def vampire_behavior(self, bunny, grid, turn, logger):
        neighbors = grid.get_adjacent_bunnies(bunny.x, bunny.y)
        victims = [b for b in neighbors if not b.is_mutant]
        if victims:
            victim = random.choice(victims)
            victim.is_mutant = True
            if logger:
                logger.log(turn, "infection", bunny, f"infected {victim.name}")
        bunny.move_random(grid)
