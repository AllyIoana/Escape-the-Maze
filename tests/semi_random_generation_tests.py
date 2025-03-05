import sys
import os
import unittest
import numpy as np
import time
from parameterized import parameterized
import cv2

sys.path.append('../maze_generator/semi_random_generation')
import semi_random_generation

class SemiRandomGenerationTestCase(unittest.TestCase):

    X_RAY = 16
    FOG = 32
    TOWER = 224
    TRAP_MOVEMENT_BASE = 96
    TRAP_REWIND_BASE = 101
    TRAP_PUSHFORWARD_BASE = 106
    TRAP_PUSHBACK_BASE = 111
    PORTAL_BASE = 150

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

    @parameterized.expand([
        (4, 4),
        (10, 10),
        (15, 15),
        (20, 20),
        (35, 35),
        (50, 50),
        (65, 65),
        (75, 75),
        (80, 80),
        (100, 100),
    ])
    def test_instance_and_size(self, width, height):
        maze, entrance, exit, _, _ = semi_random_generation.generate_maze(None, width, height, self.special_tile_counts, True)

        time.sleep(0.2)

        maze = np.array(maze)

        # assert that the maze is a numpy array
        self.assertIsInstance(maze, np.ndarray)

        # assert that the maze has the correct shape
        self.assertEqual((maze.shape[0], maze.shape[2]), (width, height))

    @parameterized.expand([
        (4, 4),
        (10, 10),
        (15, 15),
        (20, 20),
        (35, 35),
        (50, 50),
        (65, 65),
        (75, 75),
        (80, 80),
        (100, 100),
    ])
    def test_entrance_and_exit(self, width, height):
        maze, entrance, exit, _, _ = semi_random_generation.generate_maze(None, width, height, self.special_tile_counts, True)

        time.sleep(0.2)

        maze = np.array(maze)

        # assert that the entrance and exit are inside the maze
        self.assertTrue(0 <= entrance[0] < width)
        self.assertTrue(0 <= entrance[1] < height)
        self.assertTrue(0 <= exit[0] < width)
        self.assertTrue(0 <= exit[1] < height)

if __name__ == '__main__':
    unittest.main(verbosity=2)
