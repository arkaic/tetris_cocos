import cocos, pyglet, sys, pdb
from cocos import layer, scene
from cocos.sprite import Sprite
from cocos.director import director
from cocos.actions import Place
from random import randrange
from pyglet import window


class SquareSprite(Sprite):
    bounding_coord = None
    grid_coord = None

    def __init__(self, image, coord, position=(0, 0), rotation=0, scale=1,
                opacity=255, color=(255, 255, 255), anchor=None):
        super(SquareSprite, self).__init__(image, position=position,
                rotation=rotation, scale=scale, opacity=opacity, color=color,
                anchor=anchor)

        self.bounding_coord = coord

    def set_grid_coord(self, coord):
        self.grid_coord = coord


class Block():
    """ References all SquareSprites and their location on the model 2D array.
    Sprites will exist inside an abstract bounding square that this class defines.

    Each block will have following attributes:
     * Bounding square coordinates for each sprite, relative to origin point 0,0.
       (TODO or this is a SquareSprite attribute instead)
     * Sprite grid coordinate that the origin point is mapped to.
    """

    char = None
    board_layer = None  # cocos parent layer
    sprite_grid = None
    square_sprites = None
    _gridlocation_coord = None

    def __init__(self, block_char, tetrisboardlayer, rotated_state):
        self.char = block_char
        self.board_layer = tetrisboardlayer
        self.sprite_grid = tetrisboardlayer.sprite_grid
        self.square_sprites = []

        init_bounding_coords = []
        img = None
        if self.char == 'I':
            self._gridlocation_coord = (4, 19)
            img = self.board_layer.sandbox.cells[0][0].tile.image
            init_bounding_coords = [(-1,1), (0,1), (1,1), (2,1)]
        elif self.char == 'J':
            self._gridlocation_coord = (4, 20)
            img = self.board_layer.sandbox.cells[0][1].tile.image
            init_bounding_coords = [(-1,1), (-1,0), (0,0), (1,0)]
        elif self.char == 'L':
            self._gridlocation_coord = (4, 20)
            img = self.board_layer.sandbox.cells[0][2].tile.image
            init_bounding_coords = [(-1,0), (0,0), (1,0), (1,1)]
        elif self.char == 'O':
            self._gridlocation_coord = (4, 20)
            img = self.board_layer.sandbox.cells[0][3].tile.image
            init_bounding_coords = [(0,1), (0,0), (1,1), (1,0)]
        elif self.char == 'S':
            self._gridlocation_coord = (4, 20)
            img = self.board_layer.sandbox.cells[0][4].tile.image
            init_bounding_coords = [(-1,0), (0,0), (0,1), (1,1)]
        elif self.char == 'T':
            self._gridlocation_coord = (4, 20)
            img = self.board_layer.sandbox.cells[0][6].tile.image
            init_bounding_coords = [(-1,0), (0,1), (0,0), (1,0)]
        elif self.char == 'Z':
            self._gridlocation_coord = (4, 20)
            img = self.board_layer.sandbox.cells[0][5].tile.image
            init_bounding_coords = [(-1,1), (0,1), (0,0), (1,0)]

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
                print("{}, {} from {}".format(rotated_sprite_x, rotated_sprite_y, self._gridlocation_coord))

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



