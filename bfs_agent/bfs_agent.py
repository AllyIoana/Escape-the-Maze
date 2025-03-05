from collections import deque
from base_agent.base_agent import BaseAgent

class BFSAgent(BaseAgent):
    path = []
    visited = []

    def initialize_agent_info(self, response: dict):
        super().initialize_agent_info(response)
        self.path = [self.position]
        self.queue = deque([(self.position, [])])  # Queue for BFS, stores (position, path_so_far)
        self.visited = set()  # Track visited positions
        print(f"Memory initialized: {self.memory}")  # Debugging memory initialization

    def register_move(self, info: dict):
        super().register_move(info)
        self.path.append(self.position)
        if self.position not in self.visited:
            self.visited.add(self.position)

    def move(self):
        # print(f"Starting BFS from position: {self.position}")
        directions = {'N': (-1, 0), 'E': (0, 1), 'S': (1, 0), 'W': (0, -1)}
        deltas = {(-1, 0): 'N', (0, 1): 'E', (1, 0): 'S', (0, -1): 'W'}

        # Perform BFS
        while self.queue:
            current_position, current_path = self.queue.popleft()
            print(f"Exploring position: {current_position}, Path: {current_path}")

            if self.is_goal(current_position):
                print(f"Goal found at: {current_position}")
                return "".join(current_path)  # Return the path to the goal

            for direction, (dx, dy) in directions.items():
                next_position = (current_position[0] + dx, current_position[1] + dy)
                if next_position not in self.visited and self.is_traversable(next_position):
                    self.visited.add(next_position)
                    print(f"Adding position {next_position} to queue.")
                    self.queue.append((next_position, current_path + [deltas[(dx, dy)]]))

        # print("No path found.")
        return ""  # If no path is found

    def is_goal(self, position):
        # Check if the position is the goal (e.g., represented by a specific value in memory)
        is_goal = self.memory.get(position, -1) == 182  # Assuming goal is represented by 182
        if is_goal:
            print(f"Goal found at {position}")
        return is_goal

    def is_traversable(self, position):
        # Check if the position is within bounds and not a wall or obstacle
        value = self.memory.get(position, -1)
        print(f"Checking if position {position} is traversable. Value: {value}")
        return value !=  -1 and value != 0 # Assuming 255 represents a traversable path
