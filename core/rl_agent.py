# core/rl_agent.py

import random
from collections import defaultdict
import numpy as np
import pickle
import os

def save_all_agents(agent_dict, path="q_tables/"):
    os.makedirs(path, exist_ok=True)
    for name, agent in agent_dict.items():
        with open(f"{path}{name}.pkl", "wb") as f:
            pickle.dump(agent.q_table, f)

def load_agent_qtable(name, path="q_tables/"):
    file_path = f"{path}{name}.pkl"
    if os.path.exists(file_path):
        try:
            with open(file_path, "rb") as f:
                return pickle.load(f)
        except EOFError:
            print(f"[WARN] Q-table for {name} is empty or corrupted.")
            return None
    else:
        print(f"[INFO] No Q-table found for {name}, starting fresh.")
    return None




class BunnyRLAgent:
    def __init__(self, bunny):
        self.bunny = bunny
        self.q_table = {}
        self.epsilon = 0.1
        self.alpha = 0.2
        self.gamma = 0.95
        self.last_state = None
        self.last_action = None

    def num_actions(self):
        return 5  # 0: N, 1: S, 2: E, 3: W, 4: Do Nothing

    def get_state(self, grid):
        x, y = self.bunny.x, self.bunny.y
        age = self.bunny.age

        adjacent = grid.get_adjacent_bunnies(x, y)
        female_adj = any(b.sex == 'F' and b.is_adult() for b in adjacent)
        male_adj = any(b.sex == 'M' and b.is_adult() for b in adjacent)
        #vampire_near = any(b.is_mutant for b in adjacent)
        vampire_near = grid.is_vampire_in_range(x, y, radius=3)

        heat = int(grid.female_heatmap.data[x][y] > 1.0)
        empty = len(grid.get_adjacent_empty_tiles(x, y)) > 0
        near_edge = int(x == 0 or y == 0 or x == grid.GRID_WIDTH - 1 or y == grid.GRID_HEIGHT - 1)

        if self.bunny.sex == 'F':
            return (age // 4, self.bunny.has_baby, vampire_near, male_adj, empty, near_edge)

        else:  # Male-specific state
            return (age // 4, female_adj, vampire_near, heat, empty)

       
    def choose_action(self, state):
        if state not in self.q_table:
            self.q_table[state] = [0.0] * 5  # Ensure the value is a plain list (no lambda)

        # Epsilon-greedy selection
        if random.random() < self.epsilon:
            return random.randint(0, 4)  # Explore: random action
        return max(range(5), key=lambda a: self.q_table[state][a])  # Exploit: best known action


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

