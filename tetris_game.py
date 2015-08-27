import cocos, pyglet, sys, pdb
from cocos import layer, scene
from cocos.sprite import Sprite
from cocos.director import director
from cocos.actions import Place
from random import randrange
from pyglet import window


class SquareSprite(Sprite):
    bounding_coord = None
    
    def __init__(self, image, coord, position=(0, 0), rotation=0, scale=1,
                opacity=255, color=(255, 255, 255), anchor=None):
        super(SquareSprite, self).__init__(image, position=position, 
                rotation=rotation, scale=scale, opacity=opacity, color=color,
                anchor=anchor)

        self.bounding_coord = coord


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
    gridlocation_coord = None

    def __init__(self, block_char, tetrisboardlayer, rotated_state):
        self.char = block_char
        self.board_layer = tetrisboardlayer
        self.sprite_grid = tetrisboardlayer.sprite_grid
        self.square_sprites = []
        self._make_sprites(rotated_state)

    def move(self, direction):
        """ Move sprite on sprite grid (and visually too?)
        """
        if not self._can_move(direction):
            return False

        # Erase from sprite grid
        for sprite in self.square_sprites:
            sprite_x, sprite_y = self.grid_coord(sprite.bounding_coord)
            self.sprite_grid[sprite_x][sprite_y] = None

        # Put sprites into new locations by changing the grid location coord and 
        # offsetting every sprite by it again.
        prev_gridloc_x, prev_gridloc_y = self.gridlocation_coord
        for sprite in self.square_sprites:            
            if direction == 'LEFT':
                self.gridlocation_coord = (prev_gridloc_x - 1, prev_gridloc_y)
            elif direction == 'RIGHT':
                self.gridlocation_coord = (prev_gridloc_x + 1, prev_gridloc_y)
            elif direction == 'DOWN':
                self.gridlocation_coord = (prev_gridloc_x, prev_gridloc_y - 1)
            sprite_x, sprite_y = self.grid_coord(sprite.bounding_coord)
            self.sprite_grid[sprite_x][sprite_y] = sprite
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

        # Erase
        for sprite in self.square_sprites:
            sprite_x, sprite_y = self.grid_coord(sprite.bounding_coord)
            self.sprite_grid[sprite_x][sprite_y] = None

        if not self._can_rotate(direction):
            return False

        prev_gridloc_x, prev_gridloc_y
        # for sprite in self.square_sprites:
        #     sprite_x, sprite_y = self.grid_coord(sprite.bounding_coord)
        #     if direction == 'CLOCKWISE':
        #         rotated_sprite_x = sprite_y
        #         if self.char == 'I' or self.char == 'O'
        #             rotated_sprite_y = 1 - sprite_x
        #         else:
        #             rotated_sprite_y = -1 * sprite_x
        #         if self.sprite_grid
        #         pass

        return True

    def grid_coord(self, bound_coord):
        return (bound_coord[0] + self.gridlocation_coord[0], 
            bound_coord[1] + self.gridlocation_coord[1])

    def _make_sprites(self, state):
        init_bounding_coords = []
        img = None
        if self.char == 'I':
            self.gridlocation_coord = (4, 19)
            img = self.board_layer.sandbox.cells[0][0].tile.image
            init_bounding_coords = [(-1,1), (0,1), (1,1), (2,1)]
        elif self.char == 'J':
            self.gridlocation_coord = (4, 20)
            img = self.board_layer.sandbox.cells[0][1].tile.image
            init_bounding_coords = [(-1,1), (-1,0), (0,0), (1,0)]
        elif self.char == 'L':
            self.gridlocation_coord = (4, 20)
            img = self.board_layer.sandbox.cells[0][2].tile.image
            init_bounding_coords = [(-1,0), (0,0), (1,0), (1,1)]
        elif self.char == 'O':
            self.gridlocation_coord = (4, 20)
            img = self.board_layer.sandbox.cells[0][3].tile.image
            init_bounding_coords = [(0,1), (0,0), (1,1), (1,0)]
        elif self.char == 'S':
            self.gridlocation_coord = (4, 20)
            img = self.board_layer.sandbox.cells[0][4].tile.image
            init_bounding_coords = [(-1,0), (0,0), (0,1), (1,1)]
        elif self.char == 'T':
            self.gridlocation_coord = (4, 20)
            img = self.board_layer.sandbox.cells[0][6].tile.image
            init_bounding_coords = [(-1,0), (0,1), (0,0), (1,0)]
        elif self.char == 'Z':
            self.gridlocation_coord = (4, 20)
            img = self.board_layer.sandbox.cells[0][5].tile.image
            init_bounding_coords = [(-1,1), (0,1), (0,0), (1,0)]

        # Add sprites to both the member list and the grid model
        for bounding_coord in init_bounding_coords:
            sprite = SquareSprite(img, bounding_coord)
            self.square_sprites.append(sprite)
            sprite_x, sprite_y = self.grid_coord(bounding_coord)
            self.sprite_grid[sprite_x][sprite_y] = sprite

    def _can_move(self, direction):
        """ Sprite coordinates are made up of the grid location offset by the 
        bounding coords 
        """
        for sprite in self.square_sprites:
            sprite_x, sprite_y = self.grid_coord(sprite.bounding_coord)
            if direction == 'LEFT':
                if sprite_x <= 0:
                    return False
                if (not self._is_a_block_coord((sprite_x - 1, sprite_y)) and 
                    self.sprite_grid[sprite_x - 1][sprite_y] != None):
                    # if shifted position of square is not in block and there's
                    # something in that shifted coordinate, can't move block
                    return False
            elif direction == 'RIGHT':
                if sprite_x >= self.board_layer.width - 1:
                    return False
                if (not self._is_a_block_coord((sprite_x + 1, sprite_y)) and 
                    self.sprite_grid[sprite_x + 1][sprite_y] != None):
                    return False
            elif direction == 'DOWN':
                if sprite_y <= 0: 
                    return False
                if (not self._is_a_block_coord((sprite_x, sprite_y - 1)) and 
                    self.sprite_grid[sprite_x][sprite_y - 1] != None):
                    return False
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
        for sprite in self.square_sprites:
            sprite_x, sprite_y = self.grid_coord(sprite.bounding_coord)
            if direction == 'CLOCKWISE':
                rotated_sprite_x = sprite_y
                if self.char == 'I' or self.char == 'O':
                    rotated_sprite_y = 1 - sprite_x
                else:
                    rotated_sprite_y = -sprite_x
            elif direction == 'COUNTERCLOCKWISE':
                if self.char == 'I' or self.char == 'O':
                    rotated_sprite_x = 1 - sprite_y
                else:
                    rotated_sprite_x = -sprite_y
                rotated_sprite_y = sprite_x

            if direction == 'CLOCKWISE' OR direction == 'COUNTERCLOCKWISE':
                if self.sprite_grid[rotated_sprite_x][rotated_sprite_y] != None:
                    return False
        return True

    def _is_a_block_coord(self, grid_coord):
        for square in self.square_sprites:
            if grid_coord == self.grid_coord(square.bounding_coord):
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
    is_event_handler = True
    key_pressed = None
    sprite_grid = None
    current_block = None
    tetris_maplayer = None
    sandbox = None
    # existing_blocks = []  # maybe i use it maybe i dont

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
        self._new_block()

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

        # # Draw sprites on layer
        for s in self.current_block.square_sprites:
            x, y = self.current_block.grid_coord(s.bounding_coord)
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
            self.schedule_interval(self._button_held, .15)

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

    def _move_block(self, dir):
        moved = False
        if dir == 'LEFT':
            if self.current_block.move('LEFT'):
                moved = True
                for sprite in self.current_block.square_sprites:
                    x, y = self.current_block.grid_coord(sprite.bounding_coord)
                    print("   {},{}".format(x,y))
                    texture_cell = self.tetris_maplayer.cells[x][y]
                    sprite.do(Place((texture_cell.x + 9, texture_cell.y + 9)))
        elif dir == 'RIGHT':
            if self.current_block.move('RIGHT'):
                # After movement in sprite grid model, do it visually
                moved = True
                for sprite in self.current_block.square_sprites:
                    x, y = self.current_block.grid_coord(sprite.bounding_coord)
                    print("   {},{}".format(x,y))
                    texture_cell = self.tetris_maplayer.cells[x][y]
                    sprite.do(Place((texture_cell.x + 9, texture_cell.y + 9)))
        elif dir == 'DOWN':
            # TODO single move down
            if self.current_block.move('DOWN'):
                moved = True
                for sprite in self.current_block.square_sprites:
                    x, y = self.current_block.grid_coord(sprite.bounding_coord)
                    print("   {},{}".format(x,y))
                    texture_cell = self.tetris_maplayer.cells[x][y]
                    sprite.do(Place((texture_cell.x + 9, texture_cell.y + 9)))
        elif dir == 'DROP':
            while self.current_block._can_move('DOWN'):
                moved = True
                self._move_block('DOWN')

            # Create next block
            self.current_block = None
            self._new_block()

            # TODO implement clear line and collapse
            pass
        elif dir == 'UP':
            # TODO rotate
            pass

        if moved:
            print("{} {}".format(dir, self.current_block.char))


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