# core/fsm_dispatcher.py


import random
import math
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

    bunny_population = len(grid.bunnies)

    if bunny_population >= 10:
        reward += 15  # colony is thriving
    elif bunny_population >= 20:
        reward += 30 # colony is doing well
    elif bunny_population >= 30:
        reward += 50 # colony is healthy
    elif bunny_population >= 50: 
        reward += 100 # colony is strong
    elif bunny_population >= 100:
        reward += 200   # colony is very strong
    else:
        reward -= 15  # colony is struggling

    if num_males > 0:
        reward += 2  # mating opportunity

    if len(empty_tiles) == 0:
        reward -= 5  # no space to breed

    if num_vampires > 0 or is_vampire_in_range(grid, bunny.x, bunny.y, radius=2):
        reward -= 10 # Near vampires
    else:
        reward += 5
        #reward -= 20  # dangerous neighborhood

    if bunny.age > bunny.max_age():
        reward -= 50  # death penalty
        
    if bunny.has_baby:
        reward += 25  # Big bonus for successful birth
    elif num_males > 0 and len(empty_tiles) > 0:
        reward -= 3  # Small missed-opportunity penalty 
    
    #colony_reward = grid.colony_rewards["population_bonus"] + grid.colony_rewards["vampire_free_bonus"]
    #reward += 0.1 * colony_reward  # scaled contribution
    
    return math.tanh(reward / 50.0)
    


def reward_func_male(bunny, grid):
    if not bunny.is_adult() or bunny.sex != 'M':
        return 0  # Only applies to adult males

    reward = 1  # Survived a turn       
    

    neighbors = grid.get_adjacent_bunnies(bunny.x, bunny.y)
    empty_tiles = grid.get_adjacent_empty_tiles(bunny.x, bunny.y)
    females = [b for b in neighbors if b.sex == 'F' and b.is_adult() and not b.is_mutant]
    vampires = [b for b in neighbors if b.is_mutant]
    
    if females:
        reward += 10 # Found a female
    # elif any(b.sex == 'F' and b.is_adult() for b in grid.bunnies if abs(b.x - bunny.x) + abs(b.y - bunny.y) <= 3):
    #     reward += 2 # Small incentive for being near a female

    if vampires or is_vampire_in_range(grid, bunny.x, bunny.y, radius=2):
        reward -= 20    # Dangerous neighborhood
    if any(b.sex == 'F' and b.has_baby for b in neighbors):
        reward += 10  # Found a female with a baby

    if hasattr(grid, 'female_heatmap') and grid.female_heatmap.data[bunny.x][bunny.y] > 1.0:
        reward += 2  # Standing in a favorable heatmap zone

    if females and empty_tiles and not any(b.has_baby for b in females):
        reward -= 1  # Small missed-opportunity penalty

    if bunny.age > bunny.max_age():
        reward -= 50  # Death penalty

    return reward

def reward_func_vampire(bunny, grid):
    if not bunny.is_adult or not bunny.is_mutant:
        return 0

    reward = 1
    neighbors = grid.get_adjacent_bunnies(bunny.x, bunny.y)
    victims = [b for b in neighbors if not b.is_mutant]
    adults = sum(1 for b in grid.bunnies if b.is_adult)
    
    if adults <= 15:
        reward -= 10   # Too few adults, risk of extinction
    if victims:
        reward += 10 # Successfully infected a bunny
    else:
        reward -= 1  # Wandering without prey

    if sum(1 for b in neighbors if b.is_mutant) > 1:
        reward -= 2  # Overcrowding penalty
    if bunny.age > bunny.max_age():
        reward -= 50  # Death penalty

    return math.tanh(reward / 50.0)

def reward_func_juvenile(bunny, grid):
    if bunny.is_adult or bunny.is_mutant:
        return 0

    reward = 1

    if is_vampire_in_range(grid, bunny.x, bunny.y, radius=2):
        reward -= 10 # Near vampires
    else:
        reward += 5
    if bunny.age >= 2:
        reward += 10 # Grown into adult
    #if any(b.is_mutant for b in grid.get_adjacent_bunnies(bunny.x, bunny.y)):
    #    reward -= 10 # Mutated into vampire

    return math.tanh(reward / 50.0)

#def vampire_nearby(bunny, grid):
#        neighbors = grid.get_adjacent_bunnies(bunny.x, bunny.y)
#        return any(b.is_mutant for b in neighbors)
#
def is_vampire_in_range(grid, x, y, radius=2):
    for dx in range(-radius, radius + 1):
        for dy in range(-radius, radius + 1):
            tx, ty = x + dx, y + dy
            if grid.in_bounds(tx, ty):
                b = grid.get_bunny_at(tx, ty)
                if b and b.is_mutant:
                    return True
    return False
