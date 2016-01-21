from random import randrange

import tetris_game

blockmap = ['L', 'J', 'I', 'O', 'S', 'Z', 'T']

def make_tetris_block(board_layer, name=None):
    if name is None:
        name = blockmap[randrange(7)]
    block = tetris_game.Block(name, board_layer)

    # Handle all field settings for the block below
    # Get block bounding locations for individual squares and the graphic image
    # for the block
    img = None
    bounding_locations = None
    if name == 'I':
        img = board_layer.sandbox.cells[0][0].tile.image
        bounding_locations = [(-1, 1), (0, 1), (1, 1), (2, 1)]
    elif name == 'J':
        img = board_layer.sandbox.cells[0][1].tile.image
        bounding_locations = [(-1, 1), (-1, 0), (0, 0), (1, 0)]
    elif name == 'L':
        img = board_layer.sandbox.cells[0][2].tile.image
        bounding_locations = [(-1, 0), (0, 0), (1, 0), (1, 1)]
    elif name == 'O':
        img = board_layer.sandbox.cells[0][3].tile.image
        bounding_locations = [(0, 1), (0, 0), (1, 1), (1, 0)]
    elif name == 'S':
        img = board_layer.sandbox.cells[0][4].tile.image
        bounding_locations = [(-1, 0), (0, 0), (0, 1), (1, 1)]
    elif name == 'T':
        img = board_layer.sandbox.cells[0][6].tile.image
        bounding_locations = [(-1, 0), (0, 1), (0, 0), (1, 0)]
    elif name == 'Z':
        img = board_layer.sandbox.cells[0][5].tile.image
        bounding_locations = [(-1, 1), (0, 1), (0, 0), (1, 0)]

    # Set block location
    if name == 'I':
        block.location = (4, 19)
    else:
        block.location = (4, 20)

    # make squares for each bounding
    # Add to block's list of squares, the square matrix representing tetris grid
    # and map the square to its bounding coordinate
    for bounding_loc in bounding_locations:
        # block's location is offset with bounding to get tetris grid location
        square_x = bounding_loc[0] + block.location[0]
        square_y = bounding_loc[1] + block.location[1]
        square = make_tetris_square(img, block, (square_x, square_y))
        block.squares.append(square)
        block.squares_matrix[square_x][square_y] = square
        block.bounding_locations_map[square] = bounding_loc

    return block

def make_tetris_square(img, block, loc):
    square = tetris_game.Square(img, block, loc)
    return square
