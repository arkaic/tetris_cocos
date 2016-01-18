import unittest

from tetris_game import *

class TestTetrisBoard(unittest.TestCase):

    def setUp(self):
        pass

    def test_collapse(self):
        # After a drop and before the next recursive clear (if there exists new
        # lines), assert no more clumps can move
        # If there are new lines, repeat.
        # Else, check that there are no empty rows
        # I could also identify all clumps in the board and make sure they can't move
        pass


if __name__ == '__main__':
    unittest.main()