#
#def move_vampire_toward_cluster(bunny, grid):
#        heatmap = grid.get_bunny_density_map()
#        directions = grid.get_valid_moves(bunny)
#
#        best_score = -float("inf")
#        best_move = None
#
#        for dx, dy in directions:
#            nx, ny = bunny.x + dx, bunny.y + dy
#            if grid.in_bounds(nx, ny) and grid.is_empty(nx, ny):
#                score = sum(
#                    heatmap[x][y]
#                    for x in range(max(0, nx-2), min(grid.GRID_WIDTH, nx+3))
#                    for y in range(max(0, ny-2), min(grid.GRID_HEIGHT, ny+3))
#                )
#                if score > best_score:
#                    best_score = score
#                    best_move = (dx, dy)
#
#        if best_move:
#            bunny.move(best_move[0], best_move[1], grid)

class FSMDispatcher:
    def __init__(self, mode="FSM"):
        self.mode = mode
        self.rl_agents = {}
        self.shared_tables = {k: load_agent_qtable(f"{k}_shared") or {} for k in ['male', 'female', 'juvenile', 'vampire']}


    def update_bunny(self, bunny, grid, turn, logger=None):
        # Determine bunny type and reward function — used in both FSM and RL
        if bunny.is_mutant:
            btype = 'vampire'
            reward_fn = reward_func_vampire
        elif not bunny.is_adult:
            btype = 'juvenile'
            reward_fn = reward_func_juvenile
        elif bunny.sex == "M":
            btype = 'male'
            reward_fn = reward_func_male
        else:
            btype = 'female'
            reward_fn = reward_func_female

        role = btype
        # Ensure agent exists (used even in FSM mode for training)
        if bunny.name not in self.rl_agents:
            self.rl_agents[bunny.name] = BunnyRLAgent(bunny, self.shared_tables[btype])
        agent = self.rl_agents[bunny.name]
        agent.use_dqn = True
        agent.load_model()


        if self.mode == "RL":
            s = agent.get_state(grid)
            agent.step(grid, turn, logger, reward_fn)
            #return reward_fn(bunny, grid), role  # you could capture this inside step() as well
            s_prime = agent.get_state(grid)            
            reward = reward_fn(bunny, grid)
            agent.update_q(s, 5, reward, s_prime, grid)
            #if turn % 5 == 0:
            max_turns = 10
            if agent.use_dqn and (turn % 5 == 0 or turn == max_turns - 1):
                agent.save_model()  # Auto-save per-role
            return reward, role
        #else:
        #    s = agent.get_state(grid)
        #    if btype == 'vampire':
        #        agent.infect(grid)
        #    elif btype == 'juvenile':
        #        agent.flee_from_vampires(grid)
        #    elif btype == 'male':
        #        agent.seek_female(grid)
        #    elif btype == 'female':
        #        agent.birth(grid)
#
        #    s_prime = agent.get_state(grid)
        #    reward = reward_fn(bunny, grid)
        #    agent.update_q(s, 5, reward, s_prime)
#
        #return reward_fn(bunny, grid)
        else:
            # FSM Mode — still collect RL experience
            s = agent.get_state(grid)
#            # FSM behavior execution
            if bunny.is_mutant:
                self.vampire_behavior(bunny, grid, turn, logger)
            elif not bunny.is_adult():
                self.juvenile_behavior(bunny, grid, turn, logger)
            elif bunny.sex == "M":
                self.adult_male_behavior(bunny, grid, turn, logger)
            else:
                self.adult_female_behavior(bunny, grid, turn, logger)
