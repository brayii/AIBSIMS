# main.py

import pygame
import time
from core.grid import Grid, SCREEN_WIDTH, SCREEN_HEIGHT
from core.fsm_dispatcher import FSMDispatcher
from core.logger import EventLogger
from core.rl_agent import save_all_agents

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Bunny Simulator")

    grid = Grid(screen)
    dispatcher = FSMDispatcher()
    #logger = EventLogger()

    font = pygame.font.SysFont(None, 24)
    clock = pygame.time.Clock()

    turn = 0
    max_population = 0
    total_reward = 0
    reward_history = []

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
            turn_reward = 0
                    
            # Update heatmap before agent logic
            grid.female_heatmap.decay()
            grid.female_heatmap.update_from_sightings(grid.get_all_bunnies())

            total_reward = 0
            bunnies = list(grid.bunnies)  # avoid mutation during loop
            for bunny in bunnies:
                #bunny.update(grid, turn, logger)
                bunny.update(grid, turn, None)
                #dispatcher.update_bunny(bunny, grid, turn, logger)
                reward = dispatcher.update_bunny(bunny, grid, turn, None)
                total_reward += reward    

            avg_reward = total_reward / len(grid.bunnies) if grid.bunnies else 0
    
                
            # Check for extinction
            if len(grid.bunnies) == 0:
                print(f"Simulation ended at turn {turn} — all bunnies are gone.")
                running = False
                break
            
            # Draw grid and bunnies
            grid.update()

            # --- HUD Metrics ---
            total = len(grid.bunnies)
            adults = sum(1 for b in grid.bunnies if b.is_adult())
            mutants = sum(1 for b in grid.bunnies if b.is_mutant)
            max_population = max(max_population, len(grid.bunnies))
            fps_display = f"{fps:.1f}" if fps > 1.0 else "--"

            hud_lines = [
                f"Turn: {turn}",
                f"FPS: {fps_display}",
                f"Bunnies: {total} (Adults: {adults}, Mutants: {mutants})",
                f"Max Population: {max_population}",
                f"Avg Reward: {avg_reward:.2f}",
            ]

            for i, line in enumerate(hud_lines):
                text = font.render(line, True, (255, 255, 255))
                screen.blit(text, (10, 10 + i * 20))

        pygame.display.flip()

    #logger.close()
    pygame.quit()
    save_all_agents(dispatcher.rl_agents,shared=True)
    print("[INFO] RL agents saved.")


if __name__ == "__main__":
    main()
