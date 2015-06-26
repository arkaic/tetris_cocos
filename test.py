# __author__ = 'henry'
from tetris import *

board = Board()
board.new_block('l')
board.drop_block()
print(board)

board.new_block('z')
print(board)
while board.new_block:    
    process_input(board)
    print(board)
    update(board)
    print(board)
    render(board)
    sleep(.3)    
