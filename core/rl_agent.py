# core/rl_agent.py

import random

class RLAgent:
    def __init__(self):
        # Later: load a trained model here
        pass

    def act(self, observation):
        """
        Decide what action to take given an observation.
        This is a placeholder (random action).
        """
        return random.choice(["stay", "up", "down", "left", "right"])

