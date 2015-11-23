import cocos
from cocos import layer, scene
from cocos.sprite import Sprite
from cocos.director import director
from cocos.actions import Place
from random import randrange
from pyglet import window

# How I'm rendering: see docstrings in Tetris Board 

class SquareSprite(Sprite):
    """ The bounding_coord represents its location in an abstract bounding square
    centered on the origin 0,0. The grid_coord is the actual coordinate location
    on the sprite grid """

    bounding_coord = None
    grid_coord = None

    def __init__(self, image, coord, position=(0, 0), rotation=0, scale=1,
                 opacity=255, color=(255, 255, 255), anchor=None):
        super(SquareSprite, self).__init__(image, position=position, rotation=rotation,
                                           scale=scale, opacity=opacity, color=color,
                                           anchor=anchor)
        self.bounding_coord = coord


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

    char = None
    board_layer = None     # cocos parent layer
    sprite_grid = None     # references the Board layer's grid
    square_sprites = None  # list of all squares for the block (Sprite)
    _gridlocation_coord = None

    def __init__(self, block_char, tetrisboardlayer, rotated_state):
        self.char = block_char
        self.board_layer = tetrisboardlayer
        self.sprite_grid = tetrisboardlayer.sprite_grid
        self.square_sprites = []

        # Define the bounding square coordinates of the block
        init_bounding_coords = []
        img = None
        if self.char == 'I':
            self._gridlocation_coord = (4, 19)
            img = self.board_layer.sandbox.cells[0][0].tile.image
            init_bounding_coords = [(-1, 1), (0, 1), (1, 1), (2, 1)]
        elif self.char == 'J':
            self._gridlocation_coord = (4, 20)
            img = self.board_layer.sandbox.cells[0][1].tile.image
            init_bounding_coords = [(-1, 1), (-1, 0), (0, 0), (1, 0)]
        elif self.char == 'L':
            self._gridlocation_coord = (4, 20)
            img = self.board_layer.sandbox.cells[0][2].tile.image
            init_bounding_coords = [(-1, 0), (0, 0), (1, 0), (1, 1)]
        elif self.char == 'O':
            self._gridlocation_coord = (4, 20)
            img = self.board_layer.sandbox.cells[0][3].tile.image
            init_bounding_coords = [(0, 1), (0, 0), (1, 1), (1, 0)]
        elif self.char == 'S':
            self._gridlocation_coord = (4, 20)
            img = self.board_layer.sandbox.cells[0][4].tile.image
            init_bounding_coords = [(-1, 0), (0, 0), (0, 1), (1, 1)]
        elif self.char == 'T':
            self._gridlocation_coord = (4, 20)
            img = self.board_layer.sandbox.cells[0][6].tile.image
            init_bounding_coords = [(-1, 0), (0, 1), (0, 0), (1, 0)]
        elif self.char == 'Z':
            self._gridlocation_coord = (4, 20)
            img = self.board_layer.sandbox.cells[0][5].tile.image
            init_bounding_coords = [(-1, 1), (0, 1), (0, 0), (1, 0)]

        # Add sprites to both the member list and the grid model
        for bounding_coord in init_bounding_coords:
            sprite = SquareSprite(img, bounding_coord)
            self.square_sprites.append(sprite)
            sprite_x, sprite_y = self.grid_coord(sprite)
            self.sprite_grid[sprite_x][sprite_y] = sprite

    def move(self, direction):
        """ Move sprite on sprite grid (and visually too?)
        """
        if not self.can_move(direction):
            return False

        # Erase from sprite grid
        for sprite in self.square_sprites:
            sprite_x, sprite_y = self.grid_coord(sprite)
            sprite.grid_coord = None
            self.sprite_grid[sprite_x][sprite_y] = None

        # Put sprites into new locations by changing the grid location coord and 
        # offsetting every sprite by it again.
        prev_gridloc_x, prev_gridloc_y = self._gridlocation_coord
        for sprite in self.square_sprites:
            if direction == 'LEFT':
                self._gridlocation_coord = (prev_gridloc_x - 1, prev_gridloc_y)
            elif direction == 'RIGHT':
                self._gridlocation_coord = (prev_gridloc_x + 1, prev_gridloc_y)
            elif direction == 'DOWN':
                self._gridlocation_coord = (prev_gridloc_x, prev_gridloc_y - 1)
            sprite_x, sprite_y = self.grid_coord(sprite)
            self.sprite_grid[sprite_x][sprite_y] = sprite

        return True

    def can_move(self, direction):
        """ Sprite coordinates are made up of the grid location offset by the
        bounding coords
        """
        # TODO refactor lines around for terseness
        for sprite in self.square_sprites:
            sprite_x, sprite_y = self.grid_coord(sprite)
            if direction == 'LEFT':
                if sprite_x <= 0:
                    return False
                if (not self._is_a_block_coord((sprite_x - 1, sprite_y)) and
                        self.sprite_grid[sprite_x - 1][sprite_y] is not None):
                    # if shifted position of square is not in block and there's
                    # something in that shifted coordinate, can't move block
                    return False
            elif direction == 'RIGHT':
                if sprite_x >= self.board_layer.width - 1:
                    return False
                if (not self._is_a_block_coord((sprite_x + 1, sprite_y)) and
                        self.sprite_grid[sprite_x + 1][sprite_y] is not None):
                    return False
            elif direction == 'DOWN':
                if sprite_y <= 0:
                    return False
                if (not self._is_a_block_coord((sprite_x, sprite_y - 1)) and
                        self.sprite_grid[sprite_x][sprite_y - 1] is not None):
                    return False
        return True

    def rotate(self, direction):
        """ Formula for I and O block
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
        for sprite in self.square_sprites:
            sprite_x, sprite_y = self.grid_coord(sprite)
            sprite.grid_coord = None
            self.sprite_grid[sprite_x][sprite_y] = None

        # Rotate and reassign the bounding coords of the square. Then get the
        # grid coordinates and write the square into the model grid.
        for sprite in self.square_sprites:
            bound_x, bound_y = sprite.bounding_coord
            rotated_bound_x, rotated_bound_y = None, None
            if direction == 'CLOCKWISE':
                rotated_bound_x = bound_y
                if self.char == 'I' or self.char == 'O':
                    rotated_bound_y = 1 - bound_x
                else:
                    rotated_bound_y = -1 * bound_x
            elif direction == 'COUNTERCLOCKWISE':
                if self.char == 'I' or self.char == 'O':
                    rotated_bound_x = 1 - bound_y
                else:
                    rotated_bound_x = -bound_y
                rotated_bound_y = bound_x

            if direction == 'CLOCKWISE' or direction == 'COUNTERCLOCKWISE':
                sprite.bounding_coord = (rotated_bound_x, rotated_bound_y)
                sprite_x, sprite_y = self.grid_coord(sprite)
                self.sprite_grid[sprite_x][sprite_y] = sprite

        return True

    def grid_coord(self, sprite):
        if sprite in self.square_sprites:
            if sprite.grid_coord is None:
                sprite.grid_coord = (
                    sprite.bounding_coord[0] + self._gridlocation_coord[0],
                    sprite.bounding_coord[1] + self._gridlocation_coord[1])
            return sprite.grid_coord

    def bound_to_grid_coord(self, bound_coord):
        return (bound_coord[0] + self._gridlocation_coord[0],
                bound_coord[1] + self._gridlocation_coord[1])

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
        for sprite in self.square_sprites:
            bound_x, bound_y = sprite.bounding_coord
            if direction == 'CLOCKWISE':
                rotated_bound_x = bound_y
                if self.char == 'I' or self.char == 'O':
                    rotated_bound_y = 1 - bound_x
                else:
                    rotated_bound_y = -bound_x
            elif direction == 'COUNTERCLOCKWISE':
                if self.char == 'I' or self.char == 'O':
                    rotated_bound_x = 1 - bound_y
                else:
                    rotated_bound_x = -bound_y
                rotated_bound_y = bound_x

            if not self._is_a_block_coord((rotated_bound_x, rotated_bound_y)):
                # if not part of the block and the direction is correct
                rotated_sprite_x, rotated_sprite_y = self.bound_to_grid_coord((rotated_bound_x, rotated_bound_y))

                if rotated_sprite_x < 0 or rotated_sprite_x >= self.board_layer.width:
                    return False
                if (self.sprite_grid[rotated_sprite_x][rotated_sprite_y] is not None and
                        self.sprite_grid[rotated_sprite_x][rotated_sprite_y] not in self.square_sprites):
                    return False
        return True

    def _is_a_block_coord(self, grid_coord):
        for square in self.square_sprites:
            if grid_coord == self.grid_coord(square):
                return True
        return False


class DigitSpriteGroup:
    """ Holds a group of smaller square sprites arranged to represent a digit. 
    This is for showing the score on the upper right, during the game
     *   *
    * *  *
    * *  *
    * *  *
     *   *
    """
    digit = None
    sprites = None
    atoms = None

    def __init__(self, digit, atoms):
        if digit < 0 or digit > 9:
            raise ShouldntHappenError("Digit is wrong")

        self.digit = digit
        self.sprites = []
        self.atoms = atoms

        coords = []
        if digit == 0:
            coords = [(1, 0), (0, 1), (2, 1), (0, 2), (2, 2), (0, 3), (2, 3), (1, 4)]
        elif digit == 1:
            coords = [(1, 0), (1, 1), (1, 2), (1, 3), (1, 4)]
        elif digit == 2:
            coords = [(1, 0), (2, 0), (0, 1), (1, 2), (2, 3), (0, 4), (1, 4), (0, 2)]
        elif digit == 3:
            coords = [(0, 0), (1, 0), (2, 1), (1, 2), (2, 3), (0, 4), (1, 4)]
        elif digit == 4:
            coords = [(2, 0), (2, 1), (0, 2), (1, 2), (2, 2), (0, 3), (2, 3), (0, 4), (2, 4)]
        elif digit == 5:
            coords = [(0, 0), (1, 0), (2, 1), (1, 2), (0, 3), (1, 4), (2, 4), (0, 2)]
        elif digit == 6:
            coords = [(1, 0), (0, 1), (2, 1), (0, 2), (1, 2), (0, 3), (1, 4), (2, 4)]
        elif digit == 7:
            coords = [(0, 0), (0, 1), (1, 2), (2, 3), (0, 4), (1, 4), (2, 4)]
        elif digit == 8:
            coords = [(1, 0), (0, 1), (2, 1), (1, 2), (0, 3), (2, 3), (1, 4)]
        elif digit == 9:
            coords = [(0, 0), (1, 0), (2, 1), (1, 2), (2, 2), (0, 3), (2, 3), (1, 4)]

        img = self.atoms.cells[0][digit].tile.image
        for coord in coords:
            self.sprites.append(SquareSprite(img, coord))


class TetrisBoardLayer(layer.ScrollableLayer):
    """ The code isn't very MVC, but it does keep a simple model matrix data 
    structure, the spite_grid, to hold the SquareSprites.
    """

    width = 10
    height = 22
    keydelay_interval = .25
    start_block_char = 'T'
    is_event_handler = True
    key_pressed = None
    sprite_grid = None
    current_block = None
    tetris_maplayer = None
    sandbox = None   # Palette for block creation
    atoms = None  # Palette for graphically representing numeral score
    score = None
    existing_blocks = []
    digit_sprite_sets = []
    chosen_digits = []
    # test_blocks = ['T', 'I']

    def __init__(self, xmlpath):
        super(TetrisBoardLayer, self).__init__()

        self.sprite_grid = [[None for y in range(self.height)] for x in range(self.width)]
        r = cocos.tiles.load(xmlpath)
        self.tetris_maplayer = r['map0']  # TODO 'map0' is hardcoded
        self.add(self.tetris_maplayer)
        self.sandbox = r['sandbox']  # Used as the palette
        self.score = 0

        # Set size and show the grid
        x, y = cocos.director.director.get_window_size()
        self.tetris_maplayer.set_view(0, 0, x, y)

        # Add group of sprites based on current block
        self._new_block(self.start_block_char)

        # Set up scoreboard
        for x in range(3):
            digits = []
            for y in range(10):
                digits.append(DigitSpriteGroup(y, r['atoms']))
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
            if self.current_block.move('LEFT'):
                for sprite in self.current_block.square_sprites:
                    x, y = self.current_block.grid_coord(sprite)
                    texture_cell = self.tetris_maplayer.cells[x][y]
                    sprite.do(Place((texture_cell.x + 9, texture_cell.y + 9)))
        elif direction == 'RIGHT':
            if self.current_block.move('RIGHT'):
                # After movement in sprite grid model, do it visually
                for sprite in self.current_block.square_sprites:
                    x, y = self.current_block.grid_coord(sprite)
                    texture_cell = self.tetris_maplayer.cells[x][y]
                    sprite.do(Place((texture_cell.x + 9, texture_cell.y + 9)))
        elif direction == 'DOWN':
            if self.current_block.move('DOWN'):
                for sprite in self.current_block.square_sprites:
                    x, y = self.current_block.grid_coord(sprite)
                    texture_cell = self.tetris_maplayer.cells[x][y]
                    sprite.do(Place((texture_cell.x + 9, texture_cell.y + 9)))
        elif direction == 'DROP':
            while self.current_block.can_move('DOWN'):
                self._move_block('DOWN')

            # Clear any existing lines and record the number of lines
            numlines = self._clear_lines()

            # Increment and display score
            self.score += numlines
            self._display_score()

            self.current_block = None
            self._new_block()
            # print("Collapsed\n{}".format(self._board_to_string()))
        elif direction == 'UP':
            if self.current_block.rotate('CLOCKWISE'):
                for sprite in self.current_block.square_sprites:
                    x, y = self.current_block.grid_coord(sprite)
                    texture_cell = self.tetris_maplayer.cells[x][y]
                    sprite.do(Place((texture_cell.x + 9, texture_cell.y + 9)))

    def _new_block(self, blockchar=None):
        """ Note: This should be called when self.current_block == None
        All conditions:
          blockchar=None, current exists => nothing happens
          blockchar=None, no current => get random
          blockchar=<char>, current exists => nothing happens
          blockchar=<char>, no current => use supplied
        """

        if self.current_block:
            raise ShouldntHappenError("Getting a new block without removing current")

        rotated_state = 0  # Change to rng if needed to randomize
        if blockchar is None:
            r = randrange(0, 7)
            if r == 0:
                self.current_block = Block('L', self, rotated_state)
            elif r == 1:
                self.current_block = Block('J', self, rotated_state)
            elif r == 2:
                self.current_block = Block('I', self, rotated_state)
            elif r == 3:
                self.current_block = Block('O', self, rotated_state)
            elif r == 4:
                self.current_block = Block('S', self, rotated_state)
            elif r == 5:
                self.current_block = Block('Z', self, rotated_state)
            elif r == 6:
                self.current_block = Block('T', self, rotated_state)
        else:
            self.current_block = Block(blockchar, self, rotated_state)
        self.existing_blocks.append(self.current_block)

        # Draw sprites on layer
        for s in self.current_block.square_sprites:
            x, y = self.current_block.grid_coord(s)
            texture_cell = self.tetris_maplayer.cells[x][y]
            s.position = (texture_cell.x + 9, texture_cell.y + 9)
            self.add(s, z=1)

    def _clear_lines(self):
        """ Clear any complete lines and collapse the squares as a result """

        # Get list of y coordinates to clear
        rows_to_clear = []  # will hold y coordinates
        for y in range(len(self.sprite_grid[0])):
            for x in range(len(self.sprite_grid)):
                if self.sprite_grid[x][y] is None:
                    break
                if x == len(self.sprite_grid) - 1:
                    rows_to_clear.append(y) 

        if not rows_to_clear: 
            return 0

        # Clear lines
        for y in rows_to_clear: 
            for x in range(len(self.sprite_grid)):
                try:
                    self.remove(self.sprite_grid[x][y])
                except Exception:
                    print('Sprite is not a child when clearing')
                    print('coord:{}\n'.format(self.sprite_grid[x][y].grid_coord))
                    raise ShouldntHappenError("Shouldn't happen error, closing")
                # Library function remove() doesn't nullify parent
                self.sprite_grid[x][y].parent = None
                self.sprite_grid[x][y] = None

        # Remove cleared sprites from their blocks
        blocks_to_remove = []
        for block in self.existing_blocks:
            if not block.square_sprites:
                blocks_to_remove.append(block)
            else:
                sprites_to_remove = []
                for sprite in block.square_sprites:
                    if not sprite.parent:
                        sprites_to_remove.append(sprite)
                for sprite in sprites_to_remove:
                    block.square_sprites.remove(sprite)
                if not block.square_sprites:
                    blocks_to_remove.append(block)
        for block in blocks_to_remove:
            self.existing_blocks.remove(block)

        #-----------------------------------------------------------------------
        #                              Collapsing
        # Shifts down every block above the row lines (line_ys). Keeps track 
        # of a base row that determines which squares to shift down
        #-----------------------------------------------------------------------
        prev_y = None
        base_y = rows_to_clear[0] 
        for y in rows_to_clear: 
            if prev_y is not None:
                base_y += (y - prev_y - 1)

            for block in self.existing_blocks:
                for sprite in block.square_sprites:
                    # Forget sprites lower than the clear line
                    if sprite.grid_coord[1] < base_y:
                        continue

                    # Move sprite down on sprite grid by removing it and putting
                    # it in its new position.
                    grid_x, grid_y = (sprite.grid_coord[0], sprite.grid_coord[1])
                    new_x, new_y = (grid_x, grid_y - 1)
                    if self.sprite_grid[grid_x][grid_y] is sprite:
                        # The sprite may not be in its original location because
                        # it could have been replaced by another sprite above it
                        # and within the same block, which is why the check.
                        self.sprite_grid[grid_x][grid_y] = None
                    self.sprite_grid[new_x][new_y] = sprite
                    sprite.grid_coord = (new_x, new_y)

                    # Do the rendering
                    texture_cell = self.tetris_maplayer.cells[new_x][new_y]
                    sprite.do(Place((texture_cell.x + 9, texture_cell.y + 9)))
            prev_y = y
        return len(rows_to_clear)

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
        for y in range(len(self.sprite_grid[0])):
            row = '|'
            for x in range(len(self.sprite_grid)):
                if self.sprite_grid[x][y] is None:
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
