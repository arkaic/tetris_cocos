# __author__ = 'henry'

import sys
from time import sleep
from random import randrange
from subprocess import call

# todo get python to clear screen during render.
# todo make these two classes as modular as possible
# todo get sleep timer
# todo process_input gets command line inputs
# rotation refinement = http://gamedev.stackexchange.com/questions/17974/how-to-rotate-blocks-in-tetris

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
        self.board_location = [5, 0]
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

class Board:
    height = 22
    width = 10
    matrix = None    
    line_ys = []  # Holds the y-coords of cleared lines for a block drop
    _clear_char = ' '
    current_block = None

    def __init__(self):
        self.matrix = [[' ' for y in range(self.height)] for x in range(self.width)]

    def __str__(self):
        s = '  0 1 2 3 4 5 6 7 8 9\n'
        for y in range(self.height):
            if y < 10:
                s += ' {}|'.format(y)
            else:
                s += '{}|'.format(y)
            for x in range(self.width):
                s += ' ' + self.matrix[x][y]
            s += '|\n'
        s += '  - - - - - - - - - -\n'
        return s

    def move_block_down(self):
        if not self.current_block:
            return False
        if self.can_move_block('down'):
            self._draw(' ')
            self.current_block.board_location[1] += 1
            self._draw(self.current_block.char)
            return True
        else:
            return False

    def move_block_right(self):
        if not self.current_block:
            return False
        if self.can_move_block('right'):
            self._draw(' ')
            self.current_block.board_location[0] += 1
            self._draw(self.current_block.char)
            return True
        else:
            return False

    def move_block_left(self):
        if not self.current_block:
            return False
        if self.can_move_block('left'):
            self._draw(' ')
            self.current_block.board_location[0] -= 1
            self._draw(self.current_block.char)
            return True
        else:
            return False

    def rotate_block(self, direction):
        self._draw(self.clear_char)
        self.current_block.rotate(direction)
        self._draw(self.current_block.char)

    # Note: this method should erase the current_block variable
    def drop_block(self):
        if not self.can_move_block('down'):
            self.current_block = None
            return False
        else:
            while self.can_move_block('down'):
                self.move_block_down()
            self.current_block = None
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

    def can_move_block(self, direction):
        board_coords = self.current_block.board_coords()
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
            if self.matrix[moved_coord[0]][moved_coord[1]] != ' ':
                return False
        return True

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

    # none supplied, current block => nothing happens
    # none supplied, no current => get random
    # supplied, current => nothing happens
    # supplied, no current => use supplied
    def new_block(self, blockchar=None):
        if self.current_block:
            raise ShouldntHappenError("Getting a new block without removing current")
            sys.exit()
        if blockchar is None:             
            r = randrange(0, 7)
            if r == 0:
                self.current_block = Block('l')
            elif r == 1:
                self.current_block = Block('j')
            elif r == 2:
                self.current_block = Block('i')
            elif r == 3:
                self.current_block = Block('o')
            elif r == 4:
                self.current_block = Block('s')
            elif r == 5:
                self.current_block = Block('z')
            elif r == 6:
                self.current_block = Block('t')
        else:
            self.current_block = Block(blockchar)
        self._draw(self.current_block.char)

    def _draw(self, char):
        for x, y in self.current_block.board_coords():
            if x >= 0 and y >= 0:
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

class ShouldntHappenError(UserWarning):
    pass


################################################################################


def process_input(board):
    # todo
    pass

def update(board):
    # todo if input, update
    # if no input and if time is at one second interval, move block down
    if board.current_block is None:
        board.new_block()
    if board.can_move_block('down'):
        board.move_block_down()
    else:
        board.drop_block()  # dropping erases block

def render(board):
    call(["clear"])
    print(board)    

def game_loop(time=1):
    board = Board()
    board.new_block('l')
    while True:
        process_input(board)
        update(board)
        render(board)
        sleep(time)        

def run():
    if len(sys.argv) == 1:
        game_loop()
    elif len(sys.argv) == 2:
        game_loop(float(sys.argv[1]))

if __name__ == '__main__':
    run()
