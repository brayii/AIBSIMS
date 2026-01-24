# main.py

import pygame
import time
import random
from core.grid import Grid, SCREEN_WIDTH, SCREEN_HEIGHT
from core.logger import EventLogger
from core.fsm_dispatcher import FSMDispatcher


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Bunny Simulator")

    grid = Grid(screen)
    fsm_dispatcher = FSMDispatcher()
    
    logger = EventLogger()

    font = pygame.font.SysFont(None, 24)
    clock = pygame.time.Clock()

    turn = 0
    fsm_dispatcher.dispatch(None, grid, turn, logger=logger)


    running = True
    while running:
        clock.tick(60)  # max frame rate
        fps = clock.get_fps()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Simulation step every 500ms
        if turn == 0 or pygame.time.get_ticks() % 500 < 20:
            turn += 1     

            # Target: 75% grid occupancy
            target_bunnies_count = int(0.75 * SCREEN_WIDTH * SCREEN_HEIGHT / (32*32))
            bunny_count = len(grid.bunnies)
            if bunny_count <= 0:
                running = False
                continue

            # print(f"Turn {turn}, Bunnies: {len(grid.bunnies)}, Target: {target_bunnies_count}")
            if len(grid.bunnies) > target_bunnies_count:
                # tmp_bunnies = grid.bunnies.copy()
                random.shuffle(grid.bunnies)
                
                # purge half of the excess bunnies
                count =0
                for bunny in grid.bunnies:
                    grid.bunnies.remove(bunny)
                    grid.cells[bunny.y][bunny.x] = None
                    if logger:
                        logger.log(turn, "death", bunny, "Removed due to overpopulation", controller="Main")
                    count +=1
                    if count >= bunny_count/2:
                        break

            for bunny in grid.bunnies:
                fsm_dispatcher.dispatch(bunny, grid, turn, logger=logger)
                bunny.update(grid)

            # Draw grid and bunnies
            grid.update()

            
 

        pygame.display.flip()

    logger.close()
    
    pygame.quit()   

if __name__ == "__main__":
    main()
