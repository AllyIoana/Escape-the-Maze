import numpy as np
from PIL import Image
import random
from collections import deque

# Tile values
WALL = 0
PATH = 255
ENTRANCE = 64
EXIT = 182
X_RAY = 16
FOG = 32
TOWER = 224
TRAP_MOVEMENT_BASE = 96
TRAP_REWIND_BASE = 101
TRAP_PUSHFORWARD_BASE = 106
TRAP_PUSHBACK_BASE = 111
PORTAL_BASE = 150

MAX_ATTEMPTS = 300

# Special tiles colors for visualization
SPECIAL_TILE_COLORS = {
    ENTRANCE: (255, 0, 0),           # Red
    EXIT: (0, 255, 0),               # Green
    X_RAY: (255, 255, 0),            # Yellow
    FOG: (255, 165, 0),              # Orange
    TOWER: (0, 0, 255),              # Blue
    TRAP_MOVEMENT_BASE: (255, 0, 255),      # Magenta
    TRAP_REWIND_BASE: (75, 0, 130),    # Indigo
    TRAP_PUSHFORWARD_BASE: (0, 255, 255),    # Cyan
    TRAP_PUSHBACK_BASE: (255, 105, 180),    # HotPink
    PORTAL_BASE: (128, 0, 128),       # Purple
}

# Directions for maze carving and traversal
DIRECTIONS = [(0, 2), (2, 0), (0, -2), (-2, 0)]
BFS_DIRECTIONS = [(1, 0), (0, 1), (-1, 0), (0, -1)]

# Maze Initialization
def initialize_maze(width, height):
    return np.full((height, width), WALL, dtype=np.uint8)

def carve_passage(maze, start_position, width, height, min_length):
    # Stack to keep track of the current path
    stack = [start_position]
    total_carved = 0
    visited = set([start_position])

    while stack and total_carved < min_length:
        x, y = stack[-1]

        if maze[y, x] != PATH:
            maze[y, x] = PATH
            total_carved += 1

        random.shuffle(DIRECTIONS)
        carved = False

        for dx, dy in DIRECTIONS:
            nx, ny = x + dx, y + dy
            # Check if the neighboring cell could be a valid path
            if (0 <= nx < width and 0 <= ny < height and maze[ny, nx] == WALL and (nx, ny) not in visited):
                inter_x, inter_y = x + dx // 2, y + dy // 2
                if maze[inter_y, inter_x] != PATH:
                    maze[inter_y, inter_x] = PATH
                    total_carved += 1

                visited.add((nx, ny))
                stack.append((nx, ny))
                carved = True
                break
        if not carved:
            stack.pop()

def bfs_shortest_paths(maze, start, width, height):
    # Initialize the distance matrix with -1 (unreachable)
    distance_matrix = np.full((height, width), -1, dtype=int)
    queue = deque([start])
    distance_matrix[start[1], start[0]] = 0

    while queue:
        x, y = queue.popleft()
        for dx, dy in BFS_DIRECTIONS:
            nx, ny = x + dx, y + dy
            if (0 <= nx < width and 0 <= ny < height and
                    maze[ny, nx] == PATH and distance_matrix[ny, nx] == -1):
                distance_matrix[ny, nx] = distance_matrix[y, x] + 1
                queue.append((nx, ny))

    return distance_matrix

def place_entrance_exit(maze, width, height):
    # Calculate max attempts proportional to the maze size
    max_attempts = 10

    # Generate a unique set of random positions
    available_positions = [(x, y) for x in range(1, width, 2) for y in range(1, height, 2) if maze[y, x] == PATH]
    random.shuffle(available_positions)
    entrance_positions = available_positions[:max_attempts]

    for entrance in entrance_positions:
        # Place the entrance and exit in the maze
        maze[entrance[1], entrance[0]] = ENTRANCE

        # Compute the distance matrix from the entrance
        distance_matrix = bfs_shortest_paths(maze, entrance, width, height)

        # Total number of path tiles
        total_path_tiles = np.count_nonzero(maze == PATH)

        # Minimum required distance for the exit (50% of path tiles)
        min_exit_distance = total_path_tiles // 2

        # Find all valid exit candidates
        valid_exit_candidates = [
            (x, y) for y in range(height)
            for x in range(width)
            if distance_matrix[y, x] >= min_exit_distance
        ]

        if not valid_exit_candidates:
            maze[entrance[1], entrance[0]] = PATH
            continue

        # Randomly select an exit from the valid candidates
        exit = random.choice(valid_exit_candidates)
        maze[exit[1], exit[0]] = EXIT

        return entrance, exit, distance_matrix[exit[1], exit[0]]

    # If all attempts fail, return failure
    return None, None, 0

