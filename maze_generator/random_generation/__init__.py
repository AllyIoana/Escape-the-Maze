import argparse
from random_generation import generate_maze

# Set up argument parsing
parser = argparse.ArgumentParser(description="Generate a maze with optional seed, dimensions, and test mode.")
parser.add_argument("--seed", type=int, default=None, help="Seed for random generation.")
parser.add_argument("--width", type=int, default=100, help="Width of the maze.")
parser.add_argument("--height", type=int, default=100, help="Height of the maze.")
parser.add_argument("--max_threshold", type=int, default=10, help="Maximum threshold for special tiles.")
parser.add_argument("--test", action="store_true", help="Generate a colored maze for testing.")
parser.add_argument("--no_special_tiles", action="store_true", help="Not add special tiles in maze.")

# Parse the arguments
args = parser.parse_args()

# Run maze generation with seed and threshold
try:
    entrance, exit, path_length, total_path_tiles, maze = generate_maze(
        seed=args.seed,
        width=args.width,
        height=args.height,
        max_threshold=args.max_threshold,
        test=args.test,
        no_special_tiles=args.no_special_tiles
    )

    if maze is not None:
        print("Valid maze generated.")
        print(f"Entrance: {entrance}")
        print(f"Exit: {exit}")
        print(f"Path Length: {path_length}")
        print(f"Total Path Tiles: {total_path_tiles}")
    else:
        print("Maze did not meet the required conditions.")
except ValueError as e:
    print(f"Error during maze generation: {e}")