import random

# Possible moves
MOVES = ['N', 'E', 'S', 'W']

class RandomAgent:
    def __init__(self):
        """
        Initializes the random agent with a starting move count of 10.
        """
        self.moves = 10  # Start with 10 moves
        self.position = (0, 0)  # Start position at (0, 0)

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
        Generates a list of random moves based on the current moves allowed.
        :return: A string representing the generated moves.
        """
        # Generate random moves based on the current moves allowed
        moves = [random.choice(MOVES) for _ in range(self.moves)]
        print(f"Generated moves: {''.join(moves)}")
        return "".join(moves)  # Return moves as a single string

# Example Usage
if __name__ == "__main__":
    agent = RandomAgent()
    
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