# Add special tiles based on fixed counts
def add_special_tiles(maze, special_tile_counts, width, height):
    tile_positions = [(x, y) for x in range(width) for y in range(height) if maze[y, x] == PATH]
    random.shuffle(tile_positions)

    placed_counts = {tile: 0 for tile in special_tile_counts}

    portal_ids = random.sample(range(PORTAL_BASE, PORTAL_BASE + 20), k=special_tile_counts[PORTAL_BASE])
    portal_placements = {pid: 2 for pid in portal_ids}  # Each portal ID appears twice

    def is_adjacent_to_special(x, y):
        for dx, dy in BFS_DIRECTIONS:
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height:
                # If the adjacent tile is not WALL or PATH, it is a special tile
                if maze[ny, nx] not in (WALL, PATH):
                    return True
        return False

    for tile_type, count in special_tile_counts.items():
        for _ in range(count):
            if not tile_positions:
                break
            x, y = tile_positions.pop()

            # Skip if the position is already a special tile or adjacent to one
            if maze[y, x] != PATH or is_adjacent_to_special(x, y):
                continue

            # Place non-portal special tiles
            if placed_counts[tile_type] < special_tile_counts[tile_type]:
                if tile_type != FOG and tile_type != TOWER and tile_type != X_RAY:
                    maze[y, x] = tile_type + random.choice(range(0, 5))
                else:
                    maze[y, x] = tile_type
                placed_counts[tile_type] += 1
            else:
                tile_type = random.choice(list(special_tile_counts.keys()) + list(portal_placements.keys()))

                # Place portal tiles if there are placements left
                if tile_type in portal_placements and portal_placements[tile_type] > 0:
                    maze[y, x] = tile_type
                    portal_placements[tile_type] -= 1

            # Stop if all special tiles have been placed
            if all(count >= special_tile_counts[tile_type] for tile_type, count in placed_counts.items()) and \
               all(count <= 0 for count in portal_placements.values()):
                break

# Colorize maze for visualization
def colorize_maze(maze, entrance, exit):
    color_maze = np.zeros((maze.shape[0], maze.shape[1], 3), dtype=np.uint8)
    color_maze[maze == PATH] = (255, 255, 255)
    color_maze[maze == WALL] = (0, 0, 0)

    for tile_type, color in SPECIAL_TILE_COLORS.items():
        if tile_type not in (ENTRANCE, EXIT, X_RAY, FOG, TOWER):
            color_maze[maze in range(tile_type, tile_type + 5)] = color
        else:
            color_maze[maze == tile_type] = color

    color_maze[entrance[1], entrance[0]] = SPECIAL_TILE_COLORS[ENTRANCE]
    color_maze[exit[1], exit[0]] = SPECIAL_TILE_COLORS[EXIT]
    return Image.fromarray(color_maze, mode="RGB")

# Generate the maze
def generate_maze(seed=None, width=100, height=100, special_tile_counts=None, test=False, no_special_tiles=False):
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)

    attempts = 0

    total_area = width * height
    if total_area <= 150 * 150:
        coverage_percentage = 0.5
    if total_area <= 500 * 500:
        coverage_percentage = 0.35
    else:
        coverage_percentage = 0.25

    min_length_to_carve = (width * height) * coverage_percentage

    while attempts < MAX_ATTEMPTS:
        maze = initialize_maze(width, height)
        start_position = (random.randrange(1, width, 2), random.randrange(1, height, 2))
        maze[start_position[1], start_position[0]] = PATH
        carve_passage(maze, start_position, width, height, min_length_to_carve)

        entrance, exit, path_length = place_entrance_exit(maze, width, height)
        if entrance and exit:
            total_path_tiles = np.count_nonzero(maze == PATH) + 2
            if path_length >= total_path_tiles / 2:
                if not no_special_tiles:
                    add_special_tiles(maze, special_tile_counts, width, height)

                # Generate the maze image
                if test:
                    maze_img = colorize_maze(maze, entrance, exit)
                else:
                    maze_img = Image.fromarray(maze, mode="L")

                return maze_img, (entrance[1], entrance[0]), (exit[1], exit[0]), path_length, total_path_tiles

        attempts += 1

    raise ValueError("Failed to generate a valid maze within the maximum attempts.")

