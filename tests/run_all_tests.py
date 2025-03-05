import unittest

from server_tests import ServerTestCase
from semi_random_generation_tests import SemiRandomGenerationTestCase
from random_generation_tests import RandomGenerationTestCase

if __name__ == '__main__':
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(ServerTestCase))
    suite.addTests(loader.loadTestsFromTestCase(SemiRandomGenerationTestCase))
    suite.addTests(loader.loadTestsFromTestCase(RandomGenerationTestCase))

    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
