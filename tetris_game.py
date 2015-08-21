import cocos, pyglet, sys
from cocos import layer
from cocos.actions import *
from cocos.sprite import Sprite
from random import randrange
from pyglet.window import key


class SquareSprite(Sprite):
    pass


class Block():
    """ References all SquareSprites and their location on the model 2D array.
    Sprites will exist inside a bounding square that this class defines.
    """
    # Notes: Formula for I and O block
    # newXccw = centerX - y + centerY
    # newYccw = centerY + x - centerX
    # newXcw  = centerX + y - centerY
    # newYcw  = centerY - x + centerX
    # Formula for rest
    # ccw =>   x,y => -y,x
    # cw  =>   x,y => y,-x
    def __init__(self, block_char):
        self.char = block_char
        # i = 0
        # basename = self.tetrismodel.current_block.char        
        # for x,y in self.tetrismodel.current_block.board_coords_colmajor():
        #     sprite = MyTestSprite(self.sandbox.cells[0][5].tile.image, (x, y))
        #     sprite.id = i
        #     cell = self.tetris_maplayer.cells[x][y]
        #     sprite.position = (cell.x + 9, cell.y + 9)
        #     self.add(sprite, z=1, name=(basename + str(i)))
        #     self.cur_block_sprites.append(sprite)
        #     self.all_sprites.append(sprite)
        #     i += 1


class TetrisBoardLayer(layer.ScrollableLayer):
    """ Also keeps track of SquareSprites in a 2D array because the rectmap.cells
    array only tracks the background texture.
    """
    # Notes: When clearing a line and going sprite by sprite, remove from model
    # array and then also remove the sprite from the BoardLayer

    board_width = 10
    board_height = 22
    is_event_handler = True
    keys_pressed = set()
    sprite_grid =  = [[None for y in range(self.height)] for x in range(self.width)]
    current_block = None
    tetris_maplayer = None
    sandbox = None
    # all_blocks = []  maybe i use it maybe i dont

    def __init__(self, xmlpath):
        super(TestRectMapLayerWrapper, self).__init__()        
        r = cocos.tiles.load('tetris.xml')  #['map0'] # TODO hardcoded
        self.tetris_maplayer = r['map0']
        self.sandbox = r['sandbox']  # Used as the palette

        # Set size and show the grid
        x,y = cocos.director.director.get_window_size()
        self.tetris_maplayer.set_view(0, 0, x, y)

        # Add group of sprites based on current block
        self.new_block('T')

    def _new_block(self, blockchar=None):
        # none supplied, current block => nothing happens
        # none supplied, no current => get random
        # supplied, current => nothing happens
        # supplied, no current => use supplied
        if self.current_block:
            raise ShouldntHappenError("Getting a new block without removing current")
            sys.exit()

        if blockchar is None:             
            r = randrange(0, 7)
            if r == 0:
                self.current_block = Block('L')
            elif r == 1:
                self.current_block = Block('J')
            elif r == 2:
                self.current_block = Block('I')
            elif r == 3:
                self.current_block = Block('O')
            elif r == 4:
                self.current_block = Block('S')
            elif r == 5:
                self.current_block = Block('Z')
            elif r == 6:
                self.current_block = Block('T')
        else:
            self.current_block = Block(blockchar)

        # TODO draw the block's sprites on

    def on_key_press(self, key, modifiers):
        if not self.keys_pressed:
            self.keys_pressed.add(key)
            keyspressed = [key.symbol_string(k) for k in self.keys_pressed]
            for key in keyspressed:
                self._move_block(key)
            self.schedule_interval(self._button_held, .10)

    def on_key_release(self, key, modifiers):
        self.keys_pressed.discard(key)
        if len(self.keys_pressed) == 0:
            self.unschedule(self._button_held)

    def _button_held(self, dt):
        keyspressed = [key.symbol_string(key) for key in self.keys_pressed]
        if len(keyspressed) > 0:
            for key in keyspressed:
                self._move_block(key)

    def _move_block(self, dir):
        if dir == 'DOWN':
            # TODO drop
            pass
        elif dir == 'UP':
            # TODO rotate
            pass
        elif dir == 'RIGHT':
            # TODO 
            pass
        elif dir == 'LEFT':
            pass



class ShouldntHappenError(UserWarning):
    pass


################################################################################

if __name__ == '__main__':
    pass
