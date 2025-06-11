# main.py

import pygame
import time
from core.grid import Grid, SCREEN_WIDTH, SCREEN_HEIGHT
from core.fsm_dispatcher import FSMDispatcher
from core.logger import EventLogger

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Bunny Simulator")

    grid = Grid(screen)
    dispatcher = FSMDispatcher()
    logger = EventLogger()

    font = pygame.font.SysFont(None, 24)
    clock = pygame.time.Clock()

    turn = 0
    running = True
    while running:
        clock.tick(60)  # max frame rate

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Simulation step every 500ms
        if turn == 0 or pygame.time.get_ticks() % 500 < 20:
            turn += 1

            bunnies = list(grid.bunnies)  # avoid mutation during loop
            for bunny in bunnies:
                bunny.update(grid, turn, logger)
                dispatcher.update_bunny(bunny, grid, turn, logger)

            # Draw grid and bunnies
            grid.update()

            # HUD: Turn count and population
            info = font.render(f"Turn: {turn}  Population: {len(grid.bunnies)}", True, (255, 255, 255))
            screen.blit(info, (10, 10))
            pygame.display.flip()

    logger.close()
    pygame.quit()

if __name__ == "__main__":
    main()
