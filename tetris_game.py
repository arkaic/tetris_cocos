from random import randrange

import cocos
from cocos import layer, scene
from cocos.sprite import Sprite
from cocos.director import director
from cocos.actions import Place
from pyglet import window

import tetrofactory

class Square(object):
    """ 
    The bounding_coord represents its location in an abstract bounding square
    centered on the origin 0,0. It is for the purposes of rotation
    """

    # todo: refactor SquareSprite into composition instead of inheritance.
    # remove bounding_coord and keep that Block-side. Square sprite could also
    # be renamed Square. keep a reference to the Block and its own grid coord
    # use properties

    _block = None
    _sprite = None
    _x = None    # coordinates on the tetris grid
    _y = None

    def __init__(self, image, block, loc):
        self._sprite = Sprite(image, position=(0, 0), rotation=0, scale=1, 
                              opacity=255, color=(255, 255, 255), anchor=None)
        self._block = block
        self._x, self._y = loc

    @property
    def x(self):
        return self._x
    @x.setter
    def x(self, value):
        self._x = value

    @property
    def y(self):
        return self._y
    @y.setter
    def y(self, value):
        self._y = value

    @property
    def sprite(self):
        return self._sprite
    @sprite.setter
    def sprite(self, value):
        self._sprite = value


class Block:
    """ References all SquareSprites and their location on the model 2D array.
    Sprites will exist inside an abstract bounding square that this class defines,
    depending on the type of block.

    Each block will have following attributes:
     * Bounding square coordinates for each sprite, relative to origin point 0,0.
     * Sprite grid coordinate that the origin point is mapped to.
     * A single grid location coordinate that is used as the block's actual 
       location in the grid. When the block moves, it's just this coordinate that 
       moves. It is also defined as the origin point in the abstract bounding 
       square and it is the sprites that are offsetted from this coordinate, 
       giving the appearance of moving or rotating the block.

    The abstract bounding square is used to manipulate how a specific block 
    should rotate. Apparently, there ARE standards on how each rotates, which
    can be found in the tetris wikia. I'm using the most common one, which is
    what originally defined this abstract bounding square.
    """

    name = None
    board_layer = None     # cocos parent layer
    squares_matrix = None     # references the Board layer's grid (model)
    squares = None  # list of all squares for the block (Sprite)

    # below fields are set by factory
    _location = None
    _bounding_locations_map = dict()  # maps square -> bounding location 

    def __init__(self, block_name, tetrisboardlayer):
        self.name = block_name
        self.board_layer = tetrisboardlayer
        self.squares_matrix = tetrisboardlayer.squares_matrix
        self.squares = []

    @property
    def location(self):
        return self._location
    @location.setter
    def location(self, value):
        self._location = value

    @property
    def bounding_locations_map(self):
        return self._bounding_locations_map
    @bounding_locations_map.setter
    def bounding_locations_map(self, value):
        self._bounding_locations_map = value

    def move(self, direction):
        if not self.can_move(direction):
            return False

        # Erase
        for square in self.squares:
            self.squares_matrix[square.x][square.y] = None

        prev_loc_x, prev_loc_y = self.location
        for square in self.squares:
            if direction == 'LEFT':
                self.location = (prev_loc_x - 1, prev_loc_y)
            elif direction == 'RIGHT':
                self.location = (prev_loc_x + 1, prev_loc_y)
            elif direction == 'DOWN':
                self.location = (prev_loc_x, prev_loc_y - 1)
            square.x, square.y = self.location
            self.squares_matrix[square.x][square.y] = square

        return True

    def can_move(self, direction):
        # TODO refactor lines around for terseness
        for square in self.squares:
            if direction == 'LEFT':
                if square.x <= 0:
                    return False
                if (not self._has_square_in_location((square.x - 1, square.y)) and
                        self.squares_matrix[square.x - 1][square.y] is not None):
                    # if shifted position of square is not in block and there's
                    # something in that shifted coordinate, can't move block
                    return False
            elif direction == 'RIGHT':
                if square.x >= self.board_layer.width - 1:
                    return False
                if (not self._has_square_in_location((square.x + 1, square.y)) and
                        self.squares_matrix[square.x + 1][square.y] is not None):
                    return False
            elif direction == 'DOWN':
                if square.y <= 0:
                    return False
                if (not self._has_square_in_location((square.x, square.y - 1)) and
                        self.squares_matrix[square.x][square.y - 1] is not None):
                    return False
        return True

    def rotate(self, direction):
        """ 
        Formula for I and O blocks
        newXccw = centerX + centerY - y
        newYccw = centerY - centerX + x
        newXcw  = centerX - centerY + y
        newYcw  = centerX + centerY - x
        Formula for rest
        ccw =>   x,y => -y, x
        cw  =>   x,y =>  y,-x
        """

        if not self._can_rotate(direction):
            print("can't rotate")
            return False

        # Erase
        for square in self.squares:
            self.squares_matrix[square.x][square.y] = None

        # Rotate using formulas above
        for square in self.squares:
            # Calculate new bounding coordinates
            bound_x, bound_y = self.bounding_locations_map[square]
            rotated_bound_x, rotated_bound_y = None, None
            if direction == 'CLOCKWISE':
                rotated_bound_x = bound_y
                if self.name == 'I' or self.name == 'O':
                    rotated_bound_y = 1 - bound_x
                else:
                    rotated_bound_y = -1 * bound_x
            elif direction == 'COUNTERCLOCKWISE':
                if self.name == 'I' or self.name == 'O':
                    rotated_bound_x = 1 - bound_y
                else:
                    rotated_bound_x = -bound_y
                rotated_bound_y = bound_x

            # Update bounding locations in the block's dictionary and square's
            # location coordinates on the square matrix
            self.bounding_locations_map[square] = (rotated_bound_x, rotated_bound_y)
            square.x = rotated_bound_x + block.location[0]
            square.y = rotated_bound_y + block.location[1]
            self.squares_matrix[square.x][square.y] = square

        return True

    def _can_rotate(self, direction):
        """ Formula for I and O block
        centerX and centerY = 0.5
        newXccw = centerX + centerY - y = 1 - y
        newYccw = centerY - centerX + x = x
        newXcw  = centerX - centerY + y = y
        newYcw  = centerX + centerY - x = 1 - x
        Formula for rest
        ccw =>   x,y => -y, x
        cw  =>   x,y =>  y,-x
        """
        for square in self.squares:
            bound_x, bound_y = self.bounding_locations_map[square]
            if direction == 'CLOCKWISE':
                rotated_bound_x = bound_y
                if self.name == 'I' or self.name == 'O':
                    rotated_bound_y = 1 - bound_x
                else:
                    rotated_bound_y = -bound_x
            elif direction == 'COUNTERCLOCKWISE':
                if self.name == 'I' or self.name == 'O':
                    rotated_bound_x = 1 - bound_y
                else:
                    rotated_bound_x = -bound_y
                rotated_bound_y = bound_x

            if not self._has_square_in_location((rotated_bound_x, rotated_bound_y)):
                # if not part of the block, check if rotated coordinates fit within
                # tetris grid and if the square in the square matrix matches any
                # of the squares this block currently holds
                rotated_x = rotated_bound_x + self.location[0]
                rotated_y = rotated_bound_y + self.location[1]

                if rotated_x < 0 or rotated_x >= self.board_layer.width:
                    return False
                if (self.squares_matrix[rotated_x][rotated_y] is not None and
                        self.squares_matrix[rotated_x][rotated_y] not in self.squares):
                    return False
        return True

    def _has_square_in_location(self, location):
        for square in self.squares:
            if location[0] == square.x and location[1] == square.y
        return False


