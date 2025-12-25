# core/fsm_dispatcher.py


import random

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
    def __init__(self):
           pass      


    def update_bunny(self, bunny, grid, turn, logger=None):
        # Determine bunny type and reward function — used in both FSM and RL
        if bunny.is_mutant:
            btype = 'vampire'           
        elif not bunny.is_adult():
            btype = 'juvenile'           
        elif bunny.sex == "M":
            btype = 'male'            
        else:
            btype = 'female'   
        role = btype  

        # FSM behavior execution
        if bunny.is_mutant:
            self.vampire_behavior(bunny, grid, turn, logger)
        elif not bunny.is_adult():
            self.juvenile_behavior(bunny, grid, turn, logger)
        elif bunny.sex == "M":
            self.adult_male_behavior(bunny, grid, turn, logger)
        else:
            self.adult_female_behavior(bunny, grid, turn, logger)


    def juvenile_behavior(self, bunny, grid, turn, logger):
        # if logger:     
        #     logger.log(turn, "move", bunny, bunny.state, controller="FSM")
        # else:
        #     pass

        if any(b.is_mutant for b in grid.get_adjacent_bunnies(bunny.x, bunny.y)):
            bunny.is_mutant = True
            if logger:
                logger.log(turn, "mutation", bunny, "converted to vampire")
            return
# 
        if bunny.age >= 2:
            bunny.adult = True
            if logger:
                logger.log(turn, "adult", bunny, "became adult")

        if is_vampire_in_range(grid, bunny.x, bunny.y, radius=2):
            safe_tiles = grid.get_adjacent_empty_tiles(bunny.x, bunny.y)
            best = max(safe_tiles, key=lambda t: grid.nearest_vampire_distance(*t) or -1, default=None)
            if best:
                # grid.move_bunny(bunny, *best)
                bunny.move(*best, grid)
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
        males = [b for b in neighbors if b.sex == 'M' and b.is_adult() and not b.is_mutant]        
        empty_tiles = grid.get_adjacent_empty_tiles(bunny.x, bunny.y)

        if vampires and babies:
            state = "PROTECT"
        elif vampires:
            state = "FLEE_VAMPIRE"
        elif males and empty_tiles:
            state = "BREED"
        # elif males:
        #     state = "SEEK_MATE"
        else:
            state = "IDLE"
        
        if bunny.state != state:
            bunny.state = state
            #if logger:
            #    logger.log(turn, "state", bunny, f"FSM: {state}")   

        if state == "PROTECT":
            self.move_away_from_threat(bunny, grid, vampires)  # Simple block
            if logger:
                logger.log(turn, "protect", bunny, "shielded baby from vampire", f"FSM: {state}")
        elif state == "FLEE_VAMPIRE":
            self.move_away_from_threat(bunny, grid, vampires)
            if logger:
                logger.log(turn, "flee", bunny, "escaped vampire", f"FSM: {state}")
        # elif state == "SEEK_MATE":
        #     grid.move_toward(bunny, males[0].x, males[0].y)
        #     if logger:
        #         logger.log(turn, "seek", bunny, f"moving toward male {males[0].name}", f"FSM: {state}")
        elif state == "BREED":
            if empty_tiles:
                nx, ny = random.choice(empty_tiles)
                baby = bunny.make_baby(nx, ny, grid=grid)
                grid.place_bunny(baby, nx, ny)
                if logger:
                    logger.log(turn, "birth", baby, f"by {bunny.name}")
        else:
            bunny.move_random(grid)
            if logger:
                logger.log(turn, "move", bunny, "wandering", f"FSM: {state}")


    def adult_male_behavior(self, bunny, grid, turn, logger):  
        neighbors = grid.get_adjacent_bunnies(bunny.x, bunny.y)
        females = [b for b in neighbors if b.sex == 'F' and b.is_adult() and not b.is_mutant]
        has_heat_target = grid.female_heatmap and grid.female_heatmap.best_tile_value() > 1.0

        # if females:
        #     state = "WAIT_NEAR_FEMALE"
        if has_heat_target and females:
            state = "SEEK_MATE_ZONE"
        else:
            state = "WANDER"

        if bunny.state != state:
            bunny.state = state
        # #     if logger:
        # #         logger.log(turn, "state", bunny, f"FSM: {state}")
        if state == "SEEK_MATE_ZONE":
            tx, ty = grid.female_heatmap.best_tile()
            grid.move_toward(bunny, tx, ty)
            if logger:
                logger.log(turn, "seek", bunny, f"moving toward ({tx},{ty})", f"FSM: {state}")
        elif state == "WANDER":
            bunny.move_random(grid)
            if logger:
                logger.log(turn, "move", bunny, "wandering", f"FSM: {state}")
        #elif state == "WAIT_NEAR_FEMALE":
        #    bunny.move(bunny.x, bunny.y, grid)  # stay put
        #    if logger:
        #        logger.log(turn, "wait", bunny, "waiting near female", f"FSM: {state}")
        #else:
        #    bunny.move_random(grid)
        #    if logger:
        #        logger.log(turn, "move", bunny, "wandering")

    def vampire_behavior(self, bunny, grid, turn, logger):
        # if logger:     
        #     logger.log(turn, "move", bunny, bunny.state, controller="FSM")
        # else:
        #     pass
        
        neighbors = grid.get_adjacent_bunnies(bunny.x, bunny.y)
        victims = [b for b in neighbors if not b.is_mutant]
        if victims:
             victim = random.choice(victims)
             victim.is_mutant = True
             if logger:
                 logger.log(turn, "infection", bunny, f"infected {victim.name}")
        else:
             bunny.move_random(grid)
             if logger:
                 logger.log(turn, "move", bunny, "wandering")
            
            # heatmap = grid.get_bunny_density_map()
            # best = None
            # best_score = -1
            # for dx, dy in grid.get_valid_moves(bunny):
            #     nx, ny = bunny.x + dx, bunny.y + dy
            #     score = sum(heatmap[i][j]
            #                 for i in range(max(0, nx - 2), min(grid.GRID_WIDTH, nx + 3))
            #                 for j in range(max(0, ny - 2), min(grid.GRID_HEIGHT, ny + 3)))
            #     if score > best_score:
            #         best_score = score
            #         best = (nx, ny)
            # if best:
            #     grid.move_bunny(bunny, *best)
            # else:
            #     bunny.move_random(grid)


    def move_away_from_threat(self, bunny, grid, threats):
        safe_dirs = []
        for dx, dy in grid.get_adjacent_offsets():
            nx, ny = bunny.x + dx, bunny.y + dy
            if grid.in_bounds(nx, ny) and grid.cells[ny][nx] is None:
                danger = any(abs(nx - t.x) + abs(ny - t.y) <= 1 for t in threats)
                if not danger:
                    safe_dirs.append((nx, ny))
        if safe_dirs:
            #grid.move_bunny(bunny, *random.choice(safe_dirs))
            bunny.move(*random.choice(safe_dirs), grid)
        else:
            bunny.move_random(grid)

    
