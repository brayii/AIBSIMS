# core/fsm_dispatcher.py


import random
from core.rl_agent import BunnyRLAgent, load_agent_qtable 


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
    if bunny.has_baby:
           reward += 10  # Big bonus for successful birth
    
    if not bunny.has_baby:
        male_adj = any(
            b.sex == 'M' and b.is_adult() and not b.is_mutant
            for b in grid.get_adjacent_bunnies(bunny.x, bunny.y)
        )
        empty_tiles = grid.get_adjacent_empty_tiles(bunny.x, bunny.y)
        if male_adj and len(empty_tiles) > 0:
            reward -= 1  # Small missed-opportunity penalty

    return reward
    


def reward_func_male(bunny, grid):
    if not bunny.is_adult() or bunny.sex != 'M':
        return 0  # Only applies to adult males

    reward = 1  # Survived a turn

    neighbors = grid.get_adjacent_bunnies(bunny.x, bunny.y)
    empty_tiles = grid.get_adjacent_empty_tiles(bunny.x, bunny.y)

    # Count adjacent females and vampires
    num_females = sum(1 for b in neighbors if b.sex == 'F' and b.is_adult() and not b.is_mutant)
    num_vampires = sum(1 for b in neighbors if b.is_mutant)

    if num_females > 0:
        reward += 2  # mating opportunity

    if num_vampires > 0:
        reward -= 20  # danger zone

    # Check if breeding occurred (female nearby gave birth)
    if any(b.sex == 'F' and b.has_baby for b in neighbors):
        reward += 10  # successful mating

    # Bonus for standing in favorable heatmap zone
    if hasattr(grid, 'female_heatmap'):
        try:
            if grid.female_heatmap.data[bunny.x][bunny.y] > 1.0:
                reward += 2
        except IndexError as e:
            print(f"[WARN] Heatmap out-of-bounds for bunny {bunny.name} at ({bunny.x},{bunny.y}): {e}")


    # Additional penalty for being too close to mutants
    #if any(b.is_mutant for b in neighbors):
    #    reward -= 10  # close-range threat

    # Penalty if male could have bred but didn’t
    can_breed = num_females > 0 and len(empty_tiles) > 0
    if can_breed and not any(b.sex == 'F' and b.has_baby for b in neighbors):
        reward -= 1

    if bunny.age > bunny.max_age():
        reward -= 50  # death penalty

    return reward

def reward_func_vampire(bunny, grid):
    if not bunny.is_adult() or not bunny.is_mutant:
        return 0

    reward = 1  # survived a turn

    neighbors = grid.get_adjacent_bunnies(bunny.x, bunny.y)
    victims = [b for b in neighbors if not b.is_mutant]

    if victims:
        reward += 10  # successful infection

    if not victims:
        reward -= 1  # wandering without prey

    if sum(1 for b in neighbors if b.is_mutant) > 1:
        reward -= 2  # overcrowding

    if bunny.age > bunny.max_age():
        reward -= 50

    return reward

def reward_func_juvenile(bunny, grid):
    if bunny.adult or bunny.is_mutant:
        return 0

    reward = 1  # survived a turn

    # Becomes adult = goal reached
    if bunny.age >= 2:
        reward += 10

    # Vampire adjacent = dangerous
    neighbors = grid.get_adjacent_bunnies(bunny.x, bunny.y)
    if any(b.is_mutant for b in neighbors):
        reward -= 10

    return reward

def vampire_nearby(bunny, grid):
        neighbors = grid.get_adjacent_bunnies(bunny.x, bunny.y)
        return any(b.is_mutant for b in neighbors)

def is_vampire_in_range(grid, x, y, radius=2):
    for dx in range(-radius, radius + 1):
        for dy in range(-radius, radius + 1):
            tx, ty = x + dx, y + dy
            if grid.in_bounds(tx, ty):
                b = grid.get_bunny_at(tx, ty)
                if b and b.is_mutant:
                    return True
    return False

