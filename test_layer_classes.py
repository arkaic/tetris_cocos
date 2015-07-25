from __future__ import division, print_function, unicode_literals
import tetris, cocos, pyglet
from cocos import layer, sprite
from cocos.actions import *
from cocos.sprite import Sprite

class TestRectMapLayerWrapper(layer.ScrollableLayer):
    # TODO in future, i could avoid subclassing and try to handle events manually
    # as showin in tutorial
    is_event_handler = True
    cur_spritename = "square"
    move_step = 20
    pressed = False
    # leftpressed = False
    # rightpressed = False
    # downpressed = False
    # uppressed = False

    def __init__(self, xmlpath):
        super(TestRectMapLayerWrapper, self).__init__()
        r = cocos.tiles.load('tetris.xml')  #['map0'] # TODO hardcoded
        self.tetris_maplayer = r['map0']
        x,y = cocos.director.director.get_window_size()
        self.tetris_maplayer.set_view(0, 0, x, y)

        # TODO using image from grid for a sprite, little messy
        # TODO add sprite with name param too
        sprite = Sprite(self.tetris_maplayer.cells[0][0].tile.image)
        sprite.position = (self.tetris_maplayer.cells[5][10].x + 9, 
                           self.tetris_maplayer.cells[5][10].y + 9)
        self.add(sprite, z=1, name=self.cur_spritename)
        self.cur_sprite = sprite
        self.keys_pressed = set()
        # self.schedule_interval(self._button_held, .15)

    def _button_held(self, dt):
        keyspressed = [pyglet.window.key.symbol_string(k) for k in self.keys_pressed]
        if len(keyspressed) > 0:
            for k in keyspressed:
                self._update_pos(k, self.move_step)
    
    def on_key_press(self, key, modifiers):
        self.keys_pressed.add(key)
        keyspressed = [pyglet.window.key.symbol_string(k) for k in self.keys_pressed]
        if not self.are_actions_running() and len(keyspressed) > 0:
            for k in keyspressed:
                self._update_pos(k, self.move_step)
        if self.pressed is False:
            self.pressed = True
            self.schedule_interval(self._button_held, .15)

    def on_key_release(self, key, modifiers):
        self.keys_pressed.discard(key)
        if len(self.keys_pressed) is 0:
            self.pressed = False
            self.unschedule(self._button_held)

    def _update_pos(self, dir, step):
        keyspressed = [pyglet.window.key.symbol_string(k) for k in self.keys_pressed]
        sp = self.get(self.cur_spritename)
        x,y = sp.position
        if dir == 'DOWN':
            sp.do(Place((x, y - step)))
        elif dir == 'UP':
            sp.do(Place((x, y + step)))
        elif dir == 'RIGHT':
            sp.do(Place((x + step, y)))
        elif dir == 'LEFT':
            sp.do(Place((x - step, y)))

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








