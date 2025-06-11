import pygame
import time
from core.grid import Grid, SCREEN_WIDTH, SCREEN_HEIGHT
from core.fsm_dispatcher import FSMDispatcher
from core.logger import EventLogger

def count_bunnies(bunnies):
    stats = {"M": 0, "F": 0, "J": 0, "V": 0}
    for b in bunnies:
        if b.is_mutant:
            stats["V"] += 1
        elif not b.is_adult():
            stats["J"] += 1
        elif b.sex == "M":
            stats["M"] += 1
        elif b.sex == "F":
            stats["F"] += 1
    return stats

def run_simulation(turn_limit=50):
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    grid = Grid(screen)
    dispatcher = FSMDispatcher()
    logger = EventLogger("test_log.csv")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)

    turn = 0
    running = True
    while running and turn < turn_limit:
        turn += 1
        bunnies = list(grid.bunnies)
        for bunny in bunnies:
            bunny.update(grid, turn, logger)
            dispatcher.update_bunny(bunny, grid, turn, logger)

        # Draw + overlay
        grid.update()
        stats = count_bunnies(grid.bunnies)
        label = font.render(
            f"Turn {turn} | M: {stats['M']} F: {stats['F']} J: {stats['J']} V: {stats['V']}",
            True, (255, 255, 255)
        )
        screen.blit(label, (10, 10))
        pygame.display.flip()
        clock.tick(2)  # 2 FPS ~ 500ms per step

    logger.close()
    pygame.quit()

if __name__ == "__main__":
    run_simulation()

