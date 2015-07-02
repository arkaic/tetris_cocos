# __author__ = 'henry'
from __future__ import division, print_function, unicode_literals
import tetris, cocos, sys, os, pyglet
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

if __name__ == "__main__":
    director.init()
    director.show_FPS = True
    # make a layer, make a scene with this layer, then have directory run it
    # if the layer is an event handler, it's probably pushed into the emitter of mouse/key events
    director.run(cocos.scene.Scene(ProtoTetrisLayer()))
