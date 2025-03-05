import random
from base_agent.base_agent import BaseAgent

class AStarAgent(BaseAgent):
    def initialize_agent_info(self, response: dict):
        super().initialize_agent_info(response)
        self.path = [self.position]  # Store the path of positions
        self.visited = set([self.position])  # Track visited positions
        self.directions = {'N': (-1, 0), 'E': (0, 1), 'S': (1, 0), 'W': (0, -1)}  # Possible directions

    def heuristic(self, position):
        # Penalizare pentru backtracking
        backtracking_penalty = 1 if position in self.visited else 0

        # Număr de drumuri libere din vecinătate
        num_open_paths = sum(
            1 for direction in self.directions.values()
            if self.is_path((position[0] + direction[0], position[1] + direction[1]))
        )

        # Explorarea zonelor necunoscute
        unknown_bonus = 0 if position in self.memory else -10  # Bonus mare pentru zonele necunoscute

        # Combine penalizări și bonusuri
        heuristic_value = backtracking_penalty + (1 / (num_open_paths + 1)) + unknown_bonus
        return heuristic_value

    def is_path(self, position):
        return (self.memory.get(position, 0) != 0)

    def move(self):
        moves = []
        candidates = []

        # Explorează toate direcțiile posibile
        for direction, delta in self.directions.items():
            next_position = (self.position[0] + delta[0], self.position[1] + delta[1])

            # Verifică dacă poziția următoare este validă
            if self.is_path(next_position) and next_position not in self.visited:
                heuristic_value = self.heuristic(next_position)
                candidates.append((heuristic_value, direction, next_position))

        # Prioritizează mutările pe baza euristicii
        if candidates:
            candidates.sort(key=lambda x: x[0])  # Sortează după euristică (cel mai mic cost)
            _, best_direction, best_position = candidates[0]

            # Verifică dacă următoarea poziție este ieșirea
            if self.memory.get(best_position, 0) == 182:
                print("Exit found!")
                self.finished = True  # Marchează labirintul ca rezolvat
                return ''  # Nu mai generăm alte mutări

            # Logica pentru tile uri speciale
            tile_value = self.memory.get(best_position, 0)
            if tile_value != 255 and tile_value != 182:
                view = self.construct_view()
                super().register_move({"name": best_direction, "successful": 1, "view": view})
                if tile_value in range(111,115):
                    candidates.remove((_, best_direction, best_position))
                    candidates.sort(key=lambda x: x[0])
                    _, best_direction, best_position = candidates[0]
            else:
                self.position = best_position

            # Actualizează starea agentului
            self.visited.add(best_position)
            self.path.append(best_position)
            moves.append(best_direction)
        else:
            # Backtracking dacă nu există mutări valide
            if self.path:
                previous_position = self.path.pop()
                if previous_position[0] > self.position[0]:
                    moves.append('S')
                elif previous_position[0] < self.position[0]:
                    moves.append('N')
                elif previous_position[1] > self.position[1]:
                    moves.append('E')
                elif previous_position[1] < self.position[1]:
                    moves.append('W')
                self.position = previous_position

        return ''.join(moves) 

    def construct_view(self):
        view_matrix = []
        for dx in range(-1, 2):
            row = []
            for dy in range(-1, 2):
                neighbor_position = (self.position[0] + dx, self.position[1] + dy)
                row.append(str(self.memory.get(neighbor_position, 0)))
            view_matrix.append(",".join(row))
        return ";".join(view_matrix)
