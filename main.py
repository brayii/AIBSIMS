# main.py
from core.grid import Grid
from core.logger import EventLogger
from core.fsm_dispatcher import FSMDispatcher

turn = 0
logger = EventLogger()
grid = Grid()
dispatcher = FSMDispatcher()
dispatcher.mode = "HYBRID"  # FSM, RL, HYBRID

try:
    while True:
        print(f"\n=== Turn {turn} ===")
        for bunny in grid.bunnies[:]:
            dispatcher.update_bunny(bunny, grid, turn, logger)

        grid.display()
        turn += 1
        input("[ENTER] Next turn...")

except KeyboardInterrupt:
    print("\nSimulation ended.")
finally:
    logger.close()
S