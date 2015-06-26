# __author__ = 'henry'

import sys
from time import sleep

# Todo when board sets a block, draw. and other places that need draw too
# todo get python to clear screen during render.
# todo make these two classes as modular as possible
# todo get sleep timer
# todo process_input gets command line inputs

"""
   Movement and placement of the block on the board will depend on the
   block's board_location.
"""

class Block:
    char = ""             # l j i o s z t
    board_location = []   # x,y point
    unit_coords = []      # x,y points

    def __init__(self, block_type):
        self.char = block_type
        self.board_location = [5, 2]
        if block_type == 'l':
            self.unit_coords = [[0,0], [1,0], [0,1], [0,2]]
        elif block_type == 'j':
            self.unit_coords = [[0,0], [-1,0], [0,1], [0,2]]
        elif block_type == 'i':
            self.unit_coords = [[0,0], [0,1], [0,-1], [0,-2]]
        elif block_type == 'o':
            self.unit_coords = [[0,0], [0,1], [1,0], [1,1]]
        elif block_type == 's':
            self.unit_coords = [[0,0], [0,-1], [-1,-1], [1,0]]
        elif block_type == 'z':
            self.unit_coords = [[0,0], [-1,0], [0,-1], [1,-1]]
        elif block_type == 't':
            self.unit_coords = [[0,0], [-1,0], [1,0], [0,1]]

    def board_coords(self):
        bc = []
        for coord in self.unit_coords:
            x = coord[0] + self.board_location[0]
            y = coord[1] + self.board_location[1]
            bc.append([x, y])
        return bc

    def rotate(self, direction):
        if direction == 'clockwise':
            transform = [[0,-1], [1,0]]
        elif direction == 'counterclockwise':
            transform = [[0,1], [-1,0]]
        else:
            return
        rotated_unit_coords = []
        for x, y in self.unit_coords:
            rotated_x = x * transform[0][0] + y * transform[0][1]
            rotated_y = x * transform[1][0] + y * transform[1][1]
            rotated_unit_coords.append([rotated_x, rotated_y])
        print("Rotated coordinates: {0} -> {1}".format(rotated_unit_coords, self.unit_coords))
        self.unit_coords = rotated_unit_coords

    def can_move(self, direction, board):
        board_coords = self.board_coords()
        for coord in board_coords:
            x, y = coord
            if direction == 'left':
                moved_coord = [x - 1, y]
            elif direction == 'right':
                moved_coord = [x + 1, y]
            elif direction == 'down':
                moved_coord = [x, y + 1]
            else:
                return False

            if moved_coord in board_coords:
                continue
            if (direction == 'down') and moved_coord[1] > 21:
                return False
            if ((direction == 'right' or direction == 'left') and
                    (moved_coord[0] > 9 or moved_coord[0] < 0)):
                return False
            if board.matrix[moved_coord[0]][moved_coord[1]] != ' ':
                return False
        return True



class Board:
    height = 22
    width = 10
    matrix = None
    _current_block = None
    line_ys = []  # Holds the y-coords of cleared lines for a block drop
    clear_char = ' '

    def __init__(self):
        self.matrix = [[' ' for y in range(self.height)] for x in range(self.width)]

    def __str__(self):
        s = ' 0 1 2 3 4 5 6 7 8 9\n'
        for y in range(self.height):
            s += '|'
            for x in range(self.width):
                s += ' ' + self.matrix[x][y]
            s += '|\n'
        s += ' - - - - - - - - - -\n'
        return s

    def move_block_down(self):
        if not self._current_block:
            return False
        if self._current_block.can_move('down', self):
            self._draw(' ')
            self._current_block.board_location[1] += 1
            self._draw(self._current_block.char)
            return True
        else:
            return False

    def move_block_right(self):
        if not self._current_block:
            return False
        if self._current_block.can_move('right', self):
            self._draw(' ')
            self._current_block.board_location[0] += 1
            self._draw(self._current_block.char)
            return True
        else:
            return False

    def move_block_left(self):
        if not self._current_block:
            return False
        if self._current_block.can_move('left', self):
            self._draw(' ')
            self._current_block.board_location[0] -= 1
            self._draw(self._current_block.char)
            return True
        else:
            return False

    def rotate_block(self, direction):
        self._draw(self.clear_char)
        self._current_block.rotate(direction)
        self._draw(self._current_block.char)

    def drop_block(self):
        if not self._current_block.can_move('down', self):
            self._current_block = None
            return False
        else:
            while self._current_block.can_move('down', self):
                self.move_block_down()
            self._current_block = None
            return True

    # todo untested
    def has_lines(self):
        for y in range(2, self.height):
            if self._line_is_complete(y):
                return True
            else:
                continue
        return False

    # todo untested
    def clear_lines(self):
        self.line_ys = []
        for y in range(2, self.height):
            if self._line_is_complete(y):
                for x in range(self.width):
                    self.matrix[x][y] = ' '
                self.line_ys.append(y)
            else:
                continue
        return len(self.line_ys)

    def can_block_move(self, direction):
        return self._current_block.can_move(self, direction)

    # called only after clear_lines
    def collapse_board(self):
        if not self.line_ys:
            return False
        self.line_ys.sort(reverse=True)
        for line_y in self.line_ys:
            for y in range(line_y - 1, -1, -1):
                for x in range(10):
                    self.matrix[x][y+1] = self.matrix[x][y]
        return True

    def new_block(self, block=None):
        if self._current_block:
            # if ever I wanted a new block without cleaning up first
            return
        if block is None:
            # todo get new random block
            pass
        else:
            self._current_block = block
            self._draw(block.char)

    def _draw(self, char):
        for x, y in self._current_block.board_coords():
            self.matrix[x][y] = char

    def _line_is_complete(self, y):
        for x in range(self.width):
            if self.matrix[x][y] == ' ':
                return False
            else:
                if x == self.width - 1:
                    return True
                else:
                    continue


################################################################################


def process_input(board):
    # todo
    pass
def update(board):
    # todo
    # if input, update
    # if no input and if time is at one second interval, move block down
    pass
def render(board):
    # todo
    # print matrix, or render own graphical stuff
    pass

def game_loop():
    board = Board()
    while True:
        process_input(board)
        update(board)
        render(board)
        sleep(1)

def run():
    if len(sys.argv) == 2:
        if sys.argv[1] == '-t':
            test2()
    elif len(sys.argv) == 1:
        game_loop()

if __name__ == '__main__':
    run()
