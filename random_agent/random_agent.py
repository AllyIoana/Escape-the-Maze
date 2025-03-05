from base_agent.base_agent import BaseAgent
import random

class RandomAgent(BaseAgent):
    def move(self):
        # Generate the moves the agent makes
        return "".join([random.choice(["N", "E", "S", "W"]) for _ in range(self.moves)])
