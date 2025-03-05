import random
from base_agent.base_agent import BaseAgent

class DFSAgent(BaseAgent):
    path = []
    visited = []

    def initialize_agent_info(self, response: dict):
        super().initialize_agent_info(response)
        self.path = [self.position]

    def register_move(self, info: dict):
        super().register_move(info)
        self.path.append(self.position)
        if not self.position in self.visited:
            self.visited.append(self.position)
        else:
            self.path = self.path[:self.path.index(self.position) + 1]

    def move(self):
        # Generate the moves the agent makes
        current_move = 0
        result = []
        backward_result = None
        directions = {'N': (-1, 0), 'E': (0, 1), 'S': (1, 0), 'W': (0, -1)}
        deltas = {(-1, 0): 'N', (0, 1): 'E', (1, 0): 'S', (0, -1): 'W'}
        opposite = {'N': 'S', 'E': 'W', 'S': 'N', 'W': 'E'}
        current_position = self.position
        while current_move < self.moves:
            next_positions = [(current_position[0] + directions[direction][0], current_position[1] + directions[direction][1]) for direction in ['N', 'E', 'S', 'W']]
            found = False
            for next_position in next_positions:
                if next_position in self.memory and self.memory[next_position] == 0:
                    continue
                if next_position not in self.visited:
                    result.append(deltas[(next_position[0] - current_position[0], next_position[1] - current_position[1])])
                    current_position = next_position
                    found = True
                    break
            if not found:
                if result == []:
                    previous_position = self.path[self.path.index(current_position) - 1]
                    if abs(previous_position[0] - current_position[0]) + abs(previous_position[1] - current_position[1]) != 1:
                        for i in range(self.moves):
                            random_direction = ['N', 'E', 'S', 'W']
                            result.append(random.choice(random_direction))
                        return "".join(result)
                    else:
                        result.append(deltas[(previous_position[0] - current_position[0], previous_position[1] - current_position[1])])
                        current_position = previous_position
                else:
                    if backward_result is None:
                        backward_result = result
                    elif backward_result != []:
                        result.append(opposite[backward_result.pop()])
            current_move += 1
        return "".join(result)