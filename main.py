# main.py
import pygame
import sys
from core.grid import Grid
from core.logger import EventLogger
from core.fsm_dispatcher import FSMDispatcher

TURN_INTERVAL_MS = 500  # Advance every 0.5 seconds

def main():
    pygame.init()
    screen = pygame.display.set_mode((640, 480))  # Adjust to grid dimensions if needed
    pygame.display.set_caption("Bunny Simulator")
    clock = pygame.time.Clock()

    turn = 0
    logger = EventLogger()
    grid = Grid(screen)
    dispatcher = FSMDispatcher()
    dispatcher.mode = "HYBRID"  # FSM, RL, HYBRID

    pygame.time.set_timer(pygame.USEREVENT, TURN_INTERVAL_MS)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.USEREVENT:
                print(f"=== Turn {turn} ===")
                for bunny in grid.bunnies[:]:  # Make sure grid.bunnies is populated
                    dispatcher.update_bunny(bunny, grid, turn, logger)
                turn += 1

        grid.update()  # Redraw grid + entities
        clock.tick(60)

    logger.close()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
