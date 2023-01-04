import os
import sys
import pygame

WHITE = 1
BLACK = 2
WIDTH = 1700
HEIGHT = 900
BOARD_SIZE = 800


def load_image(name, colorkey=None):
    fullname = os.path.join('figures', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    return image


def castling(field: list, row: int, col: int, col1: int, step: int) -> bool:
    if step == -1:
        col -= 1
    else:
        col += 1
    for i in range(col, col1, step):
        if field[row][i]:
            print(field[row][i])
            return False
    return True


def check(field):
    result = [False, False]
    for r in field.field:
        for p in r:
            if isinstance(p, King):
                color = opponent(p.color)
                if any(map(lambda x: x.can_attack(field, *get_cell((x.rect.y, x.rect.x)),
                                                  *get_cell(((p.rect.y, p.rect.x) if (isinstance(x, King) or
                                                                                      isinstance(x, Rook))
                                                  else (p.rect.x, p.rect.y)))),
                           filter(lambda x: x.color == color,
                                  [x for x in all_pieces.sprites()]))):
                    if color == BLACK:
                        result[0] = True
                    else:
                        result[1] = True
    return result


def opponent(color):
    if color == WHITE:
        return BLACK
    else:
        return WHITE


def correct_coords(row, col):
    '''Функция проверяет, что координаты (row, col) лежат
    внутри доски'''
    return 0 <= row < 8 and 0 <= col < 8


def get_cell(coords):
    ny = (coords[1] - (HEIGHT - BOARD_SIZE - 50)) // cell_size
    nx = (coords[0] - (WIDTH - BOARD_SIZE - 50)) // cell_size
    return nx, ny


def get_pixels(coords):
    ny = coords[1] * cell_size + HEIGHT - BOARD_SIZE - 50
    nx = coords[0] * cell_size + WIDTH - BOARD_SIZE - 50
    return nx, ny


def draw_menu(screen, board):
    pygame.draw.rect(screen, 'black', (WIDTH - BOARD_SIZE - 75, HEIGHT - BOARD_SIZE - 75,
                                       BOARD_SIZE + 50, BOARD_SIZE + 50))
    pygame.draw.rect(screen, 'black', (25, 25, 775, 600), 5)
    pygame.draw.rect(screen, 'black', (25, 25, 775, 115), 5)
    pygame.draw.rect(screen, 'black', (150, 750, 525, 125), 5)
    pygame.draw.rect(screen, '#660000', (155, 755, 515, 115))
    surr_text = pygame.font.Font(None, 50).render('Сдаться', True, 'white')
    screen.blit(surr_text, (413 - surr_text.get_width() // 2, 813 - surr_text.get_height() // 2))
    turn = pygame.font.Font(None, 50).render('Ход ' + ('белых' if board.color == WHITE else 'чёрных'),
                                             True, 'white')
    screen.blit(turn, (150 - turn.get_width() // 2, 80 - turn.get_height() // 2))
    checks = check(board)
    if checks[0]:
        check_text = pygame.font.Font(None, 50).render('Шах белым', True, 'white')
        screen.blit(check_text, (660 - check_text.get_width() // 2,
                                 55 - check_text.get_height() // 2))
    if checks[1]:
        check_text = pygame.font.Font(None, 50).render('Шах чёрным', True, 'white')
        screen.blit(check_text, (660 - check_text.get_width() // 2,
                                 105 - check_text.get_height() // 2))

def draw_possible_moves(board, row, col):
    for i in range(8):
        for j in range(8):
            piece = board.field[row][col]
            if (piece.can_attack(board, *[*get_cell((piece.rect.x + 1, piece.rect.y + 1))][::-1], i, j) and
                  board.field[i][j]):
                if board.field[i][j].color == opponent(piece.color):
                    pygame.draw.rect(screen, 'red', (*get_pixels((j, i)), cell_size, cell_size), 5)
            elif piece.can_move(board, *[*get_cell((piece.rect.x + 1, piece.rect.y + 1))][::-1], i, j):
                pygame.draw.circle(screen, 'green',
                                   tuple(map(lambda z: z + cell_size // 2, get_pixels((j, i)))), 10)
    pygame.draw.rect(screen, 'green', (*get_pixels((col, row)), cell_size, cell_size), 5)
    pygame.display.flip()


class Board(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(all_sprites)
        self.color = WHITE
        self.field = []
        self.indent_h = WIDTH - BOARD_SIZE - 50
        self.indent_v = HEIGHT - BOARD_SIZE - 50
        for row in range(8):
            self.field.append([None] * 8)
        self.field[0] = [
            Rook(WHITE, self.indent_h, self.indent_v),
            Knight(WHITE, self.indent_h + cell_size, self.indent_v),
            Bishop(WHITE, self.indent_h + cell_size * 2, self.indent_v),
            King(WHITE, self.indent_h + cell_size * 3, self.indent_v),
            Queen(WHITE, self.indent_h + cell_size * 4, self.indent_v),
            Bishop(WHITE, self.indent_h + cell_size * 5, self.indent_v),
            Knight(WHITE, self.indent_h + cell_size * 6, self.indent_v),
            Rook(WHITE, self.indent_h + cell_size * 7, self.indent_v)
        ]
        self.field[1] = [Pawn(WHITE, self.indent_h + cell_size * i, self.indent_v + cell_size) for i in range(8)]

        self.field[6] = [Pawn(BLACK, self.indent_h + cell_size * i, self.indent_v + cell_size * 6) for i in range(8)]

        self.field[7] = [
            Rook(BLACK, self.indent_h, self.indent_v + cell_size * 7),
            Knight(BLACK, self.indent_h + cell_size, self.indent_v + cell_size * 7),
            Bishop(BLACK, self.indent_h + cell_size * 2, self.indent_v + cell_size * 7),
            King(BLACK, self.indent_h + cell_size * 3, self.indent_v + cell_size * 7),
            Queen(BLACK, self.indent_h + cell_size * 4, self.indent_v + cell_size * 7),
            Bishop(BLACK, self.indent_h + cell_size * 5, self.indent_v + cell_size * 7),
            Knight(BLACK, self.indent_h + cell_size * 6, self.indent_v + cell_size * 7),
            Rook(BLACK, self.indent_h + cell_size * 7, self.indent_v + cell_size * 7)
        ]
        self.image = pygame.Surface((800, 800))
        self.rect = pygame.Rect(WIDTH - BOARD_SIZE - 50, HEIGHT - BOARD_SIZE - 50, WIDTH - 25, HEIGHT - 25)
        self.image.fill('#f0dab5')
        for i in range(0, WIDTH, cell_size):
            for j in range(0 if i % (cell_size * 2) == 0 else cell_size, WIDTH, cell_size * 2):
                pygame.draw.rect(self.image, '#b58763', (i, WIDTH - j - cell_size, cell_size, cell_size))

    def current_player_color(self):
        return self.color

    def cell(self, row, col):
        '''Возвращает строку из двух символов. Если в клетке (row, col)
        находится фигура, символы цвета и фигуры. Если клетка пуста,
        то два пробела.'''
        piece = self.field[row][col]
        if piece is None:
            return '  '
        color = piece.get_color()
        c = 'w' if color == WHITE else 'b'
        return c + piece.char()

    def get_piece(self, row, col):
        if correct_coords(row, col):
            return self.field[row][col]
        else:
            return None

    def move_piece(self, col, row):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                if (event.type == pygame.MOUSEBUTTONDOWN and
                        (self.indent_h <= event.pos[0] <= self.indent_h + BOARD_SIZE and
                         self.indent_v <= event.pos[1] <= self.indent_v + BOARD_SIZE)):
                    col1, row1 = get_cell(event.pos)
                    if not correct_coords(row, col) or not correct_coords(row1, col1):
                        return False
                    if (col, row) == (col1, row1):
                        return False
                    piece = self.field[row][col]
                    if self.field[row1][col1] is None:
                        if not piece.can_move(self, row, col, row1, col1):
                            return False
                    else:
                        if piece.can_attack(self, row, col, row1, col1) and self.field[row1][col1].color != piece.color:
                            pygame.sprite.spritecollide(self.field[row1][col1], all_pieces, True)
                            self.field[row1][col1] = None
                        elif (row == row1 and
                              self.field[row1][col1].char() == 'R' and
                              self.field[row][col].char() == 'K' and
                              self.field[row][col].turn == 0):
                            step = -1 if col >= col1 else 1
                            if castling(self.field, row, col, col1, step):
                                rook = self.field[row1][col1]
                                if step == -1:
                                    self.field[row][col] = None
                                    self.field[row][col - 2] = piece
                                    self.field[row1][col1] = None
                                    self.field[row1][col1 + 2] = rook
                                    piece.rect.x, piece.rect.y = get_pixels((col - 2, row))
                                    rook.rect.x, piece.rect.y = get_pixels((col1 + 2, row1))
                                elif step == 1:
                                    self.field[row][col] = None
                                    self.field[row][col + 2] = piece
                                    self.field[row1][col1] = None
                                    self.field[row1][col1 - 3] = rook
                                    piece.rect.x, piece.rect.y = get_pixels((col + 2, row))
                                    rook.rect.x, piece.rect.y = get_pixels((col1 - 3, row1))
                                self.color = opponent(self.color)
                                piece.turn += 1
                                check(self)
                                return True
                            else:
                                return False
                        else:
                            return False
                    self.field[row][col] = None  # Снять фигуру.
                    self.field[row1][col1] = piece  # Поставить на новое место.
                    piece.rect.x, piece.rect.y = get_pixels((col1, row1))
                    self.color = opponent(self.color)
                    if piece.char() == 'K':
                        piece.turn += 1
                    check(self)
                    return True
            draw_possible_moves(board, row, col)

    def surrender(self):
        pass


class Rook(pygame.sprite.Sprite):
    def __init__(self, color, x, y):
        super().__init__(all_sprites, all_pieces)
        self.color = color
        if self.color == WHITE:
            self.image = load_image('Wrook.png')
        else:
            self.image = load_image('brook.png')
        self.image = pygame.transform.scale(self.image, (cell_size, cell_size))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y

    def get_color(self):
        return self.color

    def char(self):
        return 'R'

    def can_move(self, board, row, col, row1, col1):
        if row1 == row and col1 == col:
            return False

        if row != row1 and col != col1:
            return False

        step = 1 if (row1 >= row) else -1
        for r in range(row + step, row1, step):
            if not (board.get_piece(r, col) is None):
                return False

        step = 1 if (col1 >= col) else -1
        for c in range(col + step, col1, step):
            if not (board.get_piece(row, c) is None):
                return False

        return True

    def can_attack(self, board, row, col, row1, col1):
        return self.can_move(board, row, col, row1, col1)


class Pawn(pygame.sprite.Sprite):
    def __init__(self, color, x, y):
        super().__init__(all_sprites, all_pieces)
        self.coords = get_cell((x, y))
        self.color = color
        if self.color == WHITE:
            self.image = pygame.transform.scale(load_image('Wpawn.png'), (cell_size, cell_size))
        else:
            self.image = pygame.transform.scale(load_image('bpawn.png'), (cell_size, cell_size))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y

    def get_color(self):
        return self.color

    def char(self):
        return 'P'

    def can_move(self, board, row, col, row1, col1):
        if col != col1:
            return False

        if self.color == WHITE:
            direction = 1
            start_row = 1
        else:
            direction = -1
            start_row = 6

        if row + direction == row1 and board.field[row1][col] is None:
            return True

        if (row == start_row
                and row + 2 * direction == row1
                and board.field[row + direction][col] is None
                and board.field[row1][col] is None):
            return True

        return False

    def can_attack(self, board, row, col, row1, col1):
        if row1 == row and col1 == col:
            return False
        direction = 1 if (self.color == WHITE) else -1
        return (row + direction == row1
                and (col + 1 == col1 or col - 1 == col1))


class Knight(pygame.sprite.Sprite):
    def __init__(self, color, x, y):
        super().__init__(all_sprites, all_pieces)
        self.color = color
        if self.color == WHITE:
            self.image = load_image("Wknight.png")
        else:
            self.image = load_image("bknight.png")
        self.image = pygame.transform.scale(self.image, (cell_size, cell_size))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y

    def get_color(self):
        return self.color

    def char(self):
        return 'N'  # kNight, буква 'K' уже занята королём

    def can_move(self, board, row, col, row1, col1):
        delta_row = abs(row1 - row)
        delta_col = abs(col1 - col)
        if row1 == row and col1 == col:
            return False
        if (delta_row == 2 and delta_col == 1 or
                delta_row == 1 and delta_col == 2):
            return True
        return False

    def can_attack(self, board, row, col, row1, col1):
        return self.can_move(board, row, col, row1, col1)


class King(pygame.sprite.Sprite):
    def __init__(self, color, x, y):
        super().__init__(all_sprites, all_pieces)
        self.coords = get_cell((x, y))
        self.color = color
        self.image = load_image('Wking.png') if self.color == WHITE else load_image('Bking.png')
        self.image = pygame.transform.scale(self.image, (cell_size, cell_size))
        self.rect = self.image.get_rect().move(x, y)
        self.rect.x, self.rect.y = x, y
        self.turn = 0

    def get_color(self):
        return self.color

    def char(self):
        return 'K'

    def can_move(self, board, row, col, row1, col1):
        delta_row = abs(row - row1)
        delta_col = abs(col - col1)
        if delta_row <= 1 and delta_col <= 1:
            if any(map(lambda x: x.can_attack(board, *get_cell((x.rect.y, x.rect.x)),
                                              *((col1, row1) if (isinstance(x, King) or
                                                                 isinstance(x, Rook))
                                              else (row1, col1))),
                       filter(lambda x: x.color == opponent(self.color),
                              [x for x in all_pieces.sprites()]))):
                return False
            return True
        return False

    def can_attack(self, board, row, col, row1, col1):
        return self.can_move(board, row, col, row1, col1)


class Queen(pygame.sprite.Sprite):
    def __init__(self, color, x, y):
        super().__init__(all_sprites, all_pieces)
        self.coords = get_cell((x, y))
        self.color = color
        self.image = load_image('Wqueen.png') if self.color == WHITE else load_image('Bqueen.png')
        self.image = pygame.transform.scale(self.image, (cell_size, cell_size))
        self.rect = self.image.get_rect().move(x, y)
        self.rect.x, self.rect.y = x, y

    def get_color(self):
        return self.color

    def char(self):
        return 'Q'

    def can_move(self, board, row, col, row1, col1):
        delta_row = abs(row1 - row)
        delta_col = abs(col1 - col)
        if row1 == row and col1 == col:
            return False
        if row == row1 or col == col1:
            step = 1 if (row1 >= row) else -1
            for r in range(row + step, row1, step):
                if not (board.get_piece(r, col) is None):
                    return False

            step = 1 if (col1 >= col) else -1
            for c in range(col + step, col1, step):
                if not (board.get_piece(row, c) is None):
                    return False

            return True

        if delta_col == delta_row:
            step = 1 if (row1 >= row) else -1
            direction = 1 if col1 >= col else -1
            for i in range(2, delta_row + 1):
                if board.get_piece(row + i * step - step, col + i * direction - direction):
                    return False
            return True

        return False

    def can_attack(self, board, row, col, row1, col1):
        return self.can_move(board, row, col, row1, col1)


class Bishop(pygame.sprite.Sprite):
    def __init__(self, color, x, y):
        super().__init__(all_sprites, all_pieces)
        self.coords = get_cell((x, y))
        self.color = color
        self.image = load_image('Wbishop.png') if self.color == WHITE else load_image('Bbishop.png')
        self.image = pygame.transform.scale(self.image, (cell_size, cell_size))
        self.rect = self.image.get_rect().move(x, y)
        self.rect.x, self.rect.y = x, y

    def get_color(self):
        return self.color

    def char(self):
        return 'B'

    def can_move(self, board, row, col, row1, col1):
        delta_row = abs(row1 - row)
        delta_col = abs(col1 - col)

        if row1 == row and col1 == col:
            return False

        if delta_row != delta_col:
            return False

        step = 1 if (row1 >= row) else -1
        direction = 1 if col1 >= col else -1
        for i in range(2, delta_row + 1):
            if board.get_piece(row + i * step - step, col + i * direction - direction):
                return False
        return True

    def can_attack(self, board, row, col, row1, col1):
        return self.can_move(board, row, col, row1, col1)


if __name__ == "__main__":
    running = True
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Шах и Мат')
    all_sprites = pygame.sprite.Group()
    all_pieces = pygame.sprite.Group()
    cell_size = BOARD_SIZE // 8
    board = Board()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if (board.indent_h <= x <= board.indent_h + BOARD_SIZE and
                        board.indent_v <= y <= board.indent_v + BOARD_SIZE):
                    x, y = get_cell((x, y))
                    if (not (board.field[y][x] is None) and
                            board.color == board.field[y][x].get_color()):
                        board.move_piece(x, y)
                elif 150 <= x <= 675 and 750 <= y <= 825:
                    board.surrender()
        screen.fill('#404147')
        draw_menu(screen, board)
        all_sprites.update()
        all_sprites.draw(screen)
        pygame.display.flip()
    pygame.quit()
