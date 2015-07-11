from __future__ import division, print_function, unicode_literals
import tetris, cocos, sys, os, pyglet
from cocos import tiles, layer
from cocos.director import director
from cocos.text import Label
from cocos.actions import *
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class ProtoTetrisLayer(cocos.layer.ColorLayer):
    is_event_handler = True
    board = tetris.Board()

    def __init__(self):
        super(ProtoTetrisLayer, self).__init__(64,64,224,255)
        sprite = cocos.sprite.Sprite('grossini.png')
        sprite.position = 320, 240
        self.add(sprite, z=1, name='gross')
        self.keys_pressed = set()
        self.schedule_interval(self.act_on_input, .033) 
        # self.schedule_interval(self.act_on_sched, 1)

    def on_key_press(self, key, modifiers):
        self.keys_pressed.add(key)

    def on_key_release(self, key, modifiers):
        self.keys_pressed.discard(key)

    def act_on_input(self, dt):
        key_names = [pyglet.window.key.symbol_string (k) for k in self.keys_pressed]
        if len(key_names) > 0:
            for k in key_names:
                self.update_pos(k, 5)

    def act_on_sched(self, dt):
        self.update_pos('DOWN', 50)

    def update_pos(self, dir, step):
        key_names = [pyglet.window.key.symbol_string (k) for k in self.keys_pressed]
        sprite = self.get('gross')
        print("\n" + dir)
        x,y = sprite.position
        if dir == 'DOWN':
            print(key_names)
            sprite.do(Place((x,y-step)))
        elif dir == 'UP':
            print(key_names)
            sprite.do(Place((x,y+step)))
        elif dir == 'RIGHT':
            print(key_names) 
            sprite.do(Place((x+step,y)))            
        elif dir == 'LEFT':
            print(key_names)
            sprite.do(Place((x-step,y)))
        x,y = sprite.position
        print("({},{})".format(x, y))

# class ProtoBoardLayer(cocos.layer.RectMapLayer):
#     def __init__(self, board):
#         super(ProtoBoardLayer, self).__init__()
#         pass

if __name__ == "__main__":
    director.init(resizable=True)
    director.show_FPS = True
    map = tiles.load('tetris.xml')['map0']

    sprite_layer = layer.ScrollableLayer()
    sprite = cocos.sprite.Sprite('grossini.png')

    imgs = [pyglet.resource.image('sprites/cellblue.png'),
            pyglet.resource.image('sprites/cellgreen.png'),
            pyglet.resource.image('sprites/cellred.png')]
    anim = pyglet.image.Animation.from_image_sequence(imgs, 0.5, True)
    anim_sprite = cocos.sprite.Sprite(anim)

    sprite_layer.add(sprite) 
    sprite_layer.add(anim_sprite)

    scroller = layer.ScrollingManager()
    scroller.add(map)
    scroller.add(sprite_layer)
    mainscene = cocos.scene.Scene(scroller)
    mainscene2 = cocos.scene.Scene(ProtoTetrisLayer())
    # make a layer, make a scene with this layer, then have directory run it
    # if the layer is an event handler, it's probably pushed into the emitter of mouse/key events
    # director.run(cocos.scene.Scene(ProtoTetrisLayer()))
    director.run(mainscene)
