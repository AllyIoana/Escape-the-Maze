import cv2
import numpy as np
from skimage import measure

# Constants for tile colors
WALL = 0
PATH = 255
ENTRANCE = 64
EXIT = 182
XRAY_INCREMENT = 16
FOG = 32
TOWER = 224
TRAP_MOVEMENT_RANGE = range(96, 101)
TRAP_REWIND_RANGE = range(101, 106)
TRAP_PUSHFORWARD_RANGE = range(106, 111)
TRAP_PUSHBACK_RANGE = range(111, 116)
PORTAL_RANGE = range(150, 170)  # Each portal value should appear exactly twice

def load_image(file_path):
    """Load grayscale image as a 2D numpy array."""
    return cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)

def validate_tile_placement(maze):
    """Ensure special tiles are not adjacent to each other, entrance, or exit."""
    rows, cols = maze.shape
    for i in range(rows):
        for j in range(cols):
            current_tile = maze[i, j]
            if current_tile in [ENTRANCE, EXIT, XRAY_INCREMENT, FOG, TOWER] or \
               current_tile in TRAP_MOVEMENT_RANGE or \
               current_tile in TRAP_REWIND_RANGE or \
               current_tile in TRAP_PUSHFORWARD_RANGE or \
               current_tile in TRAP_PUSHBACK_RANGE or \
               current_tile in PORTAL_RANGE:
                # Extract neighbors, excluding the current tile itself
                neighbors = maze[max(0, i-1):i+2, max(0, j-1):j+2]
                neighbors = neighbors.flatten()
                neighbors = neighbors[neighbors != current_tile]
                
                # Check adjacency constraints
                if any(tile in neighbors for tile in [ENTRANCE, EXIT] if tile != current_tile):
                    print(f"Invalid adjacency found near tile at ({i}, {j}) with neighbors: {neighbors}")
                    return False
    return True

def validate_path(maze):
    """Check if there is a path from entrance to exit covering 50% of the area."""
    labeled, num_features = measure.label(maze == PATH, connectivity=2, return_num=True)
    if num_features < 1:
        print("No path found between entrance and exit.")
        return False
    
    entrance_coords = np.argwhere(maze == ENTRANCE)[0]
    exit_coords = np.argwhere(maze == EXIT)[0]
    entrance_label = labeled[entrance_coords[0], entrance_coords[1]]
    exit_label = labeled[exit_coords[0], exit_coords[1]]
    
    if entrance_label != exit_label:
        print("Entrance and exit are not connected.")
        return False
    
    # Check if the connected area covers at least 50%
    path_area = np.sum(labeled == entrance_label)
    if path_area < 0.5 * maze.size:
        print("Path does not cover 50% of the maze.")
        return False
    return True

def validate_portals(maze):
    """Ensure each portal ID appears exactly twice."""
    portal_ids = [pid for pid in np.unique(maze) if pid in PORTAL_RANGE]
    for pid in portal_ids:
        if np.sum(maze == pid) != 2:
            print(f"Portal ID {pid} does not appear exactly twice.")
            return False
    return True

def generate_maze_from_image(file_path, save_file):
    # Load image
    maze = load_image(file_path)
    
    if maze is None:
        print("Error loading image.")
        return False

    # Validate tile placement
    if not validate_tile_placement(maze):
        print("Maze validation failed: invalid tile placement.")
        return False

    # Validate path from entrance to exit
    if not validate_path(maze):
        print("Maze validation failed: path constraints not met.")
        return False

    # Validate portal pairs
    if not validate_portals(maze):
        print("Maze validation failed: portal constraints not met.")
        return False

    # Save the validated maze as output
    if (save_file):
        output_path = 'validated_maze.png'
        cv2.imwrite(output_path, maze)
        print(f"Maze validated and saved as {output_path}.")
    else:
        print("Maze validated.")
    
    return True