class TetrisBoardLayer(layer.ScrollableLayer):
    """ Also keeps track of SquareSprites in a 2D array because the rectmap.cells
    array only tracks the background texture.
    """
    # Notes: When clearing a line and going sprite by sprite, remove from model
    # array and then also remove the sprite from the BoardLayer

    width = 10
    height = 22
    keydelay_interval = .25
    start_block_char = 'T'
    is_event_handler = True
    key_pressed = None
    sprite_grid = None
    current_block = None
    tetris_maplayer = None
    sandbox = None
    existing_blocks = []  # maybe i use it maybe i dont

    def __init__(self, xmlpath):
        super(TetrisBoardLayer, self).__init__()

        self.sprite_grid = [[None for y in range(self.height)] for x in range(self.width)]
        r = cocos.tiles.load(xmlpath)  #['map0'] # TODO hardcoded
        self.tetris_maplayer = r['map0']
        self.add(self.tetris_maplayer)
        self.sandbox = r['sandbox']  # Used as the palette

        # Set size and show the grid
        x,y = cocos.director.director.get_window_size()
        self.tetris_maplayer.set_view(0, 0, x, y)

        # Add group of sprites based on current block
        self._new_block(self.start_block_char)

        # Schedule timed drop of block
        self.schedule_interval(self._timed_drop, .7)

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
            sys.exit()

        rotated_state = 0  # Change to rng if needed to randomize
        if blockchar == None:
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

        # # Draw sprites on layer
        for s in self.current_block.square_sprites:
            x, y = self.current_block.grid_coord(s)
            print("{},{}".format(x,y))
            texture_cell = self.tetris_maplayer.cells[x][y]
            s.position = (texture_cell.x + 9, texture_cell.y + 9)
            self.add(s, z=1)

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

    def _timed_drop(self, dt):
        self._move_block('DOWN')

    def _button_held(self, dt):
        if self.key_pressed:
            if self.key_pressed == 'DOWN':
                self._move_block('DROP')
            else:
                self._move_block(self.key_pressed)

    def _move_block(self, direction):
        moved = False
        if direction == 'LEFT':
            if self.current_block.move('LEFT'):
                moved = True
                for sprite in self.current_block.square_sprites:
                    x, y = self.current_block.grid_coord(sprite)
                    print("   {},{}".format(x,y))
                    texture_cell = self.tetris_maplayer.cells[x][y]
                    sprite.do(Place((texture_cell.x + 9, texture_cell.y + 9)))
        elif direction == 'RIGHT':
            if self.current_block.move('RIGHT'):
                # After movement in sprite grid model, do it visually
                moved = True
                for sprite in self.current_block.square_sprites:
                    x, y = self.current_block.grid_coord(sprite)
                    print("   {},{}".format(x,y))
                    texture_cell = self.tetris_maplayer.cells[x][y]
                    sprite.do(Place((texture_cell.x + 9, texture_cell.y + 9)))
        elif direction == 'DOWN':
            if self.current_block.move('DOWN'):
                moved = True
                for sprite in self.current_block.square_sprites:
                    x, y = self.current_block.grid_coord(sprite)
                    print("   {},{}".format(x,y))
                    texture_cell = self.tetris_maplayer.cells[x][y]
                    sprite.do(Place((texture_cell.x + 9, texture_cell.y + 9)))
        elif direction == 'DROP':
            while self.current_block.can_move('DOWN'):
                moved = True
                self._move_block('DOWN')

            # Check for and clear lines
            self._clear_lines()

            # Create next block
            self.current_block = None
            self._new_block()
        elif direction == 'UP':
            if self.current_block.rotate('CLOCKWISE'):
                moved = True
                for sprite in self.current_block.square_sprites:
                    x, y = self.current_block.grid_coord(sprite)
                    print("   {},{}".format(x, y))
                    texture_cell = self.tetris_maplayer.cells[x][y]
                    sprite.do(Place((texture_cell.x + 9, texture_cell.y + 9)))

        if moved:
            if direction == 'UP':
                direction = 'ROTATE'
            print("{} {}".format(direction, self.current_block.char))

        return moved

    def _clear_lines(self):
        # Get list of y coordinates to clear
        line_ys_to_clear = []
        for y in range(len(self.sprite_grid[0])):
            for x in range(len(self.sprite_grid)):
                if self.sprite_grid[x][y] is None:
                    break
                if x == len(self.sprite_grid) - 1:
                    line_ys_to_clear.append(y)

        if not line_ys_to_clear:
            return False

        # Clear lines
        # pdb.set_trace()
        for y in line_ys_to_clear:
            for x in range(len(self.sprite_grid)):
                self.remove(self.sprite_grid[x][y])
                # Lib function remove() doesn't nullify parent?
                self.sprite_grid[x][y].parent = None
                self.sprite_grid[x][y] = None

        # Remove cleared sprites from their blocks
        for block in self.existing_blocks:
            if not block.square_sprites:
                self.existing_blocks.remove(block)
            else:
                l = []
                for sprite in block.square_sprites:
                    if not sprite.parent:
                        l.append(sprite)
                for sprite in l:
                    block.square_sprites.remove(sprite)
                if not block.square_sprites:
                    self.existing_blocks.remove(block)

        self._collapse(line_ys_to_clear)

        return True

    def _collapse(self, line_ys_to_clear):
        movable_block_exists = True
        while movable_block_exists:
            c = 0
            for block in self.existing_blocks:
                # for sprite in block.square_sprites:
                #     x, y = block.grid_coord(sprite.bounding_coord)
                #     texture_cell = self.tetris_maplayer.cells[x][y]
                #     sprite.do(Place((texture_cell.x + 9, texture_cell.y + 9)))

                self.current_block = block
                if self._move_block('DOWN'):
                    c += 1
                    print("c++")
            if c == 0:
                movable_block_exists = False
                print("didn't exist")


class ShouldntHappenError(UserWarning):
    pass

################################################################################

if __name__ == '__main__':
    director.init(resizable=True)
    tetris_board = TetrisBoardLayer('tetris.xml')
    scroller = layer.ScrollingManager()
    scroller.set_focus(100, 200)
    scroller.add(tetris_board)
    director.run(scene.Scene(scroller))