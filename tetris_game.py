import cocos, pyglet, sys
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
    # Notes: Formula for I and O block
    # newXccw = centerX + centerY - y
    # newYccw = centerY - centerX + x
    # newXcw  = centerX - centerY + y
    # newYcw  = centerX + centerY - x
    # Formula for rest
    # ccw =>   x,y => -y, x
    # cw  =>   x,y =>  y,-x

    char = None
    board_layer = None  # cocos parent layer
    sprite_grid = None
    gridlocation_coord = None
    square_sprites = []

    def __init__(self, block_char, tetrisboardlayer, rotated_state):
        self.char = block_char
        self.board_layer = tetrisboardlayer
        self.sprite_grid = tetrisboardlayer.sprite_grid
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
    keys_pressed = set()
    sprite_grid = None
    current_block = None
    tetris_maplayer = None
    sandbox = None
    # all_blocks = []  maybe i use it maybe i dont

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

    def _new_block(self, blockchar=None):
        # none supplied, current exists => nothing happens
        # none supplied, no current => get random
        # supplied, current exists => nothing happens
        # supplied, no current => use supplied
        if self.current_block:
            raise ShouldntHappenError("Getting a new block without removing current")
            sys.exit()

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

        # Draw sprites on layer
        for s in self.current_block.square_sprites:
            x, y = self.current_block.grid_coord(s.bounding_coord)
            texture_cell = self.tetris_maplayer.cells[x][y]
            s.position = (texture_cell.x + 9, texture_cell.y + 9)
            self.add(s, z=1)

    def on_key_press(self, key, modifiers):
        if not self.keys_pressed:
            self.keys_pressed.add(key)
            keyspressed = [window.key.symbol_string(k) for k in self.keys_pressed]
            for key in keyspressed:
                self._move_block(key)
            self.schedule_interval(self._button_held, .10)

    def on_key_release(self, key, modifiers):
        self.keys_pressed.discard(key)
        if len(self.keys_pressed) == 0:
            self.unschedule(self._button_held)

    def _button_held(self, dt):
        keyspressed = [window.key.symbol_string(key) for key in self.keys_pressed]
        if len(keyspressed) > 0:
            for key in keyspressed:
                self._move_block(key)

    def _move_block(self, dir):
        if dir == 'LEFT':
            if self.current_block.move('LEFT'):
                print("Move LEFT")
                for sprite in self.current_block.square_sprites:
                    x, y = self.current_block.grid_coord(sprite.bounding_coord)
                    texture_cell = self.tetris_maplayer.cells[x][y]
                    sprite.do(Place((texture_cell.x + 9, texture_cell.y + 9)))
        elif dir == 'RIGHT':
            # If block is moved on the sprite grid model, then move it visually
            if self.current_block.move('RIGHT'):
                print("Move RIGHT")
                for sprite in self.current_block.square_sprites:
                    x, y = self.current_block.grid_coord(sprite.bounding_coord)
                    texture_cell = self.tetris_maplayer.cells[x][y]
                    sprite.do(Place((texture_cell.x + 9, texture_cell.y + 9)))
        elif dir == 'DOWN':
            # TODO 
            # do drop:
            #   - 
            # if do clear:
            #   - remove sprite f.rom spritegrid
            #   - remove sprite from block
            #   - remove sprite visually
            # make new block            
            while self.current_block._can_move('DOWN'):
                print("Move DOWN")
                self.current_block.move('DOWN')
                for sprite in self.current_block.square_sprites:
                    x, y = self.current_block.grid_coord(sprite.bounding_coord)
                    texture_cell = self.tetris_maplayer.cells[x][y]
                    sprite.do(Place((texture_cell.x + 9, texture_cell.y + 9)))
        elif dir == 'UP':
            # TODO rotate
            pass            



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