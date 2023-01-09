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
            return False
    return True


def pawn_conversion(board):
    for piece in filter(lambda x: isinstance(x, Pawn), all_pieces):
        x, y = get_cell((piece.rect.x, piece.rect.y))
        if (piece.color == WHITE and y == 7 or
                (piece.color == BLACK and y == 0)):
            choice = draw_selection_dialog()
            board.field[y][x] = choice(piece.color, piece.rect.x, piece.rect.y)
            all_pieces.remove(piece)
            all_sprites.remove(piece)


def check(field):
    result = [False, False]
    for r in field.field:
        for p in r:
            if isinstance(p, King):
                color = opponent(p.color)
                col1, row1 = get_cell((p.rect.x, p.rect.y))

                if any(
                        map(
                            lambda x: x.can_attack(field,
                                                   get_cell((x.rect.x, x.rect.y))[1],
                                                   get_cell((x.rect.x, x.rect.y))[0],
                                                   row1,
                                                   col1),
                            filter(
                                lambda x: x.color == color,
                                [x for x in all_pieces.sprites()]
                            )
                        )
                ):
                    if color == BLACK:
                        result[0] = True
                    else:
                        result[1] = True
    return result


def checkmate(color, board):
    king_x = 0
    king_y = 0
    tking = None
    check_figures = []
    figures = [*filter(lambda x: x.color == opponent(color), all_pieces.sprites())]
    opponent_figures = [*filter(lambda x: x.color == color, all_pieces.sprites())]

    for k in board.field:
        for king in k:
            if isinstance(king, King) and king.color == color:
                tking = king
                king_y, king_x = get_cell((king.rect.x, king.rect.y))

    for figure in figures:
        if figure.can_attack(board,
                             get_cell((figure.rect.x, figure.rect.y))[1],
                             get_cell((figure.rect.x, figure.rect.y))[0],
                             king_x,
                             king_y):
            check_figures.append(figure)

    king_moves = [tking.can_move(board, king_x, king_y, king_x + 1, king_y + 1),
                  tking.can_move(board, king_x, king_y, king_x, king_y + 1),
                  tking.can_move(board, king_x, king_y, king_x + 1, king_y),
                  tking.can_move(board, king_x, king_y, king_x - 1, king_y + 1),
                  tking.can_move(board, king_x, king_y, king_x, king_y - 1),
                  tking.can_move(board, king_x, king_y, king_x - 1, king_y - 1),
                  tking.can_move(board, king_x, king_y, king_x + 1, king_y - 1),
                  tking.can_move(board, king_x, king_y, king_x - 1, king_y)]

    if len(check_figures) == 1 and not any(king_moves):
        for figure in opponent_figures:
            if any(map(lambda x:
                       figure.can_attack(board,
                                         get_cell((figure.rect.x, figure.rect.y))[1],
                                         get_cell((figure.rect.x, figure.rect.y))[0],
                                         get_cell((x.rect.x, x.rect.y))[1],
                                         get_cell((x.rect.x, x.rect.y))[0]
                                         ),
                       check_figures)):
                print('so close')
                break

    if not any(king_moves) and check_figures:
        for figure in opponent_figures:
            pass
    pass


def win_check(board):
    kings = []
    for row in board.field:
        for piece in row:
            if isinstance(piece, King):
                kings.append(piece)
    if len(kings) == 1:
        return kings[0].color
    else:
        return False


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


