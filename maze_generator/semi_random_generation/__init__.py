import argparse
from semi_random_generation import generate_maze, X_RAY, FOG, TOWER, TRAP_MOVEMENT_BASE, TRAP_REWIND_BASE, TRAP_PUSHFORWARD_BASE, TRAP_PUSHBACK_BASE, PORTAL_BASE

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a semi-random maze.")
    parser.add_argument("--seed", type=int, default=None, help="Seed for random generation.")
    parser.add_argument("--width", type=int, default=100, help="Width of the maze.")
    parser.add_argument("--height", type=int, default=100, help="Height of the maze.")
    parser.add_argument("--test", action="store_true", help="Generate a colored maze for testing.")
    parser.add_argument("--no_special_tiles", action="store_true", help="Not add special tiles in maze.")

    args = parser.parse_args()

    special_tile_counts = {
        X_RAY: 5,
        FOG: 7,
        TOWER: 3,
        TRAP_MOVEMENT_BASE: 2,
        TRAP_REWIND_BASE: 2,
        TRAP_PUSHFORWARD_BASE: 2,
        TRAP_PUSHBACK_BASE: 2,
        PORTAL_BASE: 4
    }

    # Generate the maze
    try:
        maze, entrance, exit, path_length, total_path_tiles = generate_maze(
            seed=args.seed,
            width=args.width,
            height=args.height,
            special_tile_counts=special_tile_counts,
            test=args.test,
            no_special_tiles=args.no_special_tiles
        )

        print("Maze generated successfully!")
        print(f"Entrance: {entrance}")
        print(f"Exit: {exit}")
        print(f"Path Length: {path_length}")
        print(f"Total Path Tiles: {total_path_tiles}")

        if args.test:
            maze.save("maze.png")
        else:
            print("Maze saved without visualization.")
    except ValueError as e:
        print(f"Error during maze generation: {e}")
