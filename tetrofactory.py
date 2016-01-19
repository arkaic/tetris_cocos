import tetris_game

block_map = ['L', 'J', 'I', 'O', 'S', 'Z', 'T']

def makeblock(boardlayer, name=None):
    block = tetris_game.Block(name, boardlayer, rotated_state)
    img = None
    if name is None:
        name = block_map[randrange(7)]
    elif name == 'I':
        block._corelocation = (4, 19)
        img = board_layer.sandbox.cells[0][0].tile.image
        block.bounding_locations = [(-1, 1), (0, 1), (1, 1), (2, 1)]
    elif name == 'J':
        block._corelocation = (4, 20)
        img = board_layer.sandbox.cells[0][1].tile.image
        block.bounding_locations = [(-1, 1), (-1, 0), (0, 0), (1, 0)]
    elif name == 'L':
        block._corelocation = (4, 20)
        img = board_layer.sandbox.cells[0][2].tile.image
        block.bounding_locations = [(-1, 0), (0, 0), (1, 0), (1, 1)]
    elif name == 'O':
        block._corelocation = (4, 20)
        img = board_layer.sandbox.cells[0][3].tile.image
        block.bounding_locations = [(0, 1), (0, 0), (1, 1), (1, 0)]
    elif name == 'S':
        block._corelocation = (4, 20)
        img = board_layer.sandbox.cells[0][4].tile.image
        block.bounding_locations = [(-1, 0), (0, 0), (0, 1), (1, 1)]
    elif name == 'T':
        block._corelocation = (4, 20)
        img = board_layer.sandbox.cells[0][6].tile.image
        block.bounding_locations = [(-1, 0), (0, 1), (0, 0), (1, 0)]
    elif name == 'Z':
        block._corelocation = (4, 20)
        img = board_layer.sandbox.cells[0][5].tile.image
        block.bounding_locations = [(-1, 1), (0, 1), (0, 0), (1, 0)]

    # Add sprites to both the member list and the grid model
    for bounding_coord in block.bounding_locations:
        # make square and reference sprite            
        square = tetris_game.Square(img, block)
        sprite = square.sprite
        block.squares.append(square)
        sprite_x, sprite_y = block.grid_coord(sprite)
        block.squares_matrix[sprite_x][sprite_y] = sprite
            
    return block
