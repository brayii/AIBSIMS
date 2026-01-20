# core/fsm_dispatcher.py

import random


class FSMDispatcher:
    def __init__(self):
        pass

    def dispatch(self, bunny, grid, turn, logger=None):
        # Placeholder for FSM logic
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
            bunny.move(random.choice([-1, 1, 0]), random.choice([-1, 1, 0]), grid)
            return
          
        for neighbor in neighbors:
            if neighbor.sex == 'M' and neighbor.is_adult() and not bunny.is_mutant:
                # print(f"Adjacent bunny at ({neighbor.x},{neighbor.y})")
                baby_posistions = grid.get_adjacent_empty_tiles(bunny.x, bunny.y)
                if baby_posistions:
                    x, y = random.choice(baby_posistions)
                    grid.place_bunny(bunny.make_baby(bunny.color, x, y), x, y)
                return
                # print(f"Adjacent empty tiles: {baby_posistions}")
                # pos = random.choice(baby_posistions) if baby_posistions else None
                # print(f"Chosen position for baby: {pos}")
                # grid.place_bunny(bunny.make_baby(bunny.color, pos[0], pos[1]), pos[0], pos[1]) if pos else None
                # state = 'breeded'
                # break
            else:
                pass
        
        # empty_tiles = grid.get_adjacent_empty_tiles(bunny.x, bunny.y)
        # if empty_tiles:
        #     print(f"Bunny at ({bunny.x},{bunny.y}) moving to empty tile.")
        #     dx, dy = random.choice(empty_tiles)
        #     bunny.move(dx - bunny.x, dy - bunny.y, grid)
        # else:
        #     pass

        return
        # if state != 'breeded' and empty_tiles:
        #     state = 'move'
# 
        # if state == 'rest':
        #     return
        # elif state == 'move':
        #     directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        #     direction = random.shuffle(directions)
        #     # print(directions)
        #     for dx, dy in directions:
        #         if bunny.move(dx, dy, grid):
        #             break
        # elif state == 'breeded':
        #     baby_posistions = grid.get_adjacent_empty_tiles(bunny.x, bunny.y)
        #     pos = random.choice(baby_posistions) if baby_posistions else None
        #     grid.place_bunny(bunny.make_baby(bunny.color, pos[0], pos[1]), pos[0], pos[1]) if pos else None
        # else:
        #     pass
            
    def male_behavior(self, bunny, grid, turn, logger=None):
        # Placeholder for male behavior logic
        if bunny.is_mutant and not bunny.is_adult():
            return
        
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        #direction = random.shuffle(directions)
        empty_tiles = grid.get_adjacent_empty_tiles(bunny.x, bunny.y)
        if empty_tiles:
            # print(f"Bunny at ({bunny.x},{bunny.y}) moving to empty tile.")
            dx, dy = random.choice(empty_tiles)
            bunny.move(dx - bunny.x, dy - bunny.y, grid)
        else:
            pass
        # print(directions)
        # for dx, dy in directions:
        #     if bunny.move(dx, dy, grid):
        #         break

    def juvenile_behavior(self, bunny, grid, turn, logger=None):
        # Placeholder for juvenile behavior logic
        if bunny.is_mutant and bunny.is_adult():
            return
        
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        direction = random.shuffle(directions)
        # print(directions)
        for dx, dy in directions:
            if bunny.move(dx, dy, grid):
                break  


    def mutant_behavior(self, bunny, grid, turn, logger=None):
        # Placeholder for mutant behavior logic
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        # print(directions)
        for dx, dy in directions:
            if bunny.move(dx, dy, grid):
                break  