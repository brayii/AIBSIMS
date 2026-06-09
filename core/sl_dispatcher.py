from core.grid import GRID_WIDTH, GRID_HEIGHT
from core.bunny import Bunny
import random
import os
from joblib import load

from core.fsm_dispatcher import FSMDispatcher

class SLDispatcher:
    def __init__(self, model_path="models/sl"):
        # Load your trained SL model here
        os.makedirs(model_path, exist_ok=True)
        female_model_path = os.path.join(model_path, "female_sl_logreg.joblib") 
        male_model_path = os.path.join(model_path, "male_sl_logreg.joblib")
        if not os.path.exists(female_model_path):
            print(f"Model file {female_model_path} not found. Please train the model and save it to this path.")
            exit(1)
        else:     
            self.female_model = load(female_model_path)
        
        if not os.path.exists(male_model_path):
            print(f"Model file {male_model_path} not found. Please train the model and save it to this path.")
            exit(1)
        else:
            self.male_model = load(male_model_path)

        self.fsm_dispatcher = FSMDispatcher()  # Create an instance of FSMDispatcher to reuse its methods
        self.threshold = 0.3  # you can tune this threshold based on your model's performance
        self.mutant_penalty = 10  # you can tune this penalty based on your model's performance

    def dispatch(self, bunny, grid, turn, logger=None):
        # Placeholder for FSM logic  
        if bunny is None:
            # Initialize with some bunnies
            colors = [
                (139, 69, 19), # brown
                (255, 255, 255), # white
                (192, 192, 192) # gray
             ]        

            pairs = [("F", "M"), ("F", "M")]
            for i, (s1, s2) in enumerate(pairs):
                x, y = random.randint(0, GRID_WIDTH - 2), random.randint(0, GRID_HEIGHT - 2)
                # b1 = Bunny(sex=s1, x=x, y=y)
                # b2 = Bunny(sex=s2, x=x+1, y=y)
                c1, c2 = random.sample(colors, 2) # always two different colors
                bunny1 = Bunny(sex=s1, x=x, y=y, color=c1)
                grid.place_bunny(bunny1, x, y)
                if logger:
                    logger.log(turn, "birth", bunny1, f"Spawned at ({x},{y})", controller="SL")
                bunny2 = Bunny(sex=s2, x=x+1, y=y, color=c2)
                grid.place_bunny(bunny2, x+1, y)
                if logger:
                    logger.log(turn, "birth", bunny2, f"Spawned at ({x+1},{y})", controller="SL")

            if grid.is_empty(x+1, y+1): 
                bunny3 = Bunny(sex=random.choice(['M', 'F']), x=x+1, y=y+1)
                grid.place_bunny(bunny3, x+1, y+1)
                if logger:
                    logger.log(turn, "birth", bunny3, f"Spawned at ({x+1},{y+1})", controller="SL")
            else:
                pass            
            
            return     
        
        if bunny.bunny_death(grid):
            if logger:
                logger.log(turn, "death", bunny, "Died of old age", controller="SL")
            return
                

        if bunny.is_mutant:
            self.fsm_dispatcher.mutant_behavior(bunny, grid, turn, logger) 
        elif not bunny.is_adult():
            self.fsm_dispatcher.juvenile_behavior(bunny, grid, turn, logger)
        elif bunny.sex == 'F':
            self.female_behavior(bunny, grid, turn, logger)
        else:
            self.male_behavior(bunny, grid, turn, logger)
            #self.fsm_dispatcher.male_behavior(bunny, grid, turn, logger)

    def female_behavior(self, bunny, grid, turn, logger=None):
        neighbors = grid.get_adjacent_bunnies(bunny.x, bunny.y)
        empty_tiles = grid.get_adjacent_empty_tiles(bunny.x, bunny.y)

        males = [n for n in neighbors if n.sex == "M" and n.is_adult() and not n.is_mutant]
        has_male = bool(males)
        has_space = bool(empty_tiles)
        feasible = has_male and has_space

        # Feature vector MUST match training order: [age, mutant, adj_male, adj_empty]
        mut = int(bunny.is_mutant)
        adj_male = int(has_male)
        adj_empty = int(has_space)
        vector = [bunny.age, mut, adj_male, adj_empty]

        p_breed = self.female_model.predict_proba([vector])[0][1]
        
        #want_breed = p_breed >= self.threshold
        want_breed = p_breed >= 0.20 # you can tune this threshold based on your model's performance

        # Decide what we will actually do (respect feasibility)
        do_breed = want_breed and feasible
        exec_action = "breed" if do_breed else "move"

        if logger:
            logger.log(
                turn,
                "decision",
                bunny,
                f"age={bunny.age} mutant={mut} adj_male={adj_male} adj_empty={adj_empty} "
                f"p_breed={p_breed:.2f} want={'breed' if want_breed else 'move'} "
                f"feasible={int(feasible)} exec={exec_action}",
                controller="SL",
            )

        if do_breed:
            x, y = random.choice(empty_tiles)
            if logger:
                logger.log(turn, "breeding", bunny,
                           f"Bred with male at ({males[0].x},{males[0].y}) baby_at=({x},{y})",
                           controller="SL")
            baby = bunny.make_baby(bunny.color, x, y)
            grid.place_bunny(baby, x, y)
            if logger:
                logger.log(turn, "birth", baby, f"Spawned at ({x},{y})", controller="SL")
        else:            
            self.move_towards_male(bunny, grid, logger, turn)          
    
    def male_behavior(self, bunny, grid, turn, logger=None):
        neighbors = grid.get_adjacent_bunnies(bunny.x, bunny.y)
    
        adjacent_females = [
            n for n in neighbors
            if n.sex == "F" and n.is_adult() and not n.is_mutant
        ]
    
        adj_female = int(bool(adjacent_females))
    
        female_has_empty = 0
        for female in adjacent_females:
            if grid.get_adjacent_empty_tiles(female.x, female.y):
                female_has_empty = 1
                break
            
        # Feature vector MUST match training order:
        # [age, mutant, adjacent_adult_female, adjacent_female_has_empty]
        mut = int(bunny.is_mutant)
        vector = [bunny.age, mut, adj_female, female_has_empty]
    
        p_breed = self.male_model.predict_proba([vector])[0][1]
        want_breed = p_breed >= self.threshold
    
        feasible = bool(adj_female and female_has_empty)
        do_breed = want_breed and feasible
        exec_action = "attempted_breeding" if do_breed else "move"
    
        if logger:
            logger.log(
                turn,
                "decision",
                bunny,
                f"age={bunny.age} mutant={mut} adj_female={adj_female} "
                f"female_has_empty={female_has_empty} p_breed={p_breed:.2f} "
                f"want={'breed' if want_breed else 'move'} "
                f"feasible={int(feasible)} exec={exec_action}",
                controller="SL",
            )
    
        if do_breed:
            female = adjacent_females[0]
    
            if logger:
                logger.log(
                    turn,
                    "attempted_breeding",
                    bunny,
                    f"Attempted to breed with female at ({female.x},{female.y})",
                    controller="SL",
                )
        else:
            empty_tiles = grid.get_adjacent_empty_tiles(bunny.x, bunny.y)
    
            if not empty_tiles:
                return
    
            all_females = [
                b for b in grid.bunnies
                if b.sex == "F" and b.is_adult() and not b.is_mutant
            ]
    
            if not all_females:
                self.move_randomly(bunny, grid, logger, turn)
                return
    
           # best_tile = min(
           #     empty_tiles,
           #     key=lambda tile: min(
           #         abs(tile[0] - f.x) + abs(tile[1] - f.y)
           #         for f in all_females
           #     )
           # )
            best_tile = self.choose_safest_target_tile(empty_tiles, all_females, grid)
    
            bunny.move(best_tile[0] - bunny.x, best_tile[1] - bunny.y, grid)
    
            if logger:
                logger.log(
                    turn,
                    "move",
                    bunny,
                    f"Moved to ({bunny.x},{bunny.y})",
                    controller="SL",
                )
            


    def move_towards_male(self, bunny, grid, logger, turn):
        empty_tiles = grid.get_adjacent_empty_tiles(bunny.x, bunny.y)
        if not empty_tiles:
            return  # no move possible  
        
        # Move towards nearest male if any, otherwise move randomly
        all_males = [b for b in grid.bunnies if b.sex == "M" and b.is_adult() and not b.is_mutant]
        if not all_males:
            self.move_randomly(bunny, grid, logger, turn)
            return  
        
        # Find the empty tile that is closest to any male 
        #best_tile = min(empty_tiles, 
        #                key=lambda tile: min(
        #                    abs(tile[0] - m.x) + abs(tile[1] - m.y) 
        #                    for m in  all_males))
        best_tile = self.choose_safest_target_tile(empty_tiles, all_males, grid)

        bunny.move(best_tile[0] - bunny.x, best_tile[1] - bunny.y, grid)
        if logger:
            logger.log(turn, "move", bunny, f"Moved to ({bunny.x},{bunny.y})", controller="SL")


    def move_randomly(self, bunny, grid, logger, turn):
        tiles = grid.get_adjacent_empty_tiles(bunny.x, bunny.y)
        if tiles:
            dx, dy = random.choice(tiles)
            bunny.move(dx - bunny.x, dy - bunny.y, grid)
            if logger:
                logger.log(turn, "move", bunny, f"Moved to ({bunny.x},{bunny.y})", controller="SL")   
    
    def count_adjacent_mutants(self, x, y, grid):
        neighbors = grid.get_adjacent_bunnies(x, y)
        return sum(1 for n in neighbors if n.is_mutant)
    
    def choose_safest_target_tile(self, empty_tiles, targets, grid):
        best_tile = None
        best_score = float("inf")

        for tile in empty_tiles:

            distance = min(
                abs(tile[0] - t.x) + abs(tile[1] - t.y)
                for t in targets
            )

            mutant_count = self.count_adjacent_mutants(
                tile[0],
                tile[1],
                grid
            )

            score = distance + self.mutant_penalty * mutant_count

            if score < best_score:
                best_score = score
                best_tile = tile
            
            # print(
            #     f"tile={tile} "
            #     f"dist={distance} "
            #     f"mutants={mutant_count} "
            #     f"score={score}"
            # )

        return best_tile
        
        