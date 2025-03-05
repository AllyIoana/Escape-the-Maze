from collections import deque
import random

# Possible moves
MOVES = ['N', 'E', 'S', 'W']

class BiDirectionalAgent:
    def __init__(self, goal):
        """
        Initializes the bi-directional search agent with a starting position and goal.
        :param goal: The goal position (x, y) in the maze.
        """
        self.moves = 10  # Start with 10 moves
        self.position = (0, 0)  # Start position at (0, 0)
        self.goal = goal  # Goal position (x, y)
        self.forward_queue = deque([self.position])  # Forward search queue
        self.backward_queue = deque([self.goal])  # Backward search queue
        self.forward_visited = set([self.position])  # Visited nodes for forward search
        self.backward_visited = set([self.goal])  # Visited nodes for backward search
        self.path_found = False  # Flag to indicate if a path is found

    def recv_info(self, response):
        """
        Processes the server's response to calculate the number of moves allowed in the next command
        and updates the agent's position based on successful moves.
        :param response: The server's JSON response containing move results.
        """
        failed_moves = 0
        
        for result in response.values():
            if result["successful"] is False:
                failed_moves += 1
            else:
                # Update position based on successful moves
                self.update_position(result["name"])
        
        # Update the moves for the next set of commands
        self.moves = 10 - failed_moves
        print(f"Next move allowance: {self.moves} moves")
        print(f"Current position: {self.position}")

    def update_position(self, direction):
        """
        Updates the agent's position based on the direction of a successful move.
        :param direction: The direction of the move ('N', 'E', 'S', 'W').
        """
        x, y = self.position
        if direction == 'N':
            self.position = (x, y + 1)  # Move North (increase y)
        elif direction == 'S':
            self.position = (x, y - 1)  # Move South (decrease y)
        elif direction == 'E':
            self.position = (x + 1, y)  # Move East (increase x)
        elif direction == 'W':
            self.position = (x - 1, y)  # Move West (decrease x)

    def move(self):
        """
        Generates a list of moves using bi-directional search logic based on the current move allowance.
        Ensures the number of generated moves does not exceed the current move allowance (self.moves).
        :return: A string representing the generated moves.
        """
        moves = []
        move_count = 0  # Track the number of moves generated
    
        while move_count < self.moves:
            if not self.forward_queue and not self.backward_queue:
                break  # No more moves to generate
            
            if self.forward_queue and not self.path_found:
                current = self.forward_queue.popleft()
                for direction, neighbor in self.get_neighbors(current).items():
                    if neighbor not in self.forward_visited:
                        self.forward_visited.add(neighbor)
                        self.forward_queue.append(neighbor)
                        moves.append(direction)
                        move_count += 1
                        if move_count >= self.moves:  # Stop if move limit is reached
                            break
                        if neighbor in self.backward_visited:
                            self.path_found = True
                            break
                        
            if self.backward_queue and not self.path_found:
                current = self.backward_queue.popleft()
                for direction, neighbor in self.get_neighbors(current).items():
                    if neighbor not in self.backward_visited:
                        self.backward_visited.add(neighbor)
                        self.backward_queue.append(neighbor)
                        if neighbor in self.forward_visited:
                            self.path_found = True
                            break
                        
            if self.path_found:
                print("Path found between start and goal!")
                break
            
        print(f"Generated moves: {''.join(moves)}")
        return ''.join(moves)  # Return moves as a single string



    def get_neighbors(self, position):
        """
        Gets neighbors of the current position.
        :param position: The current position (x, y).
        :return: A dictionary of neighbors with directions as keys.
        """
        x, y = position
        return {
            'N': (x, y + 1),
            'S': (x, y - 1),
            'E': (x + 1, y),
            'W': (x - 1, y)
        }

# Example Usage
if __name__ == "__main__":
    goal_position = (5, 5)  # Example goal
    agent = BiDirectionalAgent(goal=goal_position)
    
    # Simulating server responses for demonstration purposes
    for _ in range(5):  # Run 5 moves as a demo
        generated_moves = agent.move()
        # Example of a simulated response with random success/fail results (true or false)
        simulated_response = {
            f"command{i+1}": {"name": move, "successful": random.choice([True, False]), "view": ""}
            for i, move in enumerate(generated_moves)
        }
        print(f"Simulated response: {simulated_response}")
        
        # Process the simulated response
        agent.recv_info(simulated_response)
