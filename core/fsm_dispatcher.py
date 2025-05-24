# core/fsm_dispatcher.py

from core.rl_agent import RLAgent

class FSMDispatcher:
    def __init__(self):
        self.mode = "FSM"  # Options: FSM, RL, HYBRID
        self.rl_agent = RLAgent()

    def update_bunny(self, bunny, grid, turn, logger):
        if self.mode == "FSM":
            bunny.update(grid, turn, logger)
        elif self.mode == "RL":
            self.update_via_policy(bunny, grid, turn, logger)
        elif self.mode == "HYBRID":
            if getattr(bunny, "use_rl", False):
                self.update_via_policy(bunny, grid, turn, logger)
            else:
                bunny.update(grid, turn, logger)

    def update_via_policy(self, bunny, grid, turn, logger):
        observation = {
            "bunny": bunny,
            "neighbors": grid.get_adjacent_bunnies(bunny.x, bunny.y)
        }
        action = self.rl_agent.act(observation)
        move_map = {
            "stay": (0, 0), "up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)
        }
        dx, dy = move_map.get(action, (0, 0))
        nx, ny = bunny.x + dx, bunny.y + dy
        if grid.is_in_bounds(nx, ny) and grid.grid[ny][nx] is None:
            grid.move_bunny(bunny, nx, ny)
            logger.log(turn, "move", bunny, f"RL action: {action}", controller="RL")
