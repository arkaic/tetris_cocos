from __future__ import division, print_function, unicode_literals
import tetris, cocos, pyglet
from cocos import layer
from cocos.actions import *
from cocos.sprite import Sprite

class MyTestSprite(Sprite):
    coords = None
    id = None

    def __init__(self, image, coords, position=(0, 0), rotation=0, scale=1,
                 opacity = 255, color=(255, 255, 255), anchor = None):
        super(MyTestSprite, self).__init__(image, position=position, rotation=rotation, scale=scale,
            opacity=opacity, color=color, anchor=anchor)
        self.coords = coords

    def get_coords(self):
        return self.coords

    def set_coords(self, c):
        self.coords = c


class TestRectMapLayerWrapper(layer.ScrollableLayer):
    # TODO in future, i could avoid subclassing and try to handle events manually
    # as showin in tutorial
    is_event_handler = True
    cur_spritename = "square"
    move_step = 20
    ispressed = False
    keys_pressed = set()
    tetrismodel = tetris.Board()
    cur_sprites = []

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
            sprite.position = (self.tetris_maplayer.cells[x][y].x + 9,
                               self.tetris_maplayer.cells[x][y].y + 9)
            sprite.id = i
            self.add(sprite, z=1, name=(basename + str(i)))
            self.cur_sprites.append(sprite)
            i += 1
    
    def on_key_press(self, key, modifiers):
        if not self.keys_pressed:
            self.keys_pressed.add(key)
            keyspressed = [pyglet.window.key.symbol_string(k) for k in self.keys_pressed]
            for k in keyspressed:
                self._update_pos(k, self.move_step)
            self.schedule_interval(self._button_held, .10)

    def on_key_release(self, key, modifiers):
        self.keys_pressed.discard(key)
        if len(self.keys_pressed) is 0:
            self.ispressed = False
            self.unschedule(self._button_held)

    def _button_held(self, dt):
        keyspressed = [pyglet.window.key.symbol_string(k) for k in self.keys_pressed]
        if len(keyspressed) > 0:
            for k in keyspressed:
                self._update_pos(k, self.move_step)

    def _update_pos(self, dir, step):
        if dir == 'DOWN':
            pass
        elif dir == 'UP':
            # TODO rotate block
            pass
        elif dir == 'RIGHT':
            # The cell is reference to the grid location and its pixel x,y is 
            # needed for the actual sprite placing
            self.tetrismodel.move_block_right()
            for sprite in self.cur_sprites:
                x_model, y_model = self.tetrismodel.current_block.board_coords_colmajor()[sprite.id]
                cell = self.tetris_maplayer.cells[x_model][y_model]
                sprite.set_coords((x_model, y_model))
                sprite.do(Place((cell.x + 9, cell.y + 9)))
        elif dir == 'LEFT':
            self.tetrismodel.move_block_left()
            for sprite in self.cur_sprites:
                x_model, y_model = self.tetrismodel.current_block.board_coords_colmajor()[sprite.id]
                cell = self.tetris_maplayer.cells[x_model][y_model]
                sprite.set_coords((x_model, y_model))
                sprite.do(Place((cell.x + 9, cell.y + 9)))

    def _check_movable(self, dir):
        for sprite in self.cur_sprites:
            i, j = sprite.get_coords()
            if (dir == 'RIGHT' and i >= 9) or (dir == 'LEFT' and i <= 0):
                return False
        return True

    def run(self):
        self.add(self.tetris_maplayer)
        scroller = layer.ScrollingManager()
        scroller.set_focus(100,200)
        scroller.add(self)
        cocos.director.director.run(cocos.scene.Scene(scroller))



class AnimMovingSpriteLayer(layer.ScrollableLayer):
    is_event_handler = True
    move_step = 5
    spriteobj_name = 'square'

    def __init__(self):
        super(AnimMovingSpriteLayer, self).__init__()
        self.sprites = [pyglet.resource.image('sprites/cellblue.png'),
                        pyglet.resource.image('sprites/cellgreen.png'),
                        pyglet.resource.image('sprites/cellred.png')]
        self.anim = pyglet.image.Animation.from_image_sequence(self.sprites, 0.5, True)
        sprite_object = cocos.sprite.Sprite(self.sprites[2])
        print(sprite_object.position)
        sprite_object.position = (-90,-90)
        self.add(sprite_object, z=1, name=self.spriteobj_name)
        self.keys_pressed = set()
        self.schedule_interval(self.act_on_input, .033)
    
    def on_key_press(self, key, modifiers):
        # the image first starts off as a static image, not the animating one
        if self.get(self.spriteobj_name)._get_image() is not self.anim:
            self.get(self.spriteobj_name)._set_image(self.anim)
        self.keys_pressed.add(key)

    def on_key_release(self, key, modifiers):
        # on key release, reset the image back to the static
        # this will give the appearance of an animating sprite whenever you move
        self.keys_pressed.discard(key)
        keynames = [pyglet.window.key.symbol_string(k) for k in self.keys_pressed]
        if len(keynames) is 0:
            self.get(self.spriteobj_name)._set_image(self.sprites[2])

    def act_on_input(self, dt):
        key_names = [pyglet.window.key.symbol_string(k) for k in self.keys_pressed]
        if len(key_names) > 0:
            for k in key_names:
                self._update_pos(k, self.move_step)

    def _update_pos(self, dir, step):
        key_names = [pyglet.window.key.symbol_string(k) for k in self.keys_pressed]
        spr = self.get(self.spriteobj_name)
        x,y = spr.position
        if dir == 'DOWN':
            print(key_names)
            spr.do(Place((x,y-step)))
        elif dir == 'UP':
            print(key_names)
            spr.do(Place((x,y+step)))
        elif dir == 'RIGHT':
            print(key_names) 
            spr.do(Place((x+step,y)))
        elif dir == 'LEFT':
            print(key_names)
            spr.do(Place((x-step,y)))
        x,y = spr.position