class DigitSquareGroup:
    """ Holds a group of smaller square sprites arranged to represent a digit. 
    This is for showing the score on the upper right, during the game
     *   *
    * *  *
    * *  *
    * *  *
     *   *
    """

    class DigitSquare(object):
         def __init__(self, image, bounding_loc):
            self._sprite = Sprite(image, position=(0, 0), rotation=0, scale=1, 
                                  opacity=255, color=(255, 255, 255), anchor=None)
            self._bounding_location = bounding_loc

    bounding_map = {
        0: [(1, 0), (0, 1), (2, 1), (0, 2), (2, 2), (0, 3), (2, 3), (1, 4)],
        1: [(1, 0), (1, 1), (1, 2), (1, 3), (1, 4)],
        2: [(1, 0), (2, 0), (0, 1), (1, 2), (2, 3), (0, 4), (1, 4), (0, 2)],
        3: [(0, 0), (1, 0), (2, 1), (1, 2), (2, 3), (0, 4), (1, 4)],
        4: [(2, 0), (2, 1), (0, 2), (1, 2), (2, 2), (0, 3), (2, 3), (0, 4), (2, 4)],
        5: [(0, 0), (1, 0), (2, 1), (1, 2), (0, 3), (1, 4), (2, 4), (0, 2)],
        6: [(1, 0), (0, 1), (2, 1), (0, 2), (1, 2), (0, 3), (1, 4), (2, 4)],
        7: [(0, 0), (0, 1), (1, 2), (2, 3), (0, 4), (1, 4), (2, 4)],
        8: [(1, 0), (0, 1), (2, 1), (1, 2), (0, 3), (2, 3), (1, 4)],
        9: [(0, 0), (1, 0), (2, 1), (1, 2), (2, 2), (0, 3), (2, 3), (1, 4)]
    }
    digit = None
    digit_squares = None
    atoms = None
    bounding_locations = None

    def __init__(self, digit, atoms):
        if digit < 0 or digit > 9:
            raise ShouldntHappenError("Digit is wrong")

        self.digit = digit
        self.digit_squares = []
        self.atoms = atoms

        self.bounding_locations = self.bounding_map[digit]

        img = self.atoms.cells[0][digit].tile.image
        for loc in self.bounding_locations:
            self.digit_squares.append(DigitSquare(img, loc))


