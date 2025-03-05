import requests
import numpy as np
from time import sleep

class BaseAgent:
    server_url = "http://localhost:8000"
    uuid: str = ""
    position: tuple = (0, 0)
    maze_width: int = 0
    maze_height: int = 0
    moves: int = 10
    max_moves: int = 10
    xray_points: int = 10
    memory: dict = {}
    friendly: bool = True
    view: np.ndarray = None
    portal_positions: dict = {}
    move_history: list = []
    finished_maze: bool = False
    success: bool = False
    input_mode: int = 0

    def __init__(self, server_url: str):
        # Send the first request to the server to get the uuid
        self.server_url = server_url
        try:
            response = requests.post(self.server_url, json={}).json()
        except requests.exceptions.ConnectionError:
            print("Server is down, closing agent.")
            exit(1)
        self.uuid = response["UUID"]
        self.initialize_agent_info(response)

    def initialize_agent_info(self, response: dict):
        if "x" in response or "y" in response or "width" in response or "height" in response:
            self.friendly = True
            self.position = (int(response["x"]) if "x" in response else 0, int(response["y"]) if "y" in response else 0)
            self.maze_width = int(response["width"]) if "width" in response else 0
            self.maze_height = int(response["height"]) if "height" in response else 0
        else:
            self.friendly = False
            self.position = (0, 0)
            self.maze_width = 0
            self.maze_height = 0
        self.view = self.parse_view_matrix(response["view"])
        self.memory = {}
        self.update_memory(self.position, self.view)
        self.max_moves = int(response["moves"])
        self.moves = self.max_moves
        self.xray_points = 10
        self.portal_positions = {}
        self.finished_maze = False

    def parse_view_matrix(self, view: str):
        view = view.split(";")
        view = [v.replace("[", "").replace("]", "").replace(" ", "").split(",") for v in view]
        view = np.array(view, dtype=int)
        return view
    
    def update_memory(self, position: tuple, view: np.ndarray):
        # Update the memory of the agent
        current_position_view = view.shape[0] // 2, view.shape[1] // 2
        bounds = [(position[0] - current_position_view[0], position[1] - current_position_view[1]),
                  (position[0] + current_position_view[0], position[1] + current_position_view[1])]
        update_queue = [(current_position_view, position)]
        updated_positions = []
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        while len(update_queue) > 0:
            current_position_view, current_position = update_queue.pop(0)
            self.memory[current_position] = view[current_position_view[0], current_position_view[1]]
            updated_positions.append(current_position)
            new_entries = [((current_position_view[0] + direction[0], current_position_view[1] + direction[1]), 
                            (current_position[0] + direction[0], current_position[1] + direction[1])) for direction in directions
                            if (current_position[0] + direction[0], current_position[1] + direction[1]) not in updated_positions]
            update_queue += [entry for entry in new_entries if entry[1][0] >= bounds[0][0] and entry[1][0] <= bounds[1][0] 
                            and entry[1][1] >= bounds[0][1] and entry[1][1] <= bounds[1][1]]

    def send_actions(self, actions: str):
        # Send actions to server
        body = {
            "UUID": self.uuid,
            "input": actions
        }
        try:
            response = requests.post(self.server_url, json=body).json()
        except requests.exceptions.ConnectionError:
            print("Server is down, closing agent.")
            exit(1)
        except requests.exceptions.JSONDecodeError:
            print("Empty or eronated JSON response from server, closing agent.")
            exit(1)
        self.recv_info(response)

    def rebuild_memory_after_portals(self, new_position):
        # The position we find the portal at is not in the array
        # That means that one of the positions corresponding to the portal code is actually this position
        # We need to find the corresponding position and update the memory
        deltas = [(0, 1), (1, 0), (1, 1), (0, -1), (-1, 0), (-1, -1), (1, -1), (-1, 1)]
        current_deltas = {(0, 0)}
        analyzed_deltas = set()
        correct_portal_index = -1
        while len(current_deltas) > 0:
            delta = current_deltas.pop()
            analyzed_deltas.add(delta)
            new_position_delta = (new_position[0] + delta[0], new_position[1] + delta[1])
            portal_1_delta = (self.portal_positions[self.memory[new_position]][0][0] + delta[0], self.portal_positions[self.memory[new_position]][0][1] + delta[1])
            portal_2_delta = (self.portal_positions[self.memory[new_position]][1][0] + delta[0], self.portal_positions[self.memory[new_position]][1][1] + delta[1])
            if new_position_delta not in self.memory:
                continue
            if portal_1_delta in self.memory and self.memory[portal_1_delta] != self.memory[new_position_delta]:
                correct_portal_index = 1
                break
            if portal_2_delta in self.memory and self.memory[portal_2_delta] != self.memory[new_position_delta]:
                correct_portal_index = 0
                break
            current_deltas.update([(delta[0] + d[0], delta[1] + d[1]) for d in deltas if (delta[0] + d[0], delta[1] + d[1]) not in analyzed_deltas])
        if correct_portal_index == -1:
            print("Could not find the correct portal index")
            return new_position, new_position
        correct_portal_pos = self.portal_positions[self.memory[new_position]][correct_portal_index]
        region = None
        delta = None
        result = new_position
        if correct_portal_pos[0] / 10000 < new_position[0] / 10000:
            # We convert the region that's wrong is in to the other region
            region = round(new_position[0] / 10000)
            delta = (correct_portal_pos[0] - new_position[0], correct_portal_pos[1] - new_position[1])
            result = correct_portal_pos
        else:
            region = round(correct_portal_pos[0] / 10000)
            delta = (new_position[0] - correct_portal_pos[0], new_position[1] - correct_portal_pos[1])
            result = new_position
        for key in list(self.portal_positions.keys()):
            for i in range(0, len(self.portal_positions[key])):
                portal_pos = self.portal_positions[key][i]
                # Any other portal in the wrong region will be converted to the other region
                if round(portal_pos[0] / 10000) == region:
                    self.portal_positions[key][i] = (portal_pos[0] + delta[0], portal_pos[1] + delta[1])
        for key in list(self.memory.keys()):
            # Any tile in the wrong region will be converted to the other region
            if round(key[0] / 10000) == region:
                self.memory[(key[0] + delta[0], key[1] + delta[1])] = self.memory[key]
        for i in range(0, len(self.move_history)):
            # Any move in the wrong region will be converted to the other region
            if round(self.move_history[i][0] / 10000) == region:
                self.move_history[i] = (self.move_history[i][0] + delta[0], self.move_history[i][1] + delta[1])
        if result == new_position:
            return result, correct_portal_pos
        return result, new_position

    def register_move(self, info: dict):
        if int(info["successful"]) > 0:
            # The move was successful
            move = info["name"]
            directions = {"N": (-1, 0), "S": (1, 0), "E": (0, 1), "W": (0, -1), "P": (0, 0), "X": (0, 0)}
            new_position = (self.position[0] + directions[move][0], self.position[1] + directions[move][1])
            if new_position in self.memory and self.memory[new_position] not in [255, 64, 182, 32, 224]:
                # It's a trap or x-ray point increment
                if self.memory[new_position] == 90:
                    # We overwrite the information as if nothing happened, it's impossible to know what the trap does
                    self.position = new_position
                    self.view = self.parse_view_matrix(info["view"])
                    self.update_memory(self.position, self.view)
                elif self.memory[new_position] in range(101, 106):
                    # Rewind trap
                    n = self.memory[new_position] - 100
                    self.position = self.move_history[-n]
                    self.view = self.parse_view_matrix(info["view"])
                    self.update_memory(self.position, self.view)
                    self.move_history = self.move_history[:-n]
                    return
                elif self.memory[new_position] in range(106, 111):
                    # Push forward trap
                    n = self.memory[new_position] - 105
                    self.position = (new_position[0] + n * directions[move][0], new_position[1] + n * directions[move][1])
                    self.view = self.parse_view_matrix(info["view"])
                    self.update_memory(self.position, self.view)
                elif self.memory[new_position] in range(111, 116):
                    # Push back trap
                    n = self.memory[new_position] - 110
                    self.position = (new_position[0] - n * directions[move][0], new_position[1] - n * directions[move][1])
                    self.view = self.parse_view_matrix(info["view"])
                    self.update_memory(self.position, self.view)
                elif self.memory[new_position] in range(150, 170):
                    # Portal
                    # Position can't be calculated when jumping in a portal
                    # The position is shifted to position + portal_code * 10000
                    # The portal position pair is saved so this can be reversed
                    if self.memory[new_position] not in self.portal_positions:
                        self.portal_positions[self.memory[new_position]] = []
                    if len(self.portal_positions[self.memory[new_position]]) < 2:
                        other_position = (new_position[0] + self.memory[new_position] * 10000, new_position[1] + self.memory[new_position] * 10000)
                        self.portal_positions[self.memory[new_position]] = [new_position, other_position]
                        self.memory[other_position] = self.memory[new_position]
                    if move != "P":
                        # We moved on the portal, not through it
                        self.position = new_position
                        self.view = self.parse_view_matrix(info["view"])
                        self.update_memory(self.position, self.view)
                    else:
                        # The position of the other portal is saved in the memory
                        # The agent is moved to the other portal position
                        if new_position in self.portal_positions[self.memory[new_position]]:
                            self.position = self.portal_positions[self.memory[new_position]][0] if self.portal_positions[self.memory[new_position]][0] != new_position \
                                            else self.portal_positions[self.memory[new_position]][1]
                            self.view = self.parse_view_matrix(info["view"])
                            self.update_memory(self.position, self.view)
                        else:
                            new_position, _ = self.rebuild_memory_after_portals(new_position)
                        self.position = self.portal_positions[self.memory[new_position]][0] if self.portal_positions[self.memory[new_position]][0] != new_position \
                                            else self.portal_positions[self.memory[new_position]][1]
                        self.view = self.parse_view_matrix(info["view"])
                        self.update_memory(self.position, self.view)
                elif self.memory[new_position] == 16:
                    # X-ray point
                    self.position = new_position
                    self.view = self.parse_view_matrix(info["view"])
                    self.update_memory(self.position, self.view)
                    self.xray_points += 1
                else:
                    # Whatever other code we treat as normal movement, though this should never happen
                    self.position = new_position
                    self.view = self.parse_view_matrix(info["view"])
                    self.update_memory(self.position, self.view)
            else:
                # Normal movement
                self.position = new_position
                self.view = self.parse_view_matrix(info["view"])
                self.update_memory(self.position, self.view)
            # Save the move in the move history
            self.move_history.append(self.position)
        
    def recv_info(self, response: dict):
        if "end" in response:
            # The agent finished the maze successfully or unsuccessfully
            self.finished_maze = True
            self.success = int(response["end"]) > 0
            return

        # Receive information from server, call from send_actions to get the updated state
        info = list(response.items())
        info = sorted(info, key=lambda x: -1 if x[0] == "moves" else int(x[0].replace("command_", "")))

        for i in range(len(info)):
            (key, value) = info[i]
            if key == "moves":
                self.moves = int(response["moves"])
            else:
                self.register_move(value)
                    

    def get_info(self):
        # Returns relevant information about the agent
        return {
            "uuid": self.uuid,
            "position": self.position,
            "maze_width": self.maze_width,
            "maze_height": self.maze_height,
            "moves": self.moves,
            "max_moves": self.max_moves,
            "xray_points": self.xray_points,
            "memory": self.memory,
            "friendly": self.friendly,
            "view": self.view,
            "portal_positions": self.portal_positions
        }
    
    def solve(self):
        # Solve the maze
        while True:
            if self.finished_maze:
                print("finished")
                sleep(1)
                try:
                    response = requests.post(self.server_url, json={"UUID": self.uuid})
                    if "view" in response.json():
                        self.initialize_agent_info(response.json())
                except requests.exceptions.ConnectionError:
                    print("Server is down, closing agent.")
                    exit(1)
                except requests.exceptions.JSONDecodeError:
                    continue
                    # print("Empty or eronated JSON response from server")
            else:
                actions = self.move()
                self.send_actions(actions)

    def move(self):
        # Generate the moves the agent makes
        # Override this function to implement your own agent
        raise NotImplementedError
    
    def train(self):
        # Train the agent, override this function to implement your own training
        raise NotImplementedError