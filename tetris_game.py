import sys

import cocos
from cocos import layer, scene
from cocos.sprite import Sprite
from cocos.director import director
from cocos.actions import Place
from pyglet import window

import tetrofactory

class Square:
    """ 
    The bounding_coord represents its location in an abstract bounding square
    centered on the origin 0,0. It is for the purposes of rotation
    """

    _block = None
    _sprite = None
    _x = None    # coordinates on the tetris grid
    _y = None
    # debug purposes
    x_history = None
    y_history = None

    def __init__(self, image, block, loc):
        self._sprite = Sprite(image, position=(0, 0), rotation=0, scale=1, 
                              opacity=255, color=(255, 255, 255), anchor=None)
        self._block = block
        self.x_history = list()
        self.y_history = list()
        self.x = loc[0]
        self.y = loc[1]

    @property
    def x(self):
        return self._x
    @x.setter
    def x(self, value):
        self._x = value
        # self.x_history.append(value)

    @property
    def y(self):
        return self._y
    @y.setter
    def y(self, value):
        self._y = value
        if value < 0: 
            raise ShouldntHappenError("y assigned value < 0")
            sys.exit()

    @property
    def sprite(self):
        return self._sprite
    @sprite.setter
    def sprite(self, value):
        self._sprite = value

    @property
    def block(self):
        return self._block
    

