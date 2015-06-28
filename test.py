# __author__ = 'henry'
from tetris import *
from coco import *

def movement_test():
    board = Board()
    board.new_block('l')
    board.drop_block()
    print(str(board))

    board.new_block('s')
    print(str(board))
    while board.current_block:    
        process_input(board)
        print(str(board))
        update(board)
        print(str(board))
        render(board)
        sleep(.1)
        # hacky
        if board.current_block is None: 
            break

    board.new_block('z')
    print(board)
    board.rotate_block('clockwise')
    print(board)
    board.move_block_right()
    print(board)
    print(board)

    while board.new_block:    
        process_input(board)
        print(board)
        update(board)
        print(board)
        render(board)
        sleep(.1)    
        if not board.new_block:
            break


def render_test():
    # cocos.director.director.init()
    #cocos.director.director.run(cocos.scene.Scene(HelloWorld()))
    pass
###############################################################################

movement_test()