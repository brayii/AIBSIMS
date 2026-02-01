# core/fsm_dispatcher.py

import random
from core import grid, logger
from core import bunny
from core.bunny import Bunny
from core.grid import GRID_WIDTH, GRID_HEIGHT


class FSMDispatcher:
    def __init__(self):
        pass

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
                    logger.log(turn, "birth", bunny1, f"Spawned at ({x},{y})", controller="FSM")
                bunny2 = Bunny(sex=s2, x=x+1, y=y, color=c2)
                grid.place_bunny(bunny2, x+1, y)
                if logger:
                    logger.log(turn, "birth", bunny2, f"Spawned at ({x+1},{y})", controller="FSM")

            if grid.is_empty(x+1, y+1): 
                bunny3 = Bunny(sex=random.choice(['M', 'F']), x=x+1, y=y+1)
                grid.place_bunny(bunny3, x+1, y+1)
                if logger:
                    logger.log(turn, "birth", bunny3, f"Spawned at ({x+1},{y+1})", controller="FSM")
            else:
                pass            
            
            return     
        
        if bunny.bunny_death(grid):
            if logger:
                logger.log(turn, "death", bunny, "Died of old age", controller="FSM")
            return
        
        if bunny.is_mutant:
            self.mutant_behavior(bunny, grid, turn, logger) 
        elif not bunny.is_adult():
            self.juvenile_behavior(bunny, grid, turn, logger)
        elif bunny.sex == 'F':
            self.female_behavior(bunny, grid, turn, logger)
        else:
            self.male_behavior(bunny, grid, turn, logger)

    
    def female_behavior(self, bunny, grid, turn, logger=None):
        # Placeholder for female behavior logic
        # ['breeded', 'move', 'rest']
        #state = 'rest'
        if bunny.is_mutant and not bunny.is_adult():
            return     
        
        neighbors = grid.get_adjacent_bunnies(bunny.x, bunny.y)
        # print(f"Bunny at ({bunny.x},{bunny.y}) has {len(neighbors)} adjacent bunnies.") 
        male = [m for m in neighbors if m.sex == 'M'and m.is_adult() and not bunny.is_mutant]
        if len(neighbors) == 0 or not male or bunny.is_mutant:
            empty_tiles = grid.get_adjacent_empty_tiles(bunny.x, bunny.y)
            if empty_tiles:
                self.move_randomly(bunny, grid, logger, turn)
                # print(f"Bunny at ({bunny.x},{bunny.y}) moving to empty tile.")
                # dx, dy = random.choice(empty_tiles)
                # bunny.move(dx - bunny.x, dy - bunny.y, grid)
                # if logger:
                #     logger.log(turn, "move", bunny, f"Moved to ({bunny.x},{bunny.y})", controller="FSM")
                return
          
        for neighbor in neighbors:
            if neighbor.sex == 'M' and neighbor.is_adult() and not bunny.is_mutant:
                # print(f"Adjacent bunny at ({neighbor.x},{neighbor.y})")
                baby_posistions = grid.get_adjacent_empty_tiles(bunny.x, bunny.y)
                if baby_posistions:
                    x, y = random.choice(baby_posistions)
                    if logger:
                        logger.log(turn, "breeding", bunny, f"Bred with male at ({neighbor.x},{neighbor.y})", controller="FSM")
                    grid.place_bunny(bunny.make_baby(bunny.color, x, y), x, y)
                else:
                    if logger:
                        logger.log(turn, "breeding_failed", bunny, f"No space to place baby despite mate at ({neighbor.x},{neighbor.y})")

                return
           
            else:
                pass

        return

            
    def male_behavior(self, bunny, grid, turn, logger=None):
        # Placeholder for male behavior logic
        if bunny.is_mutant and not bunny.is_adult():
            return        
     
        
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        #direction = random.shuffle(directions)
        empty_tiles = grid.get_adjacent_empty_tiles(bunny.x, bunny.y)
        if empty_tiles:
            self.move_randomly(bunny, grid, logger, turn)
            return
            # print(f"Bunny at ({bunny.x},{bunny.y}) moving to empty tile.")
            # dx, dy = random.choice(empty_tiles)
            # bunny.move(dx - bunny.x, dy - bunny.y, grid)
            # if logger:
            #     logger.log(turn, "move", bunny, f"Moved to ({bunny.x},{bunny.y})", controller="FSM")
        else:
            pass


    def juvenile_behavior(self, bunny, grid, turn, logger=None):
        # Placeholder for juvenile behavior logic
        if bunny.is_mutant and bunny.is_adult():
            return
        
        empty_tiles = grid.get_adjacent_empty_tiles(bunny.x, bunny.y)
        if empty_tiles:
            self.move_randomly(bunny, grid, logger, turn)
            # print(f"Bunny at ({bunny.x},{bunny.y}) moving to empty tile.")
            # dx, dy = random.choice(empty_tiles)
            # bunny.move(dx - bunny.x, dy - bunny.y, grid)
            # if logger:
            #     logger.log(turn, "move", bunny, f"Moved to ({bunny.x},{bunny.y})", controller="FSM")    


    def mutant_behavior(self, bunny, grid, turn, logger=None):
        # Placeholder for mutant behavior logic     
        neighbors = grid.get_adjacent_bunnies(bunny.x, bunny.y)

        if len(neighbors) == 0 or bunny.is_mutant:
            empty_tiles = grid.get_adjacent_empty_tiles(bunny.x, bunny.y)
            if empty_tiles:
                self.move_randomly(bunny, grid, logger, turn)
                # print(f"Bunny at ({bunny.x},{bunny.y}) moving to empty tile.")
                # dx, dy = random.choice(empty_tiles)
                # bunny.move(dx - bunny.x, dy - bunny.y, grid)
                # if logger:
                #     logger.log(turn, "move", bunny, f"Moved to ({bunny.x},{bunny.y})", controller="FSM")
        
        for neighbor in neighbors:
            if not neighbor.is_mutant:
                # print(f"Mutant bunny at ({bunny.x},{bunny.y}) infecting bunny at ({neighbor.x},{neighbor.y})")
                neighbor.is_mutant = True
                neighbor.color = (255, 0, 0)  # change color to red
                if logger:
                    logger.log(turn, "infection", neighbor, "Infected by mutant bunny", controller="FSM")
                return
            
    def move_randomly(self, bunny, grid, logger, turn):
        tiles = grid.get_adjacent_empty_tiles(bunny.x, bunny.y)
        if tiles:
            dx, dy = random.choice(tiles)
            bunny.move(dx - bunny.x, dy - bunny.y, grid)
            if logger:
                logger.log(turn, "move", bunny, f"Moved to ({bunny.x},{bunny.y})", controller="FSM")