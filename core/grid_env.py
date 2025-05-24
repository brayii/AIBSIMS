# core/grid_env.py

import gym
from gym import spaces
import numpy as np

class BunnyEnv(gym.Env):
    def __init__(self, grid_size=80):
        super().__init__()
        self.grid_size = grid_size
        self.observation_space = spaces.Box(low=0, high=5, shape=(grid_size, grid_size), dtype=np.int8)
        self.action_space = spaces.Discrete(5)  # 0=Stay, 1=Up, 2=Down, 3=Left, 4=Right

    def reset(self):
        # Reset simulation state
        return self._get_observation()

    def step(self, action):
        # Apply action to an agent
        reward = 0
        done = False
        info = {}
        return self._get_observation(), reward, done, info

    def _get_observation(self):
        # Return grid state as matrix of encoded bunny types
        obs = np.zeros((self.grid_size, self.grid_size), dtype=np.int8)
        # Example: 0=empty, 1=juvenile, 2=male, 3=female, 4=mutant
        return obs

