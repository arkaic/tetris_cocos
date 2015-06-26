# __author__ = 'henry'
from tetris import Board, Block

board = Board()
board.new_block(Block('t'))
board.drop_block()
print(board)
