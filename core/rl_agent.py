# core/rl_agent.py

import os
import pickle
import random
from collections import deque

import torch
import torch.nn as nn
import torch.optim as optim

def merge_q_tables(old_q, new_q, alpha=0.5):
    merged = old_q.copy()
    for state, new_values in new_q.items():
        if state in merged:
            merged[state] = [
                (1 - alpha) * old + alpha * new
                for old, new in zip(merged[state], new_values)
            ]
        else:
            merged[state] = new_values.copy()
    return merged


def save_all_agents(agent_dict, path="q_tables/", shared=False):
    os.makedirs(path, exist_ok=True)

    for name, agent in agent_dict.items():
        q_table = agent.q_table

        if shared:
            bunny = getattr(agent, "bunny", None)
            if bunny is None:
                btype = "unknown"
            elif bunny.is_mutant:
                btype = "vampire"
            elif not bunny.is_adult():
                btype = "juvenile"
            elif bunny.sex == "M":
                btype = "male"
            else:
                btype = "female"

            if name.startswith("J"):
                btype = "juvenile"

            filename = f"{btype}_shared.pkl"
        else:
            filename = f"{name}.pkl"

        file_path = os.path.join(path, filename)

        if shared and os.path.exists(file_path):
            try:
                with open(file_path, "rb") as f:
                    existing_q = pickle.load(f)
                q_table = merge_q_tables(existing_q, q_table, alpha=0.5)
            except Exception as e:
                print(f"[WARN] Could not merge shared Q-table for {filename}: {e}")

        with open(file_path, "wb") as f:
            pickle.dump(q_table, f)
            print(f"[SAVE] {name} as {btype} ({len(q_table)} states)")


def save_combined_qtables(agent_dict, path="q_tables/all_shared.pkl"):
    combined = {"male": {}, "female": {}, "juvenile": {}, "vampire": {}}

    for agent in agent_dict.values():
        q_table = agent.q_table
        bunny = getattr(agent, "bunny", None)

        if bunny is None:
            continue
        elif bunny.is_mutant:
            role = "vampire"
        elif not bunny.is_adult():
            role = "juvenile"
        elif bunny.sex == "M":
            role = "male"
        else:
            role = "female"

        if hasattr(agent, "last_state") and isinstance(agent.last_state, tuple):
            if agent.last_state[0] == "juvenile":
                role = "juvenile"

        for state, values in q_table.items():
            if state not in combined[role]:
                combined[role][state] = values.copy()
            else:
                combined[role][state] = [
                    (a + b) / 2.0 for a, b in zip(combined[role][state], values)
                ]

    with open(path, "wb") as f:
        pickle.dump(combined, f)

    print(f"[SAVE] Combined Q-tables saved to {path}")


def load_agent_qtable(name, path="q_tables/"):
    file_path = f"{path}{name}.pkl"
    if os.path.exists(file_path):
        try:
            with open(file_path, "rb") as f:
                return pickle.load(f)
        except EOFError:
            print(f"[WARN] Q-table for {name} is empty or corrupted.")
            return None
    return None


class QNet(nn.Module):
    def __init__(self, input_dim, output_dim):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 64),
            nn.ReLU(),
            nn.Linear(64, output_dim)
        )

    def forward(self, x):
        return self.net(x)
    