class TetrisBoardLayer(layer.ScrollableLayer):
    """ The code isn't very MVC, but it does keep a simple model matrix data 
    structure, the squares_matrix, to hold the Squares.
    """

    width = 10
    height = 22
    keydelay_interval = .25
    start_block_name = 'T'
    is_event_handler = True
    key_pressed = None
    squares_matrix = None     # MODEL
    current_block = None
    tetris_maplayer = None
    sandbox = None   # Palette for block creation
    atoms = None  # Palette for graphically representing numeral score
    score = None
    existing_blocks = []
    digit_sprite_sets = []
    chosen_digits = []

    def __init__(self, xmlpath):
        super(TetrisBoardLayer, self).__init__()

        # width | [length -------> ] 
        #       | [                ]
        #       v [                ]

        self.squares_matrix = [[None for y in range(self.height)] for x in range(self.width)]
        r = cocos.tiles.load(xmlpath)
        self.tetris_maplayer = r['map0']  # TODO 'map0' is hardcoded
        self.add(self.tetris_maplayer)
        self.sandbox = r['sandbox']  # Used as the palette
        self.score = 0

        # Set size and show the grid
        x, y = cocos.director.director.get_window_size()
        self.tetris_maplayer.set_view(0, 0, x, y)

        # Add group of sprites based on current block
        self._new_block(self.start_block_name)

        # Set up scoreboard
        for x in range(3):
            digits = []
            for y in range(10):
                digits.append(DigitSquareGroup(y, r['atoms']))
            self.digit_sprite_sets.append(digits)

        self._display_score()

        # Schedule timed drop of block
        self.schedule_interval(self._timed_drop, .4)

    def on_key_press(self, key, modifiers):
        # Note: finishes execution when key pressed and only once, even if held
        if not self.key_pressed:
            self.key_pressed = window.key.symbol_string(key)
            if self.key_pressed == 'DOWN':
                self._move_block('DROP')
            else:
                self._move_block(self.key_pressed)
            self.schedule_interval(self._button_held, self.keydelay_interval)

    def on_key_release(self, key, modifiers):
        self.key_pressed = None
        self.unschedule(self._button_held)

    def _move_block(self, direction):
        if direction == 'LEFT':
            # Does the movement in conditionals
            if self.current_block.move('LEFT'):
                # Now do the rendering for each square
                for square in self.current_block.squares:
                    texture_cell = self.tetris_maplayer.cells[square.x][square.y]
                    square.sprite.do(Place((texture_cell.x + 9, texture_cell.y + 9)))
        elif direction == 'RIGHT':
            if self.current_block.move('RIGHT'):
                for square in self.current_block.squares:
                    texture_cell = self.tetris_maplayer.cells[square.x][square.y]
                    square.sprite.do(Place((texture_cell.x + 9, texture_cell.y + 9)))
        elif direction == 'DOWN':
            if self.current_block.move('DOWN'):
                for square in self.current_block.squares:
                    texture_cell = self.tetris_maplayer.cells[square.x][square.y]
                    square.sprite.do(Place((texture_cell.x + 9, texture_cell.y + 9)))
        elif direction == 'UP':
            # rotate clockwise only
            if self.current_block.rotate('CLOCKWISE'):
                for square in self.current_block.squares:
                    texture_cell = self.tetris_maplayer.cells[square.x][square.y]
                    square.sprite.do(Place((texture_cell.x + 9, texture_cell.y + 9)))
        elif direction == 'DROP':
            while self.current_block.can_move('DOWN'):
                self._move_block('DOWN')

            # Each clear can produce new lines so iteratively clear.
            while True:
                numlines = self._clear_lines()
                if numlines == 0:
                    break
                # Increment and display score
                self.score += numlines
                self._display_score()

            self.current_block = None
            self._new_block()

    def _new_block(self, blockname=None):
        """ Note: This should be called when self.current_block == None
        All conditions:
          name=None, current exists => nothing happens
          name=None, no current => get random
          name=<name>, current exists => nothing happens
          name=<name>, no current => use supplied
        """

        if self.current_block:
            raise ShouldntHappenError("Getting a new block without removing current")
        self.current_block = tetrofactory.makeblock(self, name=blockname)
        self.existing_blocks.append(self.current_block)

        # Draw sprites on layer
        for square in self.current_block.squares:
            texture_cell = self.tetris_maplayer.cells[square.x][square.y]
            square.position = (texture_cell.x + 9, texture_cell.y + 9)
            self.add(square, z=1)

    def _clear_lines(self):
        """ Clear any complete lines and collapse the squares as a result """

        # Get list of y coordinates to clear. If there are any holes in a line,
        # move one.
        rows_to_clear = []  # will hold y coordinates
        for y in range(len(self.squares_matrix[0])):
            for x in range(len(self.squares_matrix)):
                if self.squares_matrix[x][y] is None:
                    break
                if x == len(self.squares_matrix) - 1:
                    rows_to_clear.append(y)

        if not rows_to_clear:
            return 0

        # Clear lines
        for y in rows_to_clear: 
            for x in range(len(self.squares_matrix)):
                try:
                    self.remove(self.squares_matrix[x][y])
                except Exception:
                    print('Sprite is not a child when clearing')
                    square = self.squares_matrix[x][y]
                    print('coord:({},{})\n'.format(square.x, square.y))
                    raise ShouldntHappenError("Shouldn't happen error, closing")
                # Library function remove() doesn't nullify parent
                self.squares_matrix[x][y].parent = None
                self.squares_matrix[x][y] = None

        # TODO comment out or delete once new collapse sticky comes in?
        # Remove cleared sprites from their blocks
        blocks_to_remove = []
        for block in self.existing_blocks:
            if not block.squares:
                blocks_to_remove.append(block)
            else:
                squares_to_remove = []
                for square in block.squares:
                    if not square.sprite.parent:
                        squares_to_remove.append(square)
                for square in squares_to_remove:
                    block.squares.remove(square)
                if not block.squares:
                    blocks_to_remove.append(block)
        for block in blocks_to_remove:
            self.existing_blocks.remove(block)

        #-----------------------------------------------------------------------
        #                              Collapsing
        # Shifts down every block above the row lines (line_ys). Keeps track 
        # of a base row that determines which squares to shift down
        # rows_to_clear, 
        #-----------------------------------------------------------------------
        prev_y = None
        base_y = rows_to_clear[0] 
        for y in rows_to_clear: 
            if prev_y is not None:
                base_y += (y - prev_y - 1)

            for block in self.existing_blocks:
                for square in block.squares:
                    # Forget sprites lower than the clear line
                    if square.y < base_y:
                        continue

                    # Move square down on square grid by removing it and putting
                    # it in its new position.
                    new_x, new_y = (square.x, square.y - 1)
                    if self.squares_matrix[square.x][square.y] is square:
                        # The square may not be in its original location because
                        # it could have been replaced by another square above it
                        # and within the same block, which is why the check.
                        self.squares_matrix[square.x][square.y] = None
                    square.x, square.y = (new_x, new_y)
                    self.squares_matrix[new_x][new_y] = square

                    # Do the rendering
                    texture_cell = self.tetris_maplayer.cells[new_x][new_y]
                    square.sprite.do(Place((texture_cell.x + 9, texture_cell.y + 9)))
            prev_y = y

        # Assert no rows 
        # try:
            # for 
        # except AssertionError:
            # TODO: helpful log reports for this
            # exit()
        
        return len(rows_to_clear)  # numlines

    def _collapse(self, rows_to_clear):
        """ Sticky method: identify all clumps above each cleared row and drop 
        them independently. More specifically, round robin drop them one square
        at a time. The round robin order starts with clumps above first complete
        line, then above second line and so on.
        """

        # todo identify clumps and add to clump list: start with a square and
        # recursively find non-diagonally adjacent neighbor squares: recursive
        # implementation can do a flood scan until no more unvisited cells left
        # to go to. 
        # (?also keep track of squares that have empty space below them?) 
        for y in rows_to_clear:
            pass

        # todo round robin: while loop and use modulus. Keep a counter of 
        # consecutive moveable clumps visited. Once counter == total number of 
        # clumps, end. Moveable is defined as ALL "bottom squares" of a clump having
        # currently empty space below them. 
        # if clump is moveable

    def _display_score(self):
        """ Erase previous three digits and display new ones """

        # Erase
        for digit in self.chosen_digits:
            for sprite in digit.sprites:
                self.remove(sprite)
        self.chosen_digits = []

        # Format score for 3 digit manipulation
        strscore = str(self.score)
        if len(strscore) < 3:
            if len(strscore) == 2:
                strscore = '0' + strscore
            elif len(strscore) == 1:
                strscore = '00' + strscore

        # Display three digits
        offsetpx_x, offsetpx_y = 250, 200
        for i in range(3):
            digit_int = int(strscore[i])
            digit = self.digit_sprite_sets[i][digit_int]
            self.chosen_digits.append(digit)
            for sprite in digit.sprites:
                x, y = sprite.bounding_coord
                sprite.position = (offsetpx_x + x * 9, offsetpx_y + y * 9)
                self.add(sprite, z=1)
            offsetpx_x += 40

    def _timed_drop(self, dt):
        if self.current_block.can_move('DOWN'):
            self._move_block('DOWN')
        else:
            self._move_block('DROP')

    def _button_held(self, dt):
        if self.key_pressed:
            if self.key_pressed == 'DOWN':
                self._move_block('DROP')
            else:
                self._move_block(self.key_pressed)

    def _board_to_string(self):
        s = ""
        for y in range(len(self.squares_matrix[0])):
            row = '|'
            for x in range(len(self.squares_matrix)):
                if self.squares_matrix[x][y] is None:
                    row += ' |'
                else:
                    row += '*|'
            s = row + '\n' + s
        return s


class ShouldntHappenError(UserWarning):
    pass


#===============================================================================
#===========                    MAIN SCRIPT                     ================
#===============================================================================

if __name__ == '__main__':
    director.init(resizable=True)
    tetris_board = TetrisBoardLayer('tetris.xml')
    scroller = layer.ScrollingManager()
    scroller.set_focus(100, 200)
    scroller.add(tetris_board)

    s = layer.ScrollableLayer()
    scroller.add(s)

    director.run(scene.Scene(scroller))