class Block:
    """ 
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

    #---------------------------------------------------------------------------
    #       Properties                             
    #---------------------------------------------------------------------------

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

    #---------------------------------------------------------------------------
    #       Public                                    
    #---------------------------------------------------------------------------

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

    def move(self, direction):
        if not self.can_move(direction):
            return False

        # Erase from matrix first
        for square in self.squares:
            self.squares_matrix[square.x][square.y] = None

        # Calculate new location for block
        prev_x, prev_y = self.location
        if direction == 'LEFT':
            self.location = (prev_x - 1, prev_y)
        elif direction == 'RIGHT':
            self.location = (prev_x + 1, prev_y)
        elif direction == 'DOWN':
            self.location = (prev_x, prev_y - 1)

        # For all of block's squares, update their mappings, fields, and put them
        # back into the matrix in their new location
        for square in self.squares:
            square_bounding_x, square_bounding_y = self.bounding_locations_map[square]
            square.x = square_bounding_x + self.location[0]
            square.y = square_bounding_y + self.location[1]
            self.squares_matrix[square.x][square.y] = square

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
            square.x = rotated_bound_x + self.location[0]
            square.y = rotated_bound_y + self.location[1]
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


            rotated_x = rotated_bound_x + self.location[0]
            rotated_y = rotated_bound_y + self.location[1]
            if not self._has_square_in_location((rotated_x, rotated_y)):
                # If new rotated coordinates DOES match any of the block's own
                # squares, then GREAT!
                # Otherwise, we're in here. Make sure it's not outside of tetris
                # grid dimensions and if its location in the square matrix is not
                # taken up by a square not in block

                if rotated_x < 0 or rotated_x >= self.board_layer.width:
                    return False
                if self.squares_matrix[rotated_x][rotated_y] is not None:
                    if self.squares_matrix[rotated_x][rotated_y] not in self.squares:
                        return False
                    else:
                        msg = "A square's location doesn't match its square matrix location"
                        raise ShouldntHappenError(msg)

        return True

    def _has_square_in_location(self, location):
        for square in self.squares:
            if square.x == location[0] and square.y == location[1]:
                return True
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
            self.sprite = Sprite(image, position=(0, 0), rotation=0, scale=1, 
                                  opacity=255, color=(255, 255, 255), anchor=None)
            self.bounding_location = bounding_loc

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
            self.digit_squares.append(self.DigitSquare(img, loc))


class TetrisBoardLayer(layer.ScrollableLayer):
    """ The code isn't very MVC, but it does keep a simple model matrix data 
    structure, the squares_matrix, to hold the Squares.
    """

    width = 10
    height = 22
    start_block_name = 'T'
    other_start_names = ['I', 'S', 'Z']
    # Event stuff
    keydelay_interval = .25
    is_event_handler = True
    key_pressed = None
    # Logic stuff
    squares_matrix = None     # MODEL
    current_block = None
    existing_blocks = []
    # Rendering stuff
    tetris_maplayer = None
    sandbox = None   # Palette for block creation (rendering stuff)
    # digit stuff
    digit_sprite_sets = []
    chosen_digits = []
    atoms = None  # Palette for graphically representing numeral score
    score = None

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

        # Set up scoreboard. Specifically, digit_sprite_sets shall hold 3 lists
        # of 10 DigitSquareGroup objects, one for each decimal symbol
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
            # debug
            if self.other_start_names:
                self._new_block(self.other_start_names.pop())
            else:
                self._new_block()

    def _new_block(self, blockname=None):
        """ Note: This should be called when self.current_block == None
        All conditions:
          name=None, current exists => nothing happens
          name=None, no current => get random
          name=<name>, current exists => nothing happens
          name=<name>, no current => use supplied
          tisz
        """

        if self.current_block:
            raise ShouldntHappenError("Getting a new block without removing current")
        self.current_block, gameover = tetrofactory.make_tetris_block(self, name=blockname)
        self.existing_blocks.append(self.current_block)

        # Draw sprites on layer
        for square in self.current_block.squares:
            texture_cell = self.tetris_maplayer.cells[square.x][square.y]
            square.sprite.position = (texture_cell.x + 9, texture_cell.y + 9)
            self.add(square.sprite, z=1)

        if gameover:
            # todo, exit game or go to menu
            print('GAMEOVER')
            exit()

        print(self._board_to_string('New block: %s' % self.current_block.name))

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
                    square = self.squares_matrix[x][y]
                    self.remove(square.sprite)
                except Exception:
                    print('----------------------------------------------')
                    print('Error trying to remove square.sprite from layer')
                    print('Referenced sprite to be cleared: {}'.format(square.sprite))
                    print("Sprite's block: %s" % square.block.name)
                    square = self.squares_matrix[x][y]
                    print("square.(x,y):({},{})".format(square.x, square.y))
                    print("referenced (x,y):({},{})\n".format(x, y))
                    print(self._board_to_string())
                    if len(square.x_history) != len(square.y_history):
                        print('square x and y histories do not match')
                    else:
                        print('history size =', len(square.x_history))
                        print('x   y')
                        for i in range(len(square.x_history)):
                            print('{}   {}'.format(square.x_history[i], square.y_history[i]))
                    print('----------------------------------------------')
                    raise ShouldntHappenError("Either square is None or can't remove its sprite from layer")
                # Library function remove() doesn't nullify parent
                self.squares_matrix[x][y].sprite.parent = None
                self.squares_matrix[x][y] = None

        print(self._board_to_string('clear lines'))

        # TODO comment out or delete once new collapse sticky comes in?
        # Clear out "dead" squares that each existing block holds. If a block has
        # no more squares left, remove that block from existing blocks
        # print('%d existing blocks' % len(self.existing_blocks))
        blocks_to_remove = []
        totalremoved = 0
        for block in self.existing_blocks:
            # print('block: {}'.format(block.name))
            if not block.squares:
                blocks_to_remove.append(block)
                # print('   has no squares')
            else:
                squares_to_remove = []
                for square in block.squares:
                    if not square.sprite.parent:
                        squares_to_remove.append(square)
                totalremoved += len(squares_to_remove)
                for square in squares_to_remove:
                    block.squares.remove(square)
                if not block.squares:
                    blocks_to_remove.append(block)
        # assert that total removed is 10,20,30,40
        assert (totalremoved % self.width) == 0, '{} totalremove != {} width'.format(totalremoved, self.width)
        assert totalremoved <= 40
        for block in blocks_to_remove:
            self.existing_blocks.remove(block)

        self._collapse(rows_to_clear)

        print(self._board_to_string('After collapse'))

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

        def find_clumps(square):
            """ Iterative flood search to identify clump from given square """
            visited_squares = set()
            travel_stack = [square]
            while travel_stack:
                sq = travel_stack.pop()
                if sq in visited_squares:
                    continue

                visited_squares.add(sq)
                if sq.y - 1 >= 0 and self.squares_matrix[sq.x][sq.y - 1] is not None:
                    travel_stack.append(self.squares_matrix[sq.x][sq.y - 1])
                if sq.y + 1 < self.height and self.squares_matrix[sq.x][sq.y + 1] is not None:
                    travel_stack.append(self.squares_matrix[sq.x][sq.y + 1])
                if sq.x - 1 >= 0 and self.squares_matrix[sq.x - 1][sq.y] is not None:
                    travel_stack.append(self.squares_matrix[sq.x - 1][sq.y])
                if sq.x + 1 < self.width and self.squares_matrix[sq.x + 1][sq.y] is not None:
                    travel_stack.append(self.squares_matrix[sq.x + 1][sq.y])
            return list(visited_squares)

        def is_moveable(clump):
            for square in clump:
                # Not moveable if square is at bottom of grid or the square below
                # it is not part of clump
                if square.y == 0:
                    return False
                the_square_below = self.squares_matrix[square.x][square.y - 1]
                if the_square_below is not None and the_square_below not in clump:
                    return False
            return True

        def move(clump):
            # Erase
            for square in clump:
                self.squares_matrix[square.x][square.y] = None

            # Update square.y's
            # TODO refactor if I want to try to cascade method as well from this
            # code. I will need to update existing block locations.
            for square in clump:
                square.y = square.y - 1

            # add back to matrix in new locations
            for square in clump:
                self.squares_matrix[square.x][square.y] = square

        #-----------------------------------------------------------------------
        #                         Method: find_clumps() begin
        #-----------------------------------------------------------------------
        # identify clumps and add to clump list: start with a square and
        # recursively find non-diagonally adjacent neighbor squares: recursive
        # implementation can do a flood scan until no more unvisited cells left
        # to go to. 
        clumps = []  # list of lists of squares
        for y in rows_to_clear:
            for x in range(self.width):
                # print('({},{})'.format(x,y))
                # start square for recursive clump indentification procedure
                if y + 1 > self.height:
                    break
                square = self.squares_matrix[x][y + 1]
                if square is None:
                    continue

                exists_in_clump = False
                for clump in clumps:
                    if square in clump:
                        exists_in_clump = True
                        break
                if exists_in_clump:
                    continue

                new_clump = find_clumps(square)
                clumps.append(new_clump)

        # Assertion that clumps must be disjoint
        unionset = set()
        for clump in clumps:
            for sq in clump:
                if sq in unionset:
                    print("size of unionset={}".format(len(unionset)))
                    raise ShouldntHappenError('clumps share squares')
                else:
                    unionset.add(sq)

        # Keep a counter of 
        # consecutive moveable clumps visited. Once counter == total number of 
        # clumps, end. Moveable is defined as ALL "bottom squares" of a clump having
        # currently empty space below them. 
        # if clump is moveable, increment counter
        consecutive_counter = 0
        i = 0   # for modulus round robin indexing
        while consecutive_counter < len(clumps):
            clump = clumps[i % len(clumps)]
            if is_moveable(clump):
                move(clump)
                consecutive_counter = 0
            else:
                consecutive_counter += 1
            i += 1

        # render
        for clump in clumps:
            for square in clump:
                texture_cell = self.tetris_maplayer.cells[square.x][square.y]
                square.sprite.do(Place((texture_cell.x + 9, texture_cell.y + 9)))

    def _display_score(self):
        """ Erase previous three digits and display new ones """

        # Erase
        for digit in self.chosen_digits:
            for square in digit.digit_squares:
                self.remove(square.sprite)
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
            for square in digit.digit_squares:
                x, y = square.bounding_location
                square.sprite.position = (offsetpx_x + x * 9, offsetpx_y + y * 9)
                self.add(square.sprite, z=1)
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

    def _board_to_string(self, label=None):
        s = ""
        for y in range(len(self.squares_matrix[0])):
            row = '|'
            for x in range(len(self.squares_matrix)):
                if self.squares_matrix[x][y] is None:
                    row += ' |'
                else:
                    row += '*|'
            s = row + '\n' + s
        if label is not None:
            s = label + '\n' + s
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
