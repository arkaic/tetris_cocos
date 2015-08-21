import cocos, pyglet
from cocos import layer
from cocos.actions import *
from cocos.sprite import Sprite
from random import randrange


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
    pass


class TetrisBoardLayer(layer.ScrollableLayer):
    """ Also keeps track of SquareSprites in a 2D array because the rectmap.cells
    array only tracks the background texture.
    """
    # Notes: When clearing a line and going sprite by sprite, remove from model
    # array and then also remove the sprite from the BoardLayer

    is_event_handler = True
    keys_pressed = set()
    board_width = 10
    board_height = 22
    sprite_grid = None
    current_block = None
    # all_blocks = []  maybe i use it maybe i dont

    def __init__(self, xmlpath):
        super(TestRectMapLayerWrapper, self).__init__()
        r = cocos.tiles.load('tetris.xml')  #['map0'] # TODO hardcoded
        self.tetris_maplayer = r['map0']
        self.sandbox = r['sandbox']  # Used as the palette
        print("{} x {}".format(len(self.tetris_maplayer.cells), len(self.tetris_maplayer.cells[0])))

        # Set size and show the grid
        x,y = cocos.director.director.get_window_size()
        self.tetris_maplayer.set_view(0, 0, x, y)

        # Add group of sprites based on current block
        self.tetrismodel.new_block('t')
        i = 0
        basename = self.tetrismodel.current_block.char        
        for x,y in self.tetrismodel.current_block.board_coords_colmajor():
            sprite = MyTestSprite(self.sandbox.cells[0][5].tile.image, (x, y))
            sprite.id = i
            cell = self.tetris_maplayer.cells[x][y]
            sprite.position = (cell.x + 9, cell.y + 9)
            self.add(sprite, z=1, name=(basename + str(i)))
            self.cur_block_sprites.append(sprite)
            self.all_sprites.append(sprite)
            i += 1