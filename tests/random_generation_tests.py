import sys
import os
import unittest
import numpy as np
import time
from parameterized import parameterized

sys.path.append('../maze_generator/random_generation')
sys.path.append('../maze_generator/file_input_generation')
import random_generation
import file_input_generation

class RandomGenerationTestCase(unittest.TestCase):

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
        entrance, exit, path_length, total_path_tiles, maze = random_generation.generate_maze(
            None, width, height, 0, True)

        time.sleep(0.2)

        # assert that the maze is a numpy array
        self.assertIsInstance(maze, np.ndarray)

        # assert that the maze has the correct shape
        self.assertEqual((maze.shape[0], maze.shape[1]), (width, height))

        # assert that the maze is correct
        maze_file = f"maze_{width}x{height}-seed=default-test.png"
        self.assertTrue(file_input_generation.generate_maze_from_image(maze_file, False))

        # delete the generated maze
        os.remove(maze_file)

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
        entrance, exit, path_length, total_path_tiles, maze = random_generation.generate_maze(
            None, width, height, 0, True)

        time.sleep(0.2)

        # assert that the maze is a numpy array
        self.assertIsInstance(maze, np.ndarray)

        # assert that the entrance and exit are inside the maze
        self.assertTrue(0 <= entrance[0] < width)
        self.assertTrue(0 <= entrance[1] < height)
        self.assertTrue(0 <= exit[0] < width)
        self.assertTrue(0 <= exit[1] < height)

        # assert that the maze is correct
        maze_file = f"maze_{width}x{height}-seed=default-test.png"
        self.assertTrue(file_input_generation.generate_maze_from_image(maze_file, False))

        # delete the generated maze
        os.remove(maze_file)

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
    def test_path_length(self, width, height):
        entrance, exit, path_length, total_path_tiles, maze = random_generation.generate_maze(
            None, width, height, 0, True)

        time.sleep(0.2)

        # assert that the maze is a numpy array
        self.assertIsInstance(maze, np.ndarray)

        # assert that the path length is in range
        self.assertTrue(0 <= path_length <= width * height)
        self.assertTrue(0 <= total_path_tiles <= width * height)

        # assert that the maze is correct
        maze_file = f"maze_{width}x{height}-seed=default-test.png"
        self.assertTrue(file_input_generation.generate_maze_from_image(maze_file, False))

        # delete the generated maze
        os.remove(maze_file)

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
    def test_name_save(self, width, height):
        entrance, exit, path_length, total_path_tiles, maze = random_generation.generate_maze(
            None, width, height, 0, True)

        time.sleep(0.2)

        # assert that the maze is a numpy array
        self.assertIsInstance(maze, np.ndarray)

        # assert that the maze is correct
        maze_file = f"maze_{width}x{height}-seed=default-test.png"
        self.assertTrue(file_input_generation.generate_maze_from_image(maze_file, False))

        # assert that the maze is saved with the correct name
        self.assertTrue(os.path.exists(maze_file))

        # delete the generated maze
        os.remove(maze_file)

    @parameterized.expand([
        (4, 4, 1242),
        (10, 10, 182),
        (15, 15, 8122),
        (20, 20, 1221),
        (35, 35, 293),
        (50, 50, 213),
        (65, 65, 19),
        (75, 75, 291924),
        (80, 80, 182892),
        (100, 100, 1828499),
    ])
    def test_seed(self, width, height, seed):
        entrance, exit, path_length, total_path_tiles, maze = random_generation.generate_maze(
            seed, width, height, 0, True)

        # assert that the maze is a numpy array
        self.assertIsInstance(maze, np.ndarray)

        time.sleep(0.2)

        # assert that the maze is correct
        maze_file = f"maze_{width}x{height}-seed={seed}.png"
        self.assertTrue(file_input_generation.generate_maze_from_image(maze_file, False))

        # assert that the maze is saved with the correct name
        self.assertTrue(os.path.exists(maze_file))

        os.remove(maze_file)

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
    def test_no_threshold(self, width, height):
        entrance, exit, path_length, total_path_tiles, maze = random_generation.generate_maze(
            None, width, height, 0,  True)
        
        # assert that the maze is a numpy array
        self.assertIsInstance(maze, np.ndarray)

        time.sleep(0.2)

        # assert that there are no special tiles
        self.assertTrue(np.all(np.isin(maze, [0, 255, 64, 182])))

        # assert that the maze is correct
        maze_file = f"maze_{width}x{height}-seed=default-test.png"
        self.assertTrue(file_input_generation.generate_maze_from_image(maze_file, False))

        # delete the generated maze
        os.remove(maze_file)

    @parameterized.expand([
        (4, 4, 0),
        (10, 10, 1),
        (15, 15, 1),
        (20, 20, 2),
        (35, 35, 3),
        (50, 50, 4),
        (65, 65, 4),
        (75, 75, 4),
        (80, 80, 5),
        (100, 100, 6),
    ])
    def test_threshold(self, width, height, max_threshold):
        entrance, exit, path_length, total_path_tiles, maze = random_generation.generate_maze(
            None, width, height, max_threshold, True)

        time.sleep(0.2)

        # assert that the maze is a numpy array
        self.assertIsInstance(maze, np.ndarray)

        allowed_values = {0, 255, 64, 182, 16, 32, 224, 90}
        allowed_values.update(range(96, 116))
        allowed_values.update(range(150, 170)) 

        # assert that there are special tiles
        self.assertTrue(np.all(np.isin(maze, list(allowed_values))))

        # assert that the maze is correct
        maze_file = f"maze_{width}x{height}-seed=default-test.png"
        self.assertTrue(file_input_generation.generate_maze_from_image(maze_file, False))

        # delete the generated maze
        os.remove(maze_file)

if __name__ == '__main__':
    unittest.main(verbosity=2)