#            # Update Q-table based on FSM decision as if action 5 was taken
            s_prime = agent.get_state(grid)            
            reward = reward_fn(bunny, grid)
            agent.update_q(s, 5, reward, s_prime, grid)
            return reward, role
        
        return 0, None  # Default case, shouldn't happen

                



    def juvenile_behavior(self, bunny, grid, turn, logger):
        
        if any(b.is_mutant for b in grid.get_adjacent_bunnies(bunny.x, bunny.y)):
            bunny.is_mutant = True
            if logger:
                logger.log(turn, "mutation", bunny, "converted to vampire")
            return

        if bunny.age >= 2:
            bunny.adult = True
            if logger:
                logger.log(turn, "adult", bunny, "became adult")

        if is_vampire_in_range(grid, bunny.x, bunny.y, radius=2):
            safe_tiles = grid.get_adjacent_empty_tiles(bunny.x, bunny.y)
            best = max(safe_tiles, key=lambda t: grid.nearest_vampire_distance(*t) or -1, default=None)
            if best:
                grid.move_bunny(bunny, *best)
                if logger:
                    logger.log(turn, "flee", bunny, f"fled to {best}")
            else:
                bunny.move_random(grid)
        else:
            bunny.move_random(grid)



    def adult_female_behavior(self, bunny, grid, turn, logger):
        neighbors = grid.get_adjacent_bunnies(bunny.x, bunny.y)
        babies = [b for b in neighbors if b.age < 2 and not b.is_mutant]
        vampires = [b for b in neighbors if b.is_mutant]
        males = [b for b in neighbors if b.sex == 'M' and b.is_adult and not b.is_mutant]
        empty_tiles = grid.get_adjacent_empty_tiles(bunny.x, bunny.y)

        if vampires and babies:
            state = "PROTECT"
        elif vampires:
            state = "FLEE_VAMPIRE"
        elif males and empty_tiles:
            state = "BREED"
        elif males:
            state = "SEEK_MATE"
        else:
            state = "IDLE"

        if bunny.state != state:
            bunny.state = state
            if logger:
                logger.log(turn, "state", bunny, f"FSM: {state}")

        if state == "PROTECT":
            self.move_away_from_threat(bunny, grid, vampires)  # Simple block
        elif state == "FLEE_VAMPIRE":
            self.move_away_from_threat(bunny, grid, vampires)
            if logger:
                logger.log(turn, "flee", bunny, "escaped vampire")
        elif state == "SEEK_MATE":
            grid.move_toward(bunny, males[0].x, males[0].y)
        elif state == "BREED":
            if empty_tiles:
                nx, ny = random.choice(empty_tiles)
                baby = bunny.make_baby(nx, ny, grid=grid)
                grid.place_bunny(baby, nx, ny)
                if logger:
                    logger.log(turn, "birth", baby, f"by {bunny.name}")
        else:
            bunny.move_random(grid)



    def adult_male_behavior(self, bunny, grid, turn, logger):
        neighbors = grid.get_adjacent_bunnies(bunny.x, bunny.y)
        females = [b for b in neighbors if b.sex == 'F' and b.is_adult and not b.is_mutant]
        has_heat_target = grid.female_heatmap and grid.female_heatmap.best_tile_value() > 1.0

        if females:
            state = "WAIT_NEAR_FEMALE"
        elif has_heat_target:
            state = "SEEK_MATE_ZONE"
        else:
            state = "WANDER"

        if bunny.state != state:
            bunny.state = state
            if logger:
                logger.log(turn, "state", bunny, f"FSM: {state}")

        if state == "SEEK_MATE_ZONE":
            tx, ty = grid.female_heatmap.best_tile()
            grid.move_toward(bunny, tx, ty)
            if logger:
                logger.log(turn, "seek", bunny, f"moving toward ({tx},{ty})")
        elif state == "WANDER":
            bunny.move_random(grid)



    

    def vampire_behavior(self, bunny, grid, turn, logger):
        neighbors = grid.get_adjacent_bunnies(bunny.x, bunny.y)
        victims = [b for b in neighbors if not b.is_mutant]

        if victims:
            victim = random.choice(victims)
            victim.is_mutant = True
            if logger:
                logger.log(turn, "infection", bunny, f"infected {victim.name}")
        else:
            heatmap = grid.get_bunny_density_map()
            best = None
            best_score = -1
            for dx, dy in grid.get_valid_moves(bunny):
                nx, ny = bunny.x + dx, bunny.y + dy
                score = sum(heatmap[i][j]
                            for i in range(max(0, nx - 2), min(grid.GRID_WIDTH, nx + 3))
                            for j in range(max(0, ny - 2), min(grid.GRID_HEIGHT, ny + 3)))
                if score > best_score:
                    best_score = score
                    best = (nx, ny)
            if best:
                grid.move_bunny(bunny, *best)
            else:
                bunny.move_random(grid)


    #def vampire_behavior_rl(self, bunny, grid, turn, logger):
    #    neighbors = grid.get_adjacent_bunnies(bunny.x, bunny.y)
    #    victims = [b for b in neighbors if not b.is_mutant]
#
    #    if victims:
    #        victim = random.choice(victims)
    #        victim.is_mutant = True
    #        if logger:
    #            logger.log(turn, "infection", bunny, f"infected {victim.name}")
    #        bunny.move_random(grid)
    #        #move_vampire_toward_cluster(bunny, grid)
    #    else:
    #        if hasattr(grid, 'bunny_density_map'):
    #            tx, ty = grid.bunny_density_map.best_tile()
    #            grid.move_toward(bunny, tx, ty)
    #            if logger:
    #                logger.log(turn, "hunt", bunny, f"moved toward density ({tx},{ty})")
    #        else:
    #            bunny.move_random(grid)
    #            #move_vampire_toward_cluster(bunny, grid)

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

    