class FSMDispatcher:
    def __init__(self, mode="RL"):
        self.mode = mode  # "FSM" or "RL"
        self.rl_agents = {}

    def update_bunny(self, bunny, grid, turn, logger=None):
        if self.mode == "RL":
            if bunny.name not in self.rl_agents:
                agent = BunnyRLAgent(bunny)
                q = load_agent_qtable(bunny.name)
                if q:
                    agent.q_table = q
                self.rl_agents[bunny.name] = agent

            if bunny.is_mutant:
                self.vampire_behavior_rl(bunny, grid, turn, logger)
                self.rl_agents[bunny.name].step(grid, turn, logger, reward_func_vampire)
            elif not bunny.is_adult():
                self.juvenile_behavior(bunny, grid, turn, logger)
                self.rl_agents[bunny.name].step(grid, turn, logger, reward_func_juvenile)
            elif bunny.sex == "M":
                self.adult_male_behavior(bunny, grid, turn, logger)
                self.rl_agents[bunny.name].step(grid, turn, logger, reward_func_male)
            else:
                self.adult_female_behavior(bunny, grid, turn, logger)
                self.rl_agents[bunny.name].step(grid, turn, logger, reward_func_female)

        else:
            # FSM only mode
            if bunny.is_mutant:
                self.vampire_behavior(bunny, grid, turn, logger)
            elif not bunny.is_adult():
                self.juvenile_behavior(bunny, grid, turn, logger)
            elif bunny.sex == "M":
                self.adult_male_behavior(bunny, grid, turn, logger)
            else:
                self.adult_female_behavior(bunny, grid, turn, logger)


    def juvenile_behavior(self, bunny, grid, turn, logger):
        # Mutate if adjacent to vampire
        neighbors = grid.get_adjacent_bunnies(bunny.x, bunny.y)
        if any(b.is_mutant for b in neighbors):
            bunny.is_mutant = True
            if logger:
                logger.log(turn, "mutation", bunny, "converted to vampire")
            return

        # Grow into adult
        if bunny.age >= 2:
            bunny.adult = True
            if logger:
                logger.log(turn, "adult", bunny, "became adult")

        # Flee if vampire in range
        if is_vampire_in_range(grid, bunny.x, bunny.y, radius=2):
            safe_tiles = grid.get_adjacent_empty_tiles(bunny.x, bunny.y)
            best_tile = None
            max_dist = -1
            for (tx, ty) in safe_tiles:
                dist = grid.nearest_vampire_distance(tx, ty)
                if dist is not None and dist > max_dist:
                    best_tile = (tx, ty)
                    max_dist = dist
            if best_tile:
                grid.move_bunny(bunny, *best_tile)
                if logger:
                    logger.log(turn, "flee", bunny, f"fled to ({best_tile[0]},{best_tile[1]})")
            else:
                bunny.move_random(grid)
        else:
            bunny.move_random(grid)


    def adult_female_behavior(self, bunny, grid, turn, logger):  
        neighbors = grid.get_adjacent_bunnies(bunny.x, bunny.y)
        vampires = [b for b in neighbors if b.is_mutant]
        babies = [b for b in neighbors if b.age < 2 and not b.is_mutant]
        males = [b for b in neighbors if b.sex == 'M' and b.is_adult() and not b.is_mutant]
        empty_tiles = grid.get_adjacent_empty_tiles(bunny.x, bunny.y)

        if vampires and babies:
            bunny.state = "PROTECT"
        elif vampires:
            bunny.state = "FLEE_VAMPIRE"
        elif males and empty_tiles:
            bunny.state = "BREED"
        elif males:
            bunny.state = "SEEK_MATE"
        else:
            bunny.state = "IDLE"

        if logger:
            logger.log(turn, "state", bunny, f"FSM: {bunny.state}")

        if bunny.state == "PROTECT":
            pass  # future: move into line-of-sight between vampire and baby
        elif bunny.state == "FLEE_VAMPIRE":
            self.move_away_from_threat(bunny, grid, vampires)
            if logger:
                logger.log(turn, "flee", bunny, "escaped vampire")
        elif bunny.state == "SEEK_MATE":
            grid.move_toward(bunny, males[0].x, males[0].y)
        elif bunny.state == "BREED":
            nx, ny = random.choice(empty_tiles)
            baby = bunny.make_baby(nx, ny, grid=grid)
            grid.place_bunny(baby, nx, ny)
            if logger:
                logger.log(turn, "birth", baby, f"by {bunny.name}")
        else:
            bunny.move_random(grid)


    def adult_male_behavior(self, bunny, grid, turn, logger):   
        neighbors = grid.get_adjacent_bunnies(bunny.x, bunny.y)
        females = [b for b in neighbors if b.sex == 'F' and b.is_adult() and not b.is_mutant]

        if females:
            bunny.state = "WAIT_NEAR_FEMALE"
        elif grid.female_heatmap.best_tile_value() > 1.0:
            bunny.state = "SEEK_MATE_ZONE"
        else:
            bunny.state = "WANDER"

        if logger:
            logger.log(turn, "state", bunny, f"FSM: {bunny.state}")

        if bunny.state == "WAIT_NEAR_FEMALE":
            pass
        elif bunny.state == "SEEK_MATE_ZONE":
            tx, ty = grid.female_heatmap.best_tile()
            grid.move_toward(bunny, tx, ty)
            if logger:
                logger.log(turn, "seeking_fertile", bunny, f"moving toward ({tx},{ty})")
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

    def vampire_behavior_rl(self, bunny, grid, turn, logger):
        neighbors = grid.get_adjacent_bunnies(bunny.x, bunny.y)
        victims = [b for b in neighbors if not b.is_mutant]

        if victims:
            victim = random.choice(victims)
            victim.is_mutant = True
            if logger:
                logger.log(turn, "infection", bunny, f"infected {victim.name}")
            bunny.move_random(grid)
        else:
            if hasattr(grid, 'bunny_density_map'):
                tx, ty = grid.bunny_density_map.best_tile()
                grid.move_toward(bunny, tx, ty)
                if logger:
                    logger.log(turn, "hunt", bunny, f"moved toward density ({tx},{ty})")
            else:
                bunny.move_random(grid)

    def move_away_from_threat(self, bunny, grid, threats):
        safe_dirs = []
        for dx, dy in grid.get_adjacent_offsets():
            nx, ny = bunny.x + dx, bunny.y + dy
            if grid.in_bounds(nx, ny) and grid.cells[nx][ny] is None:
                danger = any(abs(nx - t.x) + abs(ny - t.y) <= 1 for t in threats)
                if not danger:
                    safe_dirs.append((nx, ny))
        if safe_dirs:
            grid.move_bunny(bunny, *random.choice(safe_dirs))
        else:
            bunny.move_random(grid)

    
