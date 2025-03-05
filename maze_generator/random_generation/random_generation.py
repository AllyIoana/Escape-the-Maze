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

# Special tiles for testing (colors in RGB)
COLOR_TEST_ENTRANCE = (255, 0, 0)           # Red
COLOR_TEST_EXIT = (0, 255, 0)               # Green
COLOR_TEST_X_RAY = (255, 255, 0)            # Yellow
COLOR_TEST_FOG = (128, 128, 128)            # Gray
COLOR_TEST_TOWER = (0, 0, 255)              # Blue
COLOR_TEST_TRAP_MOVEMENT = (255, 69, 0)     # OrangeRed
COLOR_TEST_TRAP_REWIND = (75, 0, 130)       # Indigo
COLOR_TEST_TRAP_PUSHFORWARD = (199, 21, 133) # MediumVioletRed
COLOR_TEST_TRAP_PUSHBACK = (255, 105, 180)  # HotPink
COLOR_TEST_PORTAL = (128, 0, 128)           # Purple

# Directions for movement (right, down, left, up)
DIRECTIONS = [(0, 2), (2, 0), (0, -2), (-2, 0)]
BFS_DIRECTIONS = [(1, 0), (0, 1), (-1, 0), (0, -1)]

# Maximum attempts to generate a valid maze
MAX_ATTEMPTS = 500

def initialize_maze(width, height):
    # Initialize the maze with walls
    maze = np.full((height, width), WALL, dtype=np.uint8)
    return maze

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

def add_special_tiles(maze, max_threshold, width, height):
    # Determine a random count for each type of special tile up to max_threshold
    special_tile_counts = {
        X_RAY: random.randint(0, max_threshold),
        FOG: random.randint(0, max_threshold),
        TOWER: random.randint(0, max_threshold),
        TRAP_MOVEMENT_BASE: random.randint(0, max_threshold),
        TRAP_REWIND_BASE: random.randint(0, max_threshold),
        TRAP_PUSHFORWARD_BASE: random.randint(0, max_threshold),
        TRAP_PUSHBACK_BASE: random.randint(0, max_threshold)
    }

    # For portals, select up to 20 unique portal IDs and place each exactly twice
    portal_ids = random.sample(range(PORTAL_BASE, PORTAL_BASE + 20), k=min(20, max_threshold))
    portal_placements = {pid: 2 for pid in portal_ids}  # Each portal ID appears twice

    placed_counts = {key: 0 for key in special_tile_counts}
    available_positions = [(x, y) for x in range(width) for y in range(height) if maze[y, x] == PATH]
    random.shuffle(available_positions)  # Randomize to prevent biases in tile placement

    def is_adjacent_to_special(x, y):
        for dx, dy in BFS_DIRECTIONS:
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height:
                # If the adjacent tile is not WALL or PATH, it is a special tile
                if maze[ny, nx] not in (WALL, PATH):
                    return True
        return False

    for x, y in available_positions:
        # Skip if the position is already a special tile or if it’s adjacent to one
        if maze[y, x] != PATH or is_adjacent_to_special(x, y):
            continue

        # Place a random special tile type if there are any remaining
        tile_type = random.choice(list(special_tile_counts.keys()) + list(portal_placements.keys()))

        # Place non-portal special tiles
        if tile_type in special_tile_counts and placed_counts[tile_type] < special_tile_counts[tile_type]:
            if tile_type != FOG and tile_type != TOWER and tile_type != X_RAY:
                maze[y, x] = tile_type + random.choice(range(0, 5))
            else:
                maze[y, x] = tile_type
            placed_counts[tile_type] += 1

        # Place portal tiles if there are still placements left
        elif tile_type in portal_placements and portal_placements[tile_type] > 0:
            maze[y, x] = tile_type
            portal_placements[tile_type] -= 1

        # Stop if all tiles have been placed
        if all(count >= special_tile_counts[tile_type] for tile_type, count in placed_counts.items()) and \
           all(count <= 0 for count in portal_placements.values()):
            break

def colorize_maze(maze, entrance, exit):
    # Create an RGB image and colorize special tiles
    color_maze = np.zeros((maze.shape[0], maze.shape[1], 3), dtype=np.uint8)
    color_maze[maze == PATH] = (255, 255, 255)  # White for path
    color_maze[maze == WALL] = (0, 0, 0)        # Black for walls

    # Color the entrance and exit
    color_maze[entrance[1], entrance[0]] = COLOR_TEST_ENTRANCE
    color_maze[exit[1], exit[0]] = COLOR_TEST_EXIT

    # Color other special tiles
    color_maze[maze == X_RAY] = COLOR_TEST_X_RAY
    color_maze[maze == FOG] = COLOR_TEST_FOG
    color_maze[maze == TOWER] = COLOR_TEST_TOWER
    color_maze[maze in range(TRAP_MOVEMENT_BASE, TRAP_MOVEMENT_BASE + 5)] = COLOR_TEST_TRAP_MOVEMENT
    color_maze[maze in range(TRAP_REWIND_BASE, TRAP_REWIND_BASE + 5)] = COLOR_TEST_TRAP_REWIND
    color_maze[maze in range(TRAP_PUSHFORWARD_BASE, TRAP_PUSHFORWARD_BASE + 5)] = COLOR_TEST_TRAP_PUSHFORWARD
    color_maze[maze in range(TRAP_PUSHBACK_BASE, TRAP_PUSHBACK_BASE + 5)] = COLOR_TEST_TRAP_PUSHBACK
    color_maze[maze == PORTAL_BASE] = COLOR_TEST_PORTAL

    return Image.fromarray(color_maze, mode="RGB")

def generate_maze(seed=None, width=100, height=100, max_threshold=10, test=False, no_special_tiles=False):
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
                    add_special_tiles(maze, max_threshold, width, height)

                # Save the maze with or without colors based on test flag
                file_suffix = f"{seed if seed is not None else 'default'}"
                if test:
                    maze_img = colorize_maze(maze, entrance, exit)
                    filename = f"maze_{width}x{height}-seed={file_suffix}-test.png"
                    maze_img.save(filename)

                return (entrance[1], entrance[0]), (exit[1], exit[0]), path_length, total_path_tiles, maze

        attempts += 1

    raise ValueError("Failed to generate a valid maze within the maximum attempts.")
