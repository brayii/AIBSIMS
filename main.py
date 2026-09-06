# main.py

import pygame
import time
import random
import os
from core.grid import Grid, SCREEN_WIDTH, SCREEN_HEIGHT
from core.logger import EventLogger
from core.fsm_dispatcher import FSMDispatcher
from core.sl_dispatcher import SLDispatcher

# Available controllers are FSM and SL.
MODE = "SL"


def create_dispatcher(mode):
    if mode == "FSM":
        return FSMDispatcher()
    if mode == "SL":
        try:
            return SLDispatcher()
        except FileNotFoundError as error:
            print(f"{error}\nFalling back to FSM mode.")
            return FSMDispatcher()
    raise ValueError("Invalid MODE. Choose 'FSM' or 'SL'.")

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Bunny Simulator")

    grid = Grid(screen)
    
    dispatcher = create_dispatcher(MODE)
    
    logger = EventLogger()

    font = pygame.font.SysFont(None, 24)
    clock = pygame.time.Clock()
    simulation_interval_ms = 500
    last_simulation_tick = pygame.time.get_ticks() - simulation_interval_ms

    turn = 0
    max_population = 0
    dispatcher.dispatch(None, grid, turn, logger=logger)

    # save log file if bunny reaches a min
    bunny_count_min = 30
    count_min = False


    running = True
    while running:
        clock.tick(60)  # max frame rate
        fps = clock.get_fps()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Run at most one simulation step per interval, even after a slow frame.
        current_tick = pygame.time.get_ticks()
        if current_tick - last_simulation_tick >= simulation_interval_ms:
            last_simulation_tick = current_tick
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
                for bunny in list(grid.bunnies):
                    grid.bunnies.remove(bunny)
                    grid.cells[bunny.y][bunny.x] = None
                    if logger:
                        logger.log(turn, "death", bunny, "Removed due to overpopulation", controller="Main")
                    count +=1
                    if count >= bunny_count/2:
                        break

            for bunny in list(grid.bunnies):
                dispatcher.dispatch(bunny, grid, turn, logger=logger)
                bunny.update(grid)

            # Draw grid and bunnies
            grid.update()

            if len(grid.bunnies) >= bunny_count_min:
                count_min = True    
            
            # --- HUD Metrics ---
            adults = sum(1 for b in grid.bunnies if b.is_adult())
            mutants = sum(1 for b in grid.bunnies if b.is_mutant)
            max_population = max(max_population, len(grid.bunnies))
            fps_display = f"{fps:.1f}" if fps > 1.0 else "--"

            hud = [
                f"Turn: {turn}",
                f"FPS: {fps_display}",
                f"Bunnies: {len(grid.bunnies)} (Adults: {adults}, Mutants: {mutants})",
                f"Max Population: {max_population}",
                f"FPS: {fps_display}"
            ]

            for i, line in enumerate(hud):
                text = font.render(line, True, (255, 255, 255))
                screen.blit(text, (10, 10 + i * 20))

        pygame.display.flip()

    logger.close()
    # if not count_min:
    #     # remove file
    #     file_path = str(logger.path)       
# 
    #     # Check if file exists before deleting
    #     if os.path.exists(file_path):
    #         os.remove(file_path)
    #         print(f"{file_path} deleted successfully.")
    #     else:
    #         print("The file does not exist.")
                
    
    pygame.quit()   

if __name__ == "__main__":
    main()
