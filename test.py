# __author__ = 'henry'
from tetris import Board, Block

board = Board()

board.new_block(Block('t'))
board.drop_block()
print(board)

board.new_block(Block('z'))
board.drop_block()
print(board)

board.new_block(Block('l'))
print(board)
board.rotate_block('counterclockwise')
print(board)
board.drop_block()
print(board)
