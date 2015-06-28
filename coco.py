# __author__ = 'henry'
from __future__ import division, print_function, unicode_literals
import tetris, cocos, sys, os
from cocos.director import director
from cocos.text import Label
from cocos import actions


class BoardLayer(cocos.layer.ColorLayer):
    is_event_handler = True
    board = None
    label = None

    def __init__(self):
        super(BoardLayer, self).__init__(64, 64, 224, 255)
        self.board = tetris.Board()
        print("doing this over and over")
        self.label = Label(
            str(self.board),
            font_name='Times New Roman',
            font_size=12,
            anchor_x='center', anchor_y='center'
        )        
        self.label.position = 320, 240
        self.label.board = self.board
        self.add(self.label)
        self.label.do(actions.Repeat(MyMoveDown(.3)))


class MyMoveDown(actions.base_actions.IntervalAction):
    def __init__(self, duration):
        super(MyMoveDown, self).__init__()
        self.duration = duration

    def start(self):
        print(self.target.board.current_block)        
        if not self.target.board.current_block:
            self.target.board.new_block('l')
        if self.target.board.can_move_block('down'):
            self.target.board.move_block_down()
        else:
            self.target.board.drop_block()  # dropping erases block
        print(self.target.board)


if __name__ == "__main__":
    director.init()
    # make a layer, make a scene with this layer, then have directory run it
    # if the layer is an event handler, it's probably pushed into the emitter of mouse/key events
    director.run(cocos.scene.Scene(BoardLayer()))