def draw_game_menu(screen, board):
    pygame.draw.rect(screen, 'black', (WIDTH - BOARD_SIZE - 75, HEIGHT - BOARD_SIZE - 75,
                                       BOARD_SIZE + 50, BOARD_SIZE + 50))

    pygame.draw.rect(screen, 'black', (25, 100, 775, 600), 5)
    pygame.draw.rect(screen, 'black', (25, 100, 775, 115), 5)

    pygame.draw.rect(screen, 'black', (25, 25, 300, 60), 5)
    return_text = pygame.font.Font(None, 40).render('<- На главное меню', True, 'white')
    screen.blit(return_text, (175 - return_text.get_width() // 2, 55 - return_text.get_height() // 2))

    pygame.draw.rect(screen, 'black', (150, 750, 525, 125), 5)
    pygame.draw.rect(screen, '#660000', (155, 755, 515, 115))
    surr_text = pygame.font.Font(None, 50).render('Сдаться', True, 'white')
    screen.blit(surr_text, (413 - surr_text.get_width() // 2, 813 - surr_text.get_height() // 2))

    turn = pygame.font.Font(None, 50).render('Ход ' + ('белых' if board.color == WHITE else 'чёрных'),
                                             True, 'white')
    screen.blit(turn, (150 - turn.get_width() // 2, 155 - turn.get_height() // 2))

    checks = check(board)
    if checks[0]:
        check_text = pygame.font.Font(None, 50).render('Шах белым', True, 'white')
        screen.blit(check_text, (660 - check_text.get_width() // 2,
                                 130 - check_text.get_height() // 2))
    if checks[1]:
        check_text = pygame.font.Font(None, 50).render('Шах чёрным', True, 'white')
        screen.blit(check_text, (660 - check_text.get_width() // 2,
                                 180 - check_text.get_height() // 2))


def draw_win_screen(winner):
    v = 350
    fps = 60
    clock = pygame.time.Clock()
    y = -500
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if y < 150:
                    y = 150
                else:
                    mx, my = event.pos
                    if 375 <= mx <= 675 and 550 <= my <= 625:
                        return 1
                    elif 725 <= mx <= 1025 and 550 <= my <= 625:
                        return 2
                    elif 1075 <= mx <= 1375 and 550 <= my <= 625:
                        return 3
        if y >= 150:
            y = 150
        else:
            y += v / fps
        clock.tick(fps)
        screen.fill('#404147')
        draw_game_menu(screen, board)
        all_sprites.update()
        all_sprites.draw(screen)
        pygame.draw.rect(screen, '#404147', (300, y, 1150, 600))
        pygame.draw.rect(screen, 'black', (300, y, 1150, 600), 5)
        for _ in range(3):
            text = ['На главное меню', 'Реванш', 'Анализ партии'][_]
            pygame.draw.rect(screen, 'black', (375 + 350 * _, y + 400, 300, 75), 5)
            text = pygame.font.Font(None, 45).render(text, True, 'white')
            screen.blit(text, (525 + 350 * _ - text.get_width() // 2, y + 435 - text.get_height() // 2))
        text = pygame.font.Font(None, 70).render('Победа ' + ('белых' if winner == WHITE else 'чёрных'), True, 'white')
        screen.blit(text, (875 - text.get_width() // 2, y + 150 - text.get_height() // 2))
        pygame.display.flip()


def draw_main_menu(main_menu):
    text = pygame.font.Font(None, 100).render('Шах и Мат', True, 'white')
    main_menu.blit(text, (400 - text.get_width() // 2, 150 - text.get_height() // 2))
    for _ in range(3):
        text = ['Играть', 'Анализ партии', 'Испытания'][_]
        pygame.draw.rect(main_menu, 'black', (250, 225 + 95 * _, 300, 75), 5)
        btn_text = pygame.font.Font(None, 45).render(text, True, 'white')
        main_menu.blit(btn_text, (400 - btn_text.get_width() // 2, 260 + 95 * _ - btn_text.get_height() // 2))


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


def draw_selection_dialog():
    while True:
        pygame.draw.rect(screen, '#404147', (cell_size + board.indent_h, cell_size * 3 + board.indent_v,
                                             cell_size * 6, cell_size * 2))
        text = pygame.font.Font(None, 50).render('Выберите фигуру', True, 'white')
        screen.blit(text, (cell_size + board.indent_h + cell_size * 3 - text.get_width() // 2,
                           cell_size * 3.25 + board.indent_v - text.get_height() // 2))
        x, y = cell_size + board.indent_h + 25, cell_size * 3 + board.indent_v + 60
        for i in range(4):
            piece = ['rook', 'knight', 'bishop', 'queen'][i]
            screen.blit(pygame.transform.scale(load_image(f'W{piece}.png' if board.color == BLACK else f'b{piece}.png'),
                                               (cell_size, cell_size)), (x + 150 * i, y))
            pygame.draw.rect(screen, 'white',
                             (x + 150 * i, y, cell_size, cell_size), 5)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if x <= event.pos[0] <= x + 100 and y <= event.pos[1] <= y + cell_size:
                    return Rook
                elif x + 150 <= event.pos[0] <= x + 250 and y <= event.pos[1] <= y + cell_size:
                    return Knight
                elif x + 300 <= event.pos[0] <= x + 400 and y <= event.pos[1] <= y + cell_size:
                    return Bishop
                elif x + 450 <= event.pos[0] <= x + 550 and y <= event.pos[1] <= y + cell_size:
                    return Queen


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
                    pawn_conversion(self)
                    checkmate(self.color, self)
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
            if not (board.get_piece(r, col1) is None):
                return False

        step = 1 if (col1 >= col) else -1
        for c in range(col + step, col1, step):
            if not (board.get_piece(row1, c) is None):
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
        if delta_row <= 1 and delta_col <= 1 and\
                (not board.get_piece(row1, col1)
                 or board.get_piece(row1, col1).color != self.color) and correct_coords(row1, col1) :
            if any(map(lambda x: x.can_attack(board, get_cell((x.rect.x, x.rect.y))[1],
                                              get_cell((x.rect.x, x.rect.y))[0],
                                              row1,
                                              col1),
                       filter(lambda x: x.color == opponent(self.color), all_pieces.sprites()))):
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


def game():
    global board
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
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
                elif 25 <= x <= 325 and 25 <= y <= 85:
                    return
        screen.fill('#404147')
        draw_game_menu(screen, board)
        all_sprites.update()
        all_sprites.draw(screen)
        winner = win_check(board)
        if winner:
            choice = draw_win_screen(winner)
            if choice == 1:
                return
            elif choice == 2:
                board = Board()
        pygame.display.flip()


if __name__ == "__main__":
    running = True
    pygame.init()
    main_menu = pygame.display.set_mode((800, 600))
    pygame.display.set_caption('Главное меню')
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and (250 <= event.pos[0] <= 550 and
                                                           225 <= event.pos[1] <= 300):
                pygame.display.quit()
                screen = pygame.display.set_mode((WIDTH, HEIGHT))
                all_sprites = pygame.sprite.Group()
                all_pieces = pygame.sprite.Group()
                cell_size = BOARD_SIZE // 8
                board = Board()
                game()
                pygame.display.quit()
                main_menu = pygame.display.set_mode((800, 600))
                pygame.display.set_caption('Главное меню')
        main_menu.fill('#404147')
        draw_main_menu(main_menu)
        pygame.display.flip()
    pygame.quit()