class BunnyRLAgent:
    def __init__(self, bunny, shared_q_table):
        self.bunny = bunny
        self.q_table = shared_q_table
        self.epsilon = 0.5
        self.alpha = 0.2
        self.epsilon = max(0.05, self.epsilon * 0.995) # Decay epsilon
        self.alpha = max(0.1, self.alpha * 0.997) # Decay alpha
        self.gamma = 0.95
        self.last_state = None
        self.last_action = None

        # --- DQN-specific ---
        self.use_dqn = True
        self.state_dim = 6  # Must match encode_state_vector()
        self.q_net = QNet(self.state_dim, self.num_actions())
        self.target_net = QNet(self.state_dim, self.num_actions())
        self.target_net.load_state_dict(self.q_net.state_dict())
        self.optimizer = optim.Adam(self.q_net.parameters(), lr=1e-3)
        self.loss_fn = nn.MSELoss()
        self.buffer = deque(maxlen=10000)
        self.dqn_batch_size = 64
        self.sync_target_steps = 200
        self.steps = 0

    def num_actions(self):
        return 6  # 0–4: directions, 5: role action

    def encode_state_vector(self, grid):
            x, y = self.bunny.x, self.bunny.y
            age_norm = self.bunny.age / self.bunny.max_age()
            is_mutant = int(self.bunny.is_mutant)
            is_male = int(self.bunny.sex == 'M')
            vampire_near = int(grid.is_vampire_in_range(x, y))
            has_baby = int(getattr(self.bunny, 'has_baby', False))
            nearby = len(grid.get_adjacent_bunnies(x, y)) / 8.0
            return torch.tensor([age_norm, is_mutant, is_male, vampire_near, has_baby, nearby], dtype=torch.float32)
    
    def get_state(self, grid):
        x, y = self.bunny.x, self.bunny.y
        age_bin = min(self.bunny.age // 3, 4)
        adjacent = grid.get_adjacent_bunnies(x, y)
        empty = bool(grid.get_adjacent_empty_tiles(x, y))
        vampire_near = grid.is_vampire_in_range(x, y, radius=3)

        if self.bunny.is_mutant:
            return ('vampire', age_bin, empty, vampire_near)
        elif not self.bunny.is_adult():
            return ('juvenile', age_bin, vampire_near, empty)
        elif self.bunny.sex == 'F':
            male_adj = any(b.sex == 'M' and b.is_adult() for b in adjacent)
            return (
                'female',
                age_bin,
                int(self.bunny.has_baby),
                vampire_near,
                male_adj,
                empty
            )
        else:  # male
            female_adj = any(b.sex == 'F' and b.is_adult() for b in adjacent)
            heat = int(grid.female_heatmap.data[x][y] > 1.0)
            return (
                'male',
                age_bin,
                female_adj,
                vampire_near,
                heat,
                empty
            )

    def choose_action(self, state, grid):
        if not self.use_dqn:
            if state not in self.q_table:
                self.q_table[state] = [0.0] * self.num_actions()
            if random.random() < self.epsilon:
                return random.randint(0, self.num_actions() - 1)
            return max(range(self.num_actions()), key=lambda a: self.q_table[state][a])
        else:
            s_vec = self.encode_state_vector(grid).unsqueeze(0)
            if random.random() < self.epsilon:
                return random.randint(0, self.num_actions() - 1)
            with torch.no_grad():
                return self.q_net(s_vec).argmax().item()
            
    #def choose_action(self, state):
    #    if state not in self.q_table:
    #        self.q_table[state] = [0.0] * self.num_actions()
    #    if random.random() < self.epsilon:
    #        return random.randint(0, self.num_actions() - 1)
    #    return max(range(self.num_actions()), key=lambda a: self.q_table[state][a])

    def update_q(self, s, a, r, s_prime, grid):
        if not self.use_dqn:
            if s not in self.q_table:
                self.q_table[s] = [0.0] * self.num_actions()
            if s_prime not in self.q_table:
                self.q_table[s_prime] = [0.0] * self.num_actions()
            max_future = max(self.q_table[s_prime])
            self.q_table[s][a] += self.alpha * (r + self.gamma * max_future - self.q_table[s][a])
        else:
            s_vec = self.encode_state_vector(grid)
            s_prime_vec = self.encode_state_vector(grid)
            done = 0.0 if self.bunny.age < self.bunny.max_age() else 1.0
            self.buffer.append((s_vec, a, r, s_prime_vec, done))

            self.steps += 1
            if len(self.buffer) >= self.dqn_batch_size:
                self.train_dqn_step()

            if self.steps % self.sync_target_steps == 0:
                self.target_net.load_state_dict(self.q_net.state_dict())

    # def update_q(self, s, a, r, s_prime):
    #     if s not in self.q_table:
    #         self.q_table[s] = [0.0] * self.num_actions()
    #     if s_prime not in self.q_table:
    #         self.q_table[s_prime] = [0.0] * self.num_actions()
# 
    #     max_future = max(self.q_table[s_prime])
    #     self.q_table[s][a] += self.alpha * (r + self.gamma * max_future - self.q_table[s][a])

    def train_dqn_step(self):
        batch = random.sample(self.buffer, self.dqn_batch_size)
        s_batch, a_batch, r_batch, s_prime_batch, done_batch = zip(*batch)

        s_batch = torch.stack(s_batch)
        s_prime_batch = torch.stack(s_prime_batch)
        a_batch = torch.tensor(a_batch)
        r_batch = torch.tensor(r_batch)
        done_batch = torch.tensor(done_batch)

        q_values = self.q_net(s_batch).gather(1, a_batch.unsqueeze(1)).squeeze()
        with torch.no_grad():
            target_q = r_batch + self.gamma * self.target_net(s_prime_batch).max(1)[0] * (1 - done_batch)

        loss = self.loss_fn(q_values, target_q)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

    def act(self, action, grid):
        if action in range(5):
            dx, dy = [(0, -1), (0, 1), (1, 0), (-1, 0), (0, 0)][action]
            nx, ny = self.bunny.x + dx, self.bunny.y + dy
            if 0 <= nx < grid.GRID_WIDTH and 0 <= ny < grid.GRID_HEIGHT and grid.cells[nx][ny] is None:
                grid.move_bunny(self.bunny, nx, ny)
        elif action == 5:
            # print(f"[{self.bunny.sex}] Performing role-specific action")
            if self.bunny.is_mutant:
                self.infect(grid)
            elif not self.bunny.is_adult():
                self.flee_from_vampires(grid)
            elif self.bunny.sex == 'F':
                self.birth(grid)
            elif self.bunny.sex == 'M':
                self.seek_female(grid)

    def seek_female(self, grid):
       
        if grid.female_heatmap.best_tile_value() > 1.0:
            tx, ty = grid.female_heatmap.best_tile()
            grid.move_toward(self.bunny, tx, ty)

    def infect(self, grid):
        neighbors = grid.get_adjacent_bunnies(self.bunny.x, self.bunny.y)
        victims = [b for b in neighbors if not b.is_mutant]
        if victims:
            victim = random.choice(victims)
            victim.is_mutant = True

    def birth(self, grid):
        neighbors = grid.get_adjacent_bunnies(self.bunny.x, self.bunny.y)
        males = [b for b in neighbors if b.sex == 'M' and b.is_adult() and not b.is_mutant]
        empty_tiles = grid.get_adjacent_empty_tiles(self.bunny.x, self.bunny.y)
        if males and empty_tiles:
            nx, ny = random.choice(empty_tiles)
            baby = self.bunny.make_baby(nx, ny, grid=grid)
            grid.place_bunny(baby, nx, ny)
            self.bunny.has_baby = True

    def flee_from_vampires(self, grid):
        threats = [b for b in grid.get_adjacent_bunnies(self.bunny.x, self.bunny.y) if b.is_mutant]
        safe_tiles = grid.get_adjacent_empty_tiles(self.bunny.x, self.bunny.y)
        best_tile = None
        max_dist = -1
        for (tx, ty) in safe_tiles:
            dist = grid.nearest_vampire_distance(tx, ty)
            if dist is not None and dist > max_dist:
                best_tile = (tx, ty)
                max_dist = dist
        if best_tile:
            grid.move_bunny(self.bunny, *best_tile)
        else:
            self.bunny.move_random(grid)

    def step(self, grid, turn, logger, reward_func):
        state = self.encode_state_vector(grid) if self.use_dqn else self.get_state(grid)
        action = self.choose_action(state, grid)
        self.act(action, grid)
        reward = reward_func(self.bunny, grid)
        if self.last_state is not None and self.last_action is not None:
            self.update_q(self.last_state, self.last_action, reward, state, grid)
        self.last_state = state
        self.last_action = action

    # def step(self, grid, turn, logger, reward_func):
    #     state = self.get_state(grid)
    #     action = self.choose_action(state)
    #     self.act(action, grid)
    #     reward = reward_func(self.bunny, grid)
    #     if self.last_state is not None and self.last_action is not None:
    #         self.update_q(self.last_state, self.last_action, reward, state)
    #     self.last_state = state
    #     self.last_action = action
# 
    #     if self.last_state is not None and self.last_action is not None:
    #         self.update_q(self.last_state, self.last_action, reward, state)
    #     
    #         # 🧠 Detect graduation from juvenile to adult
    #         # if self.last_state[0] == "juvenile" and state[0] in ("male", "female"):
    #         #     print(f"[GRADUATED] {self.bunny.name} became {state[0]}")
    #         #     self.save_juvenile_snapshot()

    
    def save_juvenile_snapshot(self, path="q_tables/juvenile_grads.pkl"):
        if not isinstance(self.q_table, dict):
            return
        if len(self.q_table) == 0:
            return

        if os.path.exists(path):
            try:
                with open(path, "rb") as f:
                    combined = pickle.load(f)
            except:
                combined = {}
        else:
            combined = {}

        for state, values in self.q_table.items():
            if state[0] != "juvenile":
                continue
            if state not in combined:
                combined[state] = values.copy()
            else:
                combined[state] = [
                    (a + b) / 2.0 for a, b in zip(combined[state], values)
                ]

        with open(path, "wb") as f:
            pickle.dump(combined, f)
        print(f"[SAVE] Juvenile snapshot saved with {len(combined)} states")

    def get_role_name(self):
        if self.bunny.is_mutant:
            return "vampire"
        elif not self.bunny.is_adult():
            return "juvenile"
        elif self.bunny.sex == "M":
            return "male"
        elif self.bunny.sex == "F":
            return "female"
        return "unknown"


    def save_model(self, base_path="q_tables/"):
        if not self.use_dqn:
            return
        role = self.get_role_name()
        path = os.path.join(base_path, f"{role}_dqn.pt")
        os.makedirs(base_path, exist_ok=True)
        torch.save({
            'q_net_state_dict': self.q_net.state_dict(),
            'target_net_state_dict': self.target_net.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict()
        }, path)
        #print(f"[DQN SAVE] Saved {role} model to {path}")

    def load_model(self, base_path="q_tables/"):
        if not self.use_dqn:
            return
        role = self.get_role_name()
        path = os.path.join(base_path, f"{role}_dqn.pt")
        if not os.path.exists(path):
            print(f"[DQN LOAD] No saved model for {role} at {path}")
            return
        checkpoint = torch.load(path)
        self.q_net.load_state_dict(checkpoint['q_net_state_dict'])
        self.target_net.load_state_dict(checkpoint['target_net_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        #print(f"[DQN LOAD] Loaded {role} model from {path}")



