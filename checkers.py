import pygame
pygame.init()
pygame.font.init()

def grid_to_list(col, row, cols) -> int:
    return int(row*cols + col)

def list_to_grid(num, cols):
    return (num%cols, num//cols)

def flip_bool(b):
    if b:
        b = False
    else:
        b = True
    return b

class Piece():
    white_turn = True
    id = 0
    pieces = []

    def check_win():
        white_win = True
        black_win = True
        win_text = None
        for tile in Board.board_list:
            piece = tile.piece
            if piece is not None:
                if piece.white:
                    black_win = False
                elif not piece.white:
                    white_win = False

        if white_win:
            win_text = "white wins"
        elif black_win:
            win_text = 'black wins'

        return win_text
    
    def __init__(self, white: bool):
        self.white = white
        self.id = Piece.id
        self.king = False
        self.board: Board = None
        Piece.id += 1
        Piece.pieces.append(self)

    def king_check(self, row):
        rows = len(Board.board_list)//Board.board_cols
        if self.white and row == 0:
            self.king = True
        elif row == rows-1:
            self.king = True

    def moves(self, col, row) -> list:
        cols, rows = Board.board_cols, (len(Board.board_list)//Board.board_cols)
        if (Piece.white_turn and self.white) or not (Piece.white_turn or self.white): # if black and black turn or white and white turn
            moves = []
            temp_moves = []
            if self.king:
                temp_moves = [(-1, -1), (1, 1), (-1, 1), (1, -1)]
            else:
                if self.white: # if your white you go up else you go down
                    temp_moves = [(-1, -1), (1, -1)]
                else:
                    temp_moves = [(-1, 1), (1, 1)]

            for move in temp_moves: # gets rid of out of bounds
                nc, nr = col+move[0], row+move[1]
                if (0 <= nc < cols) and (0 <= nr < rows):
                    moves.append(grid_to_list(nc, nr, Board.board_cols))

            for move in sorted(moves, reverse=True):
                tile:Board = Board.board_list[move]

                if tile.piece:
                    moves.remove(move)
                    if (tile.piece.white is not self.white):
                        tc, tr = tile.col, tile.row
                        dc, dr = col+(tc-col)*2, row+(tr-row)*2
                        if Board.board_list[grid_to_list(dc, dr, cols)].piece is None and 0 <= dc < cols and 0<= dr < rows:
                            moves.insert(0, [grid_to_list(dc, dr, cols), move]) # so loop doesnt include it
        else:
            moves = []

        return moves

class Board():
    board_list = []
    board_cols = 0 # ititialised in create board
    tile_size = 0 # initialised in create board

    def create_board(rows, cols, tile_size: float = 10) -> None:
        for r in range(rows):
            for c in range(cols):
                Board.board_list.append(Board(r, c))
        Board.tile_size = tile_size
        Board.board_cols = cols

    def __init__(self, row:int, col:int, piece:Piece = None):
        self.row = row
        self.col = col
        self.piece = piece

class Window():
    selected_piece = None
    cur_tile = None
    WIN_FONT = pygame.font.SysFont('awadeeui', 160)

    def __init__(self, width:int, height:int, fps:int = 60):
        self.width = width
        self.height = height
        self.window = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()
        self.fps = fps

    def draw(self) -> None:

        def draw_board():
            tile: Board
            for tile in Board.board_list:
                r, c = tile.row, tile.col
                tile_size = Board.tile_size
                tile_rect = pygame.Rect((c*tile_size, r*tile_size), (tile_size, tile_size))
                if (r+c) % 2 == 0:
                    color = (193,154,107)
                else:
                    color = (100,65,23)
                pygame.draw.rect(self.window, color, tile_rect)
                if not tile.piece == None:
                    if tile.piece.white:
                        piece_color = 'white'
                    else:
                        piece_color = 'black'
                    pygame.draw.circle(self.window, piece_color, ((c*tile_size+tile_size//2), (r*tile_size+tile_size//2)), tile_size//2.1)
                    if tile.piece.king:
                        pygame.draw.circle(self.window, 'yellow', ((c*tile_size+tile_size//2), (r*tile_size+tile_size//2)), tile_size//5)


        def draw_selected_piece_to_cursor():
            if self.selected_piece is not None:
                x, y = pygame.mouse.get_pos()
                if self.selected_piece.white:
                    piece_color = 'white'
                else:
                    piece_color = 'black'
                pygame.draw.circle(self.window, piece_color, (x, y), Board.tile_size//2.1)
                if self.selected_piece.king:
                    pygame.draw.circle(self.window, 'yellow', (x, y), Board.tile_size//5)

        def draw_moves():
            if self.selected_piece is not None:
                tile_size = Board.tile_size
                r, c = self.cur_tile.row, self.cur_tile.col
                moves = self.selected_piece.moves(c, r)
                for move in moves:
                    try:
                        move = move[0]
                    except:
                        pass                    
                    c, r = list_to_grid(move, Board.board_cols)
                    pygame.draw.circle(self.window, 'red', ((c*tile_size+tile_size//2), (r*tile_size+tile_size//2)), tile_size//4)

        def draw_win_text():
            if Piece.check_win() is not None:
                text = Piece.check_win()
                win_text = self.WIN_FONT.render(text, 1, 'green')
                self.window.blit(win_text, (0, 0))


        self.window.fill('black') # refreshes screen
        draw_board() # draws board
        draw_moves() # draws movable moves
        draw_selected_piece_to_cursor() # draws mouse to curser
        draw_win_text()
        pygame.display.update() # updates screen

    def run(self) -> None:
        def mouse_to_grid() -> tuple[int]:
            x, y = pygame.mouse.get_pos()
            return x//Board.tile_size, y//Board.tile_size
        
        def mouse_to_list() -> int:
            col, row = mouse_to_grid()
            return grid_to_list(col, row, Board.board_cols)

        # BOARD INITALIZING
        Board.create_board(8, 8, tile_size=600/8)
        black_starting_pos = [(1, 0), (3, 0), (5, 0), (7, 0), (0, 1), (2, 1), (4, 1), (6, 1), (1, 2), (3, 2), (5, 2), (7, 2)]
        white_starting_pos = [(0, 7), (2, 7), (4, 7), (6, 7), (1, 6), (3, 6), (5, 6), (7, 6), (0, 5), (2, 5), (4, 5), (6, 5)]
        for starting_pos in black_starting_pos:
            x, y = starting_pos
            idx = grid_to_list(x, y, Board.board_cols)
            Board.board_list[idx].piece = Piece(False)
        for starting_pos in white_starting_pos:
            x, y = starting_pos
            idx = grid_to_list(x, y, Board.board_cols)
            Board.board_list[idx].piece = Piece(True)
        
        # GAME INITIALIZING
        right_click = False
        run = True

        # MAIN GAME LOOP
        while run:
            self.clock.tick(self.fps)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    idx = mouse_to_list()
                    if 0 <= idx < len(Board.board_list):
                        tile:Board = Board.board_list[idx]
                        if tile.piece is not None:
                            self.selected_piece:Piece = tile.piece
                            self.cur_tile = tile # sets cur tile to old tile
                            self.cur_tile.piece = None # removes piece from old tile
                
                right_click = pygame.mouse.get_pressed()[2]

                if ((event.type == pygame.MOUSEBUTTONUP and event.button == 1) or (right_click)) and (self.selected_piece is not None and self.cur_tile is not None):
                    movable = False
                    col, row = self.cur_tile.col, self.cur_tile.row
                    idx = mouse_to_list()
                    moves = self.selected_piece.moves(col, row)
                    cur_move = None
                    for move in moves:
                        cur_move = move
                        try:
                            move = move[0]
                        except:
                            pass
                        if move == idx:
                            movable = True
                            break
                    if movable and (0 <= col < Board.board_cols) and (0 <= row < len(Board.board_list)//Board.board_cols) and not right_click: # fix drop code
                        new_tile:Board = Board.board_list[idx]
                        try:
                            if cur_move[1] is not None:
                                tile = Board.board_list[cur_move[1]]
                                tile.piece = None
                        except:
                            Piece.white_turn = flip_bool(Piece.white_turn)
                        new_tile.piece = self.selected_piece
                        new_tile.piece.king_check(idx//Board.board_cols)
                    else:
                        self.cur_tile.piece = self.selected_piece # snaps piece back to old position
                    self.cur_tile = None
                    self.selected_piece = None

            self.draw()

        pygame.quit()

if __name__ == "__main__":
    window = Window(600, 600)
    window.run()