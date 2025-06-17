# core/rl_agent.py

import random
from collections import defaultdict
import numpy as np



class BunnyRLAgent:
    def __init__(self, bunny):
        self.bunny = bunny
        self.q_table = defaultdict(lambda: [0.0] * self.num_actions())
        self.epsilon = 0.1
        self.alpha = 0.2
        self.gamma = 0.95
        self.last_state = None
        self.last_action = None

    def num_actions(self):
        return 5  # 0: N, 1: S, 2: E, 3: W, 4: Do Nothing

    def get_state(self, grid):
        x, y = self.bunny.x, self.bunny.y
        age_group = 0 if self.bunny.age < 2 else 1 if self.bunny.age < 8 else 2

        adj = grid.get_adjacent_bunnies(x, y)
        num_males = sum(1 for b in adj if b.sex == 'M' and not b.is_mutant)
        num_females = sum(1 for b in adj if b.sex == 'F' and not b.is_mutant)
        num_vampires = sum(1 for b in adj if b.is_mutant)
        is_near_edge = int(x == 0 or y == 0 or x == grid.GRID_WIDTH - 1 or y == grid.GRID_HEIGHT - 1)

        return (age_group, num_males, num_females, num_vampires, is_near_edge)

    def choose_action(self, state):
        if random.random() < self.epsilon:
            return random.randint(0, self.num_actions() - 1)
        return int(np.argmax(self.q_table[state]))

    def update_q(self, s, a, r, s_prime):
        max_future = max(self.q_table[s_prime])
        self.q_table[s][a] += self.alpha * (r + self.gamma * max_future - self.q_table[s][a])

    def act(self, action, grid):
        dxdy = [(0, -1), (0, 1), (1, 0), (-1, 0), (0, 0)]  # N, S, E, W, Do Nothing
        dx, dy = dxdy[action]
        nx, ny = self.bunny.x + dx, self.bunny.y + dy

        if 0 <= nx < grid.GRID_WIDTH and 0 <= ny < grid.GRID_HEIGHT and grid.cells[nx][ny] is None:
            grid.move_bunny(self.bunny, nx, ny)

    def step(self, grid, turn, logger, reward_func):
        state = self.get_state(grid)
        action = self.choose_action(state)
        self.act(action, grid)

        reward = reward_func(self.bunny, grid)

        if self.last_state is not None and self.last_action is not None:
            self.update_q(self.last_state, self.last_action, reward, state)

        self.last_state = state
        self.last_action = action

