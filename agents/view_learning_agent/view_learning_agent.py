from base_agent.base_agent import BaseAgent
import pickle
import os
import shutil
import requests
from PIL import Image
import numpy as np
import random

class ViewLearningAgent(BaseAgent):
    view_map: dict = {}
    view_map_current_path: dict = {}
    explored_cells: set = set()
    reachable_cells: set = set()

    def __init__(self, server_url: str, mode="train"):
        if mode != "train":
            super().__init__(server_url)
        else:
            self.server_url = server_url
        try:
            with open('./view_learning_agent/learned_data.pkl', 'rb') as f:
                self.view_map = pickle.load(f)
                # for key in self.view_map:
                #     self.view_map_current_path[key] = 0
        except:
            print("No learning data found")
            self.view_map = {}
    
    def initialize_agent_info(self, response):
        self.explored_cells = set()
        self.reachable_cells = set()
        return super().initialize_agent_info(response)

    def update_memory(self, position, view):
        super().update_memory(position, view)
        if position not in self.explored_cells:
            self.explored_cells.add(position)
            if position not in self.memory:
                return
            if position in self.reachable_cells:
                self.reachable_cells.remove(position)
            directions = {"N": (-1, 0), "E": (0, 1), "S": (1, 0), "W": (0, -1)}
            for d in directions:
                neighbor = (position[0] + directions[d][0], position[1] + directions[d][1])
                if neighbor in self.memory and self.memory[neighbor] != 0 and self.memory[neighbor] not in range(101, 116) and neighbor not in self.explored_cells:
                    self.reachable_cells.add(neighbor)
            if self.memory[position] in range(150, 170):
                if len(self.portal_positions[self.memory[position]]) < 2:
                    other_portal = (self.position[0] + self.memory[self.position] * 10000, self.position[1] + self.memory[self.position] * 10000)
                    self.portal_positions[self.memory[position]] = [position, other_portal]
                    if other_portal not in self.explored_cells:
                        self.reachable_cells.add(other_portal)
                else:
                    other_portal = self.portal_positions[self.memory[position]][0] \
                        if self.portal_positions[self.memory[position]][0] != position \
                        else self.portal_positions[self.memory[position]][1]
                    if other_portal not in self.explored_cells:
                        self.reachable_cells.add(other_portal)
        else:
            super().update_memory(position, view)

    def rebuild_memory_after_portals(self, new_position):
        rebuilt_position, other_position = super().rebuild_memory_after_portals(new_position)
        if rebuilt_position == other_position:
            return rebuilt_position
        
        region = round(other_position[0] / 10000)
        delta = (rebuilt_position[0] - other_position[0], rebuilt_position[1] - other_position[1])
        self.explored_cells = {(exp[0] + delta[0], exp[1] + delta[1]) for exp in self.explored_cells if round(exp[0] / 10000) == region}
        self.explored_cells.update({exp for exp in self.explored_cells if round(exp[0] / 10000) != region})
        self.reachable_cells = {(exp[0] + delta[0], exp[1] + delta[1]) for exp in self.reachable_cells if round(exp[0] / 10000) == region}
        self.reachable_cells.update({exp for exp in self.reachable_cells if round(exp[0] / 10000) != region})
        
        return rebuilt_position, other_position

    def create_training_data(self):
        sizes = [(50, 50), (75, 75), (100, 100)]
        seeds = [i for i in range(1, 201)]

        training_data_files = os.listdir('./view_learning_agent/training_data')
        if len(training_data_files) == len(sizes) * len(seeds):
            return
        else:
            shutil.rmtree('./view_learning_agent/training_data')
            os.mkdir('./view_learning_agent/training_data')
            for size in sizes:
                for seed in seeds:
                    with open(f'./view_learning_agent/training_data/{size[0]}x{size[1]}_{seed}.png', 'wb') as f:
                        try:
                            image = requests.post(f'{self.server_url}/maze/', json={"seed": seed, "width": size[0], "height": size[1]}).content
                            f.write(image)
                        except:
                            print("Error fetching image")
                            os.rmdir('./view_learning_agent/training_data')
                            return
    
    def construct_view(self, matrix: np.array, position: tuple, size: int):
        view = np.zeros((size, size))
        for i in range(-size//2, size//2 + 1):
            for j in range(-size//2, size//2 + 1):
                x = position[0] + i
                y = position[1] + j
                if x < 0 or x >= matrix.shape[0] or y < 0 or y >= matrix.shape[1]:
                    view[i + size//2, j + size//2] = 0
                else:
                    view[i + size//2, j + size//2] = matrix[x][y]
        return view
    
    def move_to_target(self, target: tuple):
        start = (self.position[0], self.position[1])
        end = target
        
        queue = [start]
        distance = {pos: np.inf for pos in self.memory}
        distance.update({pos: np.inf for code in self.portal_positions for pos in self.portal_positions[code]})
        distance[start[0], start[1]] = 0
        parent = {pos: None for pos in self.memory}
        parent.update({pos: None for code in self.portal_positions for pos in self.portal_positions[code]})
        children = {pos: [] for pos in self.memory}
        children.update({pos: [] for code in self.portal_positions for pos in self.portal_positions[code]})

        reverse_moves = {(-1, 0): "N", (0, 1): "E", (1, 0): "S", (0, -1): "W", (0, 0): "P"}
        while queue:
            current = queue.pop(0)
            if current == end:
                break
            for i, j in [(0, 1), (1, 0), (0, -1), (-1, 0), (0, 0)]:
                x = current[0] + i
                y = current[1] + j
                if (x, y) not in self.memory and (x, y) not in self.portal_positions:
                    continue
                if self.memory[(x, y)] == 0:
                    continue
                if (i, j) == (0, 0) and self.memory[(x, y)] not in range(150, 170):
                    continue
                if self.memory[(x, y)] in range(101, 106):
                    continue
                elif self.memory[(x, y)] in range(106, 111):
                    # Push forward n positions
                    n = self.memory[(x, y)] - 105
                    x += i * n
                    y += j * n
                    if (x, y) not in self.memory or self.memory[x, y] == 0:
                        continue
                elif self.memory[(x, y)] in range(111, 116):
                    # Push back n positions
                    n = self.memory[(x, y)] - 110
                    x -= i * n
                    y -= j * n
                    if (x, y) not in self.memory or self.memory[x, y] == 0:
                        continue
                elif self.memory[(x, y)] in range(150, 170) and (i, j) == (0, 0):
                    # Go through portal
                    # TODO Check here it might break something
                    if self.memory[(x, y)] not in self.portal_positions:
                        continue
                    for portal_position in self.portal_positions[self.memory[(x, y)]]:
                        if portal_position != (x, y):
                            x, y = portal_position
                            break
                if distance[(current[0], current[1])] + 1 < distance[(x, y)]:
                    distance[(x, y)] = distance[(current[0], current[1])] + 1
                    parent[(x, y)] = current
                    children[(current[0], current[1])].append(((x, y), reverse_moves[(i, j)]))
                    queue.append((x, y))
        if distance[(end[0], end[1])] == np.inf:
            return None
        for (i, j) in self.memory:
            distance[(i, j)] = np.inf if distance[(i, j)] == np.inf else (distance[(i, j)] - distance[(end[0], end[1])])
        for code in self.portal_positions:
            for (i, j) in self.portal_positions[code]:
                distance[(i, j)] = np.inf if distance[(i, j)] == np.inf else (distance[(i, j)] - distance[(end[0], end[1])])
        child_queue = [start]
        path = []
        current = start
        while current != end and len(child_queue) > 0:
            best_child = None
            best_distance = np.inf
            best_child_direction = None
            for child, direction in children[(current[0], current[1])]:
                if distance[(child[0], child[1])] < best_distance:
                    best_distance = distance[(child[0], child[1])]
                    best_child = child
                    best_child_direction = direction
            if best_child is None:
                for parent in children:
                    children[parent] = [(child, direction) for child, direction in children[parent] if child != current]
                    if children[parent] is None:
                        children[parent] = []
                child_queue.pop()
                if len(child_queue) == 0:
                    break
                path.pop()
                current = child_queue[-1]
            else:
                path.append(best_child_direction)
                current = best_child
                child_queue.append(current)
        if path == []:
            return None
        return "".join(path[:self.moves])

    def train(self):
        self.view_map = {}
        training_data_files = os.listdir('./view_learning_agent/training_data')
        for file in training_data_files:
            with open(f'./view_learning_agent/training_data/{file}', 'rb') as f:
                image = np.array(Image.open(f))
                start, end, distance, parent, children = self.solve_maze_bfs(image)
                for i in range(image.shape[0]):
                    for j in range(image.shape[1]):
                        if image[i, j] == 0 or distance[i, j] == np.inf:
                            continue
                        for size in [1, 3, 5, 7]:
                            constructed_view = self.construct_view(image, (i, j), size)
                            view_map_key = constructed_view.tobytes()
                            path = []
                            current = (i, j)
                            while len(path) < 10 and current != end:
                                best_child = None
                                best_distance = np.inf
                                best_child_direction = None
                                for child, direction in children[current[0], current[1]]:
                                    if distance[child[0], child[1]] < best_distance:
                                        best_distance = distance[child[0], child[1]]
                                        best_child = child
                                        best_child_direction = direction
                                if best_child is None:
                                    break
                                path.append(direction)
                                current = best_child
                            score = distance[current[0], current[1]]
                            if view_map_key not in self.view_map:
                                self.view_map[view_map_key] = []
                            found = False
                            for p, s, c in self.view_map[view_map_key]:
                                if p == path:
                                    self.view_map[view_map_key].remove((p, s, c))
                                    self.view_map[view_map_key].append((path, min(s, score), c + 1))
                                    found = True
                                    break
                            if not found:
                                self.view_map[view_map_key].append((path, score, 1))
            print(f"Finished training on {file}")
        for key in self.view_map:
            self.view_map[key] = sorted(self.view_map[key], key=lambda x: x[1] / x[2])
        with open('./view_learning_agent/learned_data.pkl', 'wb+') as f:
            pickle.dump(self.view_map, f)

    def view_or_first_division(self, view: np.array):
        view_map_key = view.tobytes()
        if view.shape == (1, 1):
            return view_map_key
        if view_map_key in self.view_map:
            return view_map_key
        else:
            return self.view_or_first_division(view[1:-1, 1:-1])
        
    def view_all_divisions(self, view: np.array):
        divisions = []
        for i in range(0, view.shape[0] // 2 + 1):
            view_key = view[i:view.shape[0] - i, i:view.shape[0] - i].tobytes()
            if view_key in self.view_map:
                divisions.append(view_key)
        return divisions
    
    def calculate_path_score(self, path: list, position: tuple):
        moves = {"N": (-1, 0), "E": (0, 1), "S": (1, 0), "W": (0, -1), "X": (0, 0), "P": (0, 0)}
        score = 0
        current = position
        for move in path:
            current = (current[0] + moves[move][0], current[1] + moves[move][1])
            if current not in self.memory:
                score += 2
            elif self.memory[current] in range(101, 106):
                score = -1
                break
            # TODO change scoring here
            elif self.memory[current] == 0 or self.memory[current] in range(106, 116):
                break
            elif self.memory[current] == 182:
                score += 100
                break
            elif current not in self.explored_cells:
                score += 1
        return score
    def move(self):
        view = self.construct_view(self.view, (self.view.shape[0] // 2, self.view.shape[0] // 2), self.view.shape[0])
        all_divisions = self.view_all_divisions(view)
        all_paths = {"".join(path[:self.moves]): 0 for division in all_divisions for path, _, _ in self.view_map[division]}
        for path in all_paths:
            all_paths[path] = self.calculate_path_score(path, self.position)
        best_path, best_score = max(all_paths.items(), key=lambda x: x[1]) if len(all_paths) > 0 else ("", 0)
        if best_score <= 0:
            closest_reachable = None if len(self.reachable_cells) == 0 else min(self.reachable_cells, key=lambda x: (self.position[0] - x[0]) ** 2 + (self.position[1] - x[1]) ** 2)
            if closest_reachable is None:
                print("No reachable neighbors")
                return "".join([random.choice(["N", "E", "S", "W"]) for _ in range(self.moves)])
            best_path = self.move_to_target(closest_reachable)
            if best_path is None:
                print("No path to neighbor", closest_reachable)
                return "".join([random.choice(["N", "E", "S", "W"]) for _ in range(self.moves)])
            return best_path
        
        best_path = best_path + "".join([random.choice(["N", "E", "S", "W"]) for _ in range(self.moves - len(best_path))])
        return best_path
    