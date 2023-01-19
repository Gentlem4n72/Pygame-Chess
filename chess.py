import os
import sys
from challenges import challenges
import pygame
import tkinter, tkinter.filedialog
import datetime as dt

WHITE = 1
BLACK = 2


def load_image(name, colorkey=None):
    fullname = os.path.join('figures', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    return image


def get_filename():
    top = tkinter.Tk()
    top.withdraw()
    file_name = tkinter.filedialog.askopenfilename(parent=top, initialdir='protocols')
    top.destroy()
    # if not file_name.endswith('txt'):
    #     return ''
    return file_name


def taking_on_the_pass(piece, board):
    if get_cell((piece.rect.x, piece.rect.y))[0] < 7:
        figure1 = board.field[get_cell((piece.rect.x, piece.rect.y))[1]][get_cell((piece.rect.x, piece.rect.y))[0] + 1]
        figure2 = board.field[get_cell((piece.rect.x, piece.rect.y))[1]][get_cell((piece.rect.x, piece.rect.y))[0] - 1]
        if type(piece) is Pawn:
            if type(figure1) is Pawn and figure1.color != piece.color:
                figure1.taking = (get_cell((piece.rect.x, piece.rect.y))[1] - 1 if figure1.color == WHITE else
                                  get_cell((piece.rect.x, piece.rect.y))[1] + 1,
                                  get_cell((piece.rect.x, piece.rect.y))[0])
        if type(piece) is Pawn:
            if type(figure2) is Pawn and figure2.color != piece.color:
                figure2.taking = (get_cell((piece.rect.x, piece.rect.y))[1] - 1 if figure2.color == WHITE else
                                  get_cell((piece.rect.x, piece.rect.y))[1] + 1,
                                  get_cell((piece.rect.x, piece.rect.y))[0])
    else:
        figure2 = board.field[get_cell((piece.rect.x, piece.rect.y))[1]][get_cell((piece.rect.x, piece.rect.y))[0] - 1]
        if type(piece) is Pawn:
            if type(figure2) is Pawn and figure2.color != piece.color:
                figure2.taking = (get_cell((piece.rect.x, piece.rect.y))[1] - 1 if figure2.color == WHITE else
                                  get_cell((piece.rect.x, piece.rect.y))[1] + 1,
                                  get_cell((piece.rect.x, piece.rect.y))[0])


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
        if (piece.color == WHITE and y == 0 or
                (piece.color == BLACK and y == 7)):
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
    king_moves = []
    figures = [*filter(lambda x: x.color == opponent(color), all_pieces.sprites())]
    opponent_figures = [*filter(lambda x: x.color == color, all_pieces.sprites())]
    old_figure = None
    old_cords = ()

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
    if tking:
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
                return

    if not any(king_moves) and check_figures:
        for figure in opponent_figures:
            for y in range(8):
                for x in range(8):
                    if figure.can_attack(board,
                                         get_cell((figure.rect.x, figure.rect.y))[1],
                                         get_cell((figure.rect.x, figure.rect.y))[0],
                                         x,
                                         y)\
                            or figure.can_move(board,
                                               get_cell((figure.rect.x, figure.rect.y))[1],
                                               get_cell((figure.rect.x, figure.rect.y))[0],
                                               x,
                                               y):
                        old_figure = board.field[x][y]
                        old_cords = get_cell((figure.rect.x, figure.rect.y))
                        board.field[x][y] = figure
                        if any(map(lambda z: z.can_attack(board,
                                                          get_cell((z.rect.x, z.rect.y))[1],
                                                          get_cell((z.rect.x, z.rect.y))[0],
                                                          king_x,
                                                          king_y), figures)) is False:
                            board.field[x][y] = old_figure
                            board.field[old_cords[1]][old_cords[0]] = figure
                            return
                        board.field[x][y] = old_figure
                        board.field[old_cords[1]][old_cords[0]] = figure
        return opponent(color)
    if not any(king_moves) and check_figures:
        return opponent(color)


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
    ny = (coords[1] - (HEIGHT - BOARD_SIZE - INDENT * 2)) // cell_size
    nx = (coords[0] - (WIDTH - BOARD_SIZE - INDENT * 2)) // cell_size
    return nx, ny


def get_pixels(coords):
    ny = coords[1] * cell_size + HEIGHT - BOARD_SIZE - INDENT * 2
    nx = coords[0] * cell_size + WIDTH - BOARD_SIZE - INDENT * 2
    return nx, ny


def draw_game_menu(screen, board, analysis=False, challenges=False):
    global check_alarm

    pygame.draw.rect(screen, 'black', (WIDTH - BOARD_SIZE - INDENT * 3, HEIGHT - BOARD_SIZE - INDENT * 3,
                                       BOARD_SIZE + INDENT * 2, BOARD_SIZE + INDENT * 2))
    for i in range(8):
        letter = 'ABCDEFGH'[i]
        letter = pygame.font.Font(None, round(25 * SCALE_X)).render(letter, True, 'white')
        screen.blit(letter, (WIDTH - BOARD_SIZE + 100 * SCALE_X * i - letter.get_width() // 2,
                             HEIGHT - 37 * SCALE_Y - letter.get_height() // 2))
    for i in range(8):
        number = pygame.font.Font(None, round(25 * SCALE_X)).render(str(8 - i), True, 'white')
        screen.blit(number, (WIDTH - 40 * SCALE_X - number.get_width() // 2,
                             100 * SCALE_Y + 100 * SCALE_Y * i - number.get_height() // 2))

    pygame.draw.rect(screen, 'black', (INDENT, 100 * SCALE_Y, 775 * SCALE_X, 615 * SCALE_Y), round(5 * SCALE_X))
    pygame.draw.rect(screen, 'black', (INDENT, 100 * SCALE_Y, 775 * SCALE_X, 115 * SCALE_Y), round(5 * SCALE_X))
    color = board.color
    num = len(board.protocol) if len(board.protocol) < 5 else 5
    for i in range(num):
        color = opponent(color)
        if i == num - 1:
            pygame.draw.rect(screen, '#61626b', (INDENT, 210 * SCALE_Y + 100 * SCALE_Y * i,
                                                 775 * SCALE_X, 105 * SCALE_Y))
        pygame.draw.rect(screen, 'black', (INDENT, 210 * SCALE_Y + 100 * SCALE_Y * i,
                                           775 * SCALE_X, 105 * SCALE_Y), round(5 * SCALE_X))
        text = ' -> '.join(board.protocol[-5:][i])
        text = pygame.font.Font(None, 50).render(text, True, 'white')
        screen.blit(text, (425 * SCALE_X - text.get_width() // 2,
                           215 * SCALE_Y + 100 * SCALE_Y * i + 52 * SCALE_Y - text.get_height() // 2))

    pygame.draw.rect(screen, 'black', (INDENT, INDENT, 300 * SCALE_X, 60 * SCALE_Y), round(5 * SCALE_X))
    return_text = pygame.font.Font(None, round(40 * SCALE_X)).render('<- На главное меню', True, 'white')
    screen.blit(return_text, (175 * SCALE_X - return_text.get_width() // 2,
                              55 * SCALE_Y - return_text.get_height() // 2))

    if not analysis:
        pygame.draw.rect(screen, 'black', (150 * SCALE_X, 750 * SCALE_Y, 525 * SCALE_X, 125 * SCALE_Y), round(5 * SCALE_X))
        pygame.draw.rect(screen, '#660000', (155 * SCALE_X, 755 * SCALE_Y, 515 * SCALE_X, 115 * SCALE_Y))
        surr_text = pygame.font.Font(None, round(50 * SCALE_X)).render('Сдаться', True, 'white')
        screen.blit(surr_text, (413 * SCALE_X - surr_text.get_width() // 2,
                                813 * SCALE_Y - surr_text.get_height() // 2))
    else:
        pygame.draw.rect(screen, 'black', (180 * SCALE_X, 775 * SCALE_Y, 150 * SCALE_X, 60 * SCALE_Y),
                         round(5 * SCALE_X))
        pygame.draw.rect(screen, 'black', (450 * SCALE_X, 775 * SCALE_Y, 150 * SCALE_X, 60 * SCALE_Y),
                         round(5 * SCALE_Y))
        pygame.draw.lines(screen, 'black', True, ((100 * SCALE_X, 805 * SCALE_Y), (180 * SCALE_X, 750 * SCALE_Y),
                                                  (180 * SCALE_X, 855 * SCALE_Y)),
                          round(5 * SCALE_X))
        pygame.draw.rect(screen, '#404147', (175 * SCALE_X, 780 * SCALE_Y, 30 * SCALE_X, 50 * SCALE_Y))
        pygame.draw.lines(screen, 'black', True, ((680 * SCALE_X, 805 * SCALE_Y), (599 * SCALE_X, 750 * SCALE_Y),
                                                  (599 * SCALE_X, 855 * SCALE_Y)), round(5 * SCALE_X))
        pygame.draw.rect(screen, '#404147', (595 * SCALE_X, 780 * SCALE_Y, 30 * SCALE_X, 50 * SCALE_Y))

    turn = pygame.font.Font(None, round(50 * SCALE_X)).render('Ход ' + ('белых' if board.color == WHITE else 'чёрных'),
                                                              True, 'white')
    screen.blit(turn, (150 * SCALE_X - turn.get_width() // 2, 155 * SCALE_Y - turn.get_height() // 2))

    checks = check(board)
    if checks[0]:
        check_text = pygame.font.Font(None, round(50 * SCALE_X)).render('Шах белым', True, 'white')
        screen.blit(check_text, (660 * SCALE_X - check_text.get_width() // 2,
                                 130 * SCALE_Y - check_text.get_height() // 2))
    if checks[1]:
        check_text = pygame.font.Font(None, round(50 * SCALE_X)).render('Шах чёрным', True, 'white')
        screen.blit(check_text, (660 * SCALE_X - check_text.get_width() // 2,
                                 180 * SCALE_Y - check_text.get_height() // 2))

    if not check_alarm and (checks[0] or checks[1]):
        check_sound.play()
        check_alarm = True
    if check_alarm and not(checks[0] or checks[1]):
        check_alarm = False


def draw_win_screen(winner):
    v = 350
    fps = 60
    clock = pygame.time.Clock()
    y = -500 * SCALE_Y
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if y < 150 * SCALE_Y:
                    y = 150 * SCALE_Y
                else:
                    mx, my = event.pos
                    if 375 * SCALE_X <= mx <= 675 * SCALE_X and 550 * SCALE_Y <= my <= 625 * SCALE_Y:
                        return 1
                    elif 725 * SCALE_X <= mx <= 1025 * SCALE_X and 550 * SCALE_Y <= my <= 625 * SCALE_Y:
                        return 2
                    elif 1075 * SCALE_X <= mx <= 1375 * SCALE_X and 550 * SCALE_Y <= my <= 625 * SCALE_Y:
                        return 3
        if y >= 150 * SCALE_Y:
            y = 150 * SCALE_Y
        else:
            y += v / fps
        clock.tick(fps)
        screen.fill('#404147')
        draw_game_menu(screen, board)
        all_sprites.update()
        all_sprites.draw(screen)
        pygame.draw.rect(screen, '#404147', (300 * SCALE_X, y, 1150 * SCALE_X, 600 * SCALE_Y))
        pygame.draw.rect(screen, 'black', (300 * SCALE_X, y, 1150 * SCALE_X, 600 * SCALE_Y), round(5 * SCALE_X))
        for _ in range(3):
            text = ['На главное меню', 'Реванш', 'Анализ партии'][_]
            pygame.draw.rect(screen, 'black', (375 * SCALE_X + 350 * SCALE_X * _, y + 400 * SCALE_Y,
                                               300 * SCALE_X, 75 * SCALE_Y), 5)
            text = pygame.font.Font(None, round(45 * SCALE_Y)).render(text, True, 'white')
            screen.blit(text, (525 * SCALE_X + 350 * SCALE_X * _ - text.get_width() // 2,
                               y + 435 * SCALE_Y - text.get_height() // 2))
        text = pygame.font.Font(None, round(70 * SCALE_Y)).render('Победа ' + ('белых.' if winner == WHITE
                                                                               else 'чёрных.'), True, 'white')
        screen.blit(text, (875 * SCALE_X - text.get_width() // 2, y + 150 * SCALE_Y - text.get_height() // 2))
        pygame.display.flip()


def draw_main_menu(main_menu):
    text = pygame.font.Font(None, round(100 * SCALE_X)).render('Шах и Мат', True, 'white')
    main_menu.blit(text, (400 * SCALE_X - text.get_width() // 2, 150 * SCALE_Y - text.get_height() // 2))
    for _ in range(3):
        text = ['Играть', 'Анализ партии', 'Испытания'][_]
        pygame.draw.rect(main_menu, 'black', (250 * SCALE_X, (225 + 95 * _) * SCALE_Y,
                                              300 * SCALE_X, 75 * SCALE_Y), round(5 * SCALE_X))
        btn_text = pygame.font.Font(None, round(45 * SCALE_X)).render(text, True, 'white')
        main_menu.blit(btn_text, (400 * SCALE_X - btn_text.get_width() // 2,
                                  260 * SCALE_Y + 95 * SCALE_Y * _ - btn_text.get_height() // 2))

    image = pygame.transform.scale(load_image('note/img.png'), (40 * SCALE_X, 40 * SCALE_Y))
    main_menu.blit(image, (15 * SCALE_X, 545 * SCALE_Y,
                           40 * SCALE_X, 40 * SCALE_Y))
    pygame.draw.rect(main_menu, 'black', (10 * SCALE_X, 540 * SCALE_Y,
                                          50 * SCALE_X, 50 * SCALE_Y), round(5 * SCALE_X))
    if not volume:
        pygame.draw.line(main_menu, 'black', (13 * SCALE_X, 543 * SCALE_Y), (57 * SCALE_X, 587 * SCALE_Y), 5)


def draw_possible_moves(board, row, col):
    for i in range(8):
        for j in range(8):
            piece = board.field[row][col]
            if (piece.can_attack(board, *[*get_cell((piece.rect.x + 1, piece.rect.y + 1))][::-1], i, j) and
                    board.field[i][j]):
                if board.field[i][j].color == opponent(piece.color):
                    pygame.draw.rect(screen, 'red', (*get_pixels((j, i)), cell_size, cell_size), round(5 * SCALE_X))
            elif piece.can_move(board, *[*get_cell((piece.rect.x + 1, piece.rect.y + 1))][::-1], i, j):
                pygame.draw.circle(screen, 'green',
                                   tuple(map(lambda z: z + cell_size // 2, get_pixels((j, i)))), round(10 * SCALE_X))
    pygame.draw.rect(screen, 'green', (*get_pixels((col, row)), cell_size, cell_size), round(5 * SCALE_X))
    pygame.display.flip()


def draw_selection_dialog():
    while True:
        pygame.draw.rect(screen, '#404147', (cell_size + board.indent_h, cell_size * 3 + board.indent_v,
                                             cell_size * 6, cell_size * 2))
        text = pygame.font.Font(None, round(50 * SCALE_X)).render('Выберите фигуру', True, 'white')
        screen.blit(text, (cell_size + board.indent_h + cell_size * 3 - text.get_width() // 2,
                           cell_size * 3.25 + board.indent_v - text.get_height() // 2))
        x, y = cell_size + board.indent_h + 25 * SCALE_X, cell_size * 3 + board.indent_v + 60 * SCALE_Y
        for i in range(4):
            piece = ['rook', 'knight', 'bishop', 'queen'][i]
            screen.blit(pygame.transform.scale(load_image(f'W{piece}.png' if board.color == BLACK else f'b{piece}.png'),
                                               (cell_size, cell_size)), (x + 150 * SCALE_X * i, y))
            pygame.draw.rect(screen, 'white',
                             (x + 150 * SCALE_X * i, y, cell_size, cell_size), round(5 * SCALE_X))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if x <= event.pos[0] <= x + 100 * SCALE_X and y <= event.pos[1] <= y + cell_size:
                    click.play()
                    return Rook
                elif x + 150 * SCALE_X <= event.pos[0] <= x + 250 * SCALE_X and y <= event.pos[1] <= y + cell_size:
                    click.play()
                    return Knight
                elif x + 300 * SCALE_X <= event.pos[0] <= x + 400 * SCALE_X and y <= event.pos[1] <= y + cell_size:
                    click.play()
                    return Bishop
                elif x + 450 * SCALE_X <= event.pos[0] <= x + 550 * SCALE_X and y <= event.pos[1] <= y + cell_size:
                    click.play()
                    return Queen


def surrender(winner):
    v = 350
    fps = 60
    clock = pygame.time.Clock()
    y = -500 * SCALE_Y
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if y < 150 * SCALE_Y:
                    y = 150 * SCALE_Y
                else:
                    mx, my = event.pos
                    if 375 * SCALE_X <= mx <= 675 * SCALE_X and 550 * SCALE_Y <= my <= 625 * SCALE_Y:
                        return 1
                    elif 725 * SCALE_X <= mx <= 1025 * SCALE_X and 550 * SCALE_Y <= my <= 625 * SCALE_Y:
                        return 2
                    elif 1075 * SCALE_X <= mx <= 1375 * SCALE_X and 550 * SCALE_Y <= my <= 625 * SCALE_Y:
                        return 3
        if y >= 150 * SCALE_Y:
            y = 150 * SCALE_Y
        else:
            y += v / fps
        clock.tick(fps)
        screen.fill('#404147')
        draw_game_menu(screen, board)
        all_sprites.update()
        all_sprites.draw(screen)
        pygame.draw.rect(screen, '#404147', (300 * SCALE_X, y, 1150 * SCALE_X, 600 * SCALE_Y))
        pygame.draw.rect(screen, 'black', (300 * SCALE_X, y, 1150 * SCALE_X, 600 * SCALE_Y), round(5 * SCALE_X))
        for _ in range(3):
            text = ['На главное меню', 'Реванш', 'Анализ партии'][_]
            pygame.draw.rect(screen, 'black', (375 * SCALE_X + 350 * SCALE_X * _, y + 400 * SCALE_Y,
                                               300 * SCALE_X, 75 * SCALE_Y), 5)
            text = pygame.font.Font(None, round(45 * SCALE_Y)).render(text, True, 'white')
            screen.blit(text, (525 * SCALE_X + 350 * SCALE_X * _ - text.get_width() // 2,
                               y + 435 * SCALE_Y - text.get_height() // 2))
        text = pygame.font.Font(None, round(70 * SCALE_Y)).render(('Черные' if winner == WHITE else 'Белые') +
                                                                  ' сдались. ' + 'Победа ' + ('белых.' if winner == WHITE
                                                                               else 'чёрных.'), True, 'white')
        screen.blit(text, (875 * SCALE_X - text.get_width() // 2, y + 150 * SCALE_Y - text.get_height() // 2))
        pygame.display.flip()


class Board(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(all_sprites)
        self.color = WHITE
        self.protocol = []
        self.field = []
        self.checks = [0, 0]
        self.indent_h = WIDTH - BOARD_SIZE - INDENT * 2
        self.indent_v = HEIGHT - BOARD_SIZE - INDENT * 2
        for row in range(8):
            self.field.append([None] * 8)
        self.field[0] = [
            Rook(BLACK, self.indent_h, self.indent_v),
            Knight(BLACK, self.indent_h + cell_size, self.indent_v),
            Bishop(BLACK, self.indent_h + cell_size * 2, self.indent_v),
            Queen(BLACK, self.indent_h + cell_size * 3, self.indent_v),
            King(BLACK, self.indent_h + cell_size * 4, self.indent_v),
            Bishop(BLACK, self.indent_h + cell_size * 5, self.indent_v),
            Knight(BLACK, self.indent_h + cell_size * 6, self.indent_v),
            Rook(BLACK, self.indent_h + cell_size * 7, self.indent_v)
        ]
        self.field[1] = [Pawn(BLACK, self.indent_h + cell_size * i, self.indent_v + cell_size) for i in range(8)]

        self.field[6] = [Pawn(WHITE, self.indent_h + cell_size * i, self.indent_v + cell_size * 6) for i in range(8)]

        self.field[7] = [
            Rook(WHITE, self.indent_h, self.indent_v + cell_size * 7),
            Knight(WHITE, self.indent_h + cell_size, self.indent_v + cell_size * 7),
            Bishop(WHITE, self.indent_h + cell_size * 2, self.indent_v + cell_size * 7),
            Queen(WHITE, self.indent_h + cell_size * 3, self.indent_v + cell_size * 7),
            King(WHITE, self.indent_h + cell_size * 4, self.indent_v + cell_size * 7),
            Bishop(WHITE, self.indent_h + cell_size * 5, self.indent_v + cell_size * 7),
            Knight(WHITE, self.indent_h + cell_size * 6, self.indent_v + cell_size * 7),
            Rook(WHITE, self.indent_h + cell_size * 7, self.indent_v + cell_size * 7)
        ]
        self.image = pygame.Surface((BOARD_SIZE, BOARD_SIZE))
        self.rect = pygame.Rect(WIDTH - BOARD_SIZE - INDENT * 2, HEIGHT - BOARD_SIZE - INDENT * 2,
                                WIDTH - INDENT, HEIGHT - INDENT)
        self.image.fill('#b58763')
        for i in range(0, BOARD_SIZE, cell_size):
            for j in range(0 if i % (cell_size * 2) == 0 else cell_size, BOARD_SIZE, cell_size * 2):
                pygame.draw.rect(self.image, '#f0dab5', (j, i, cell_size, cell_size))

    def current_player_color(self):
        return self.color

    def get_piece(self, row, col):
        if correct_coords(row, col):
            return self.field[row][col]
        else:
            return None

    def move_piece(self, col, row, row1=None, col1=None, protocol=None):
        if row1 is None and col1 is None:
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        if protocol is not None:
                            protocol.close()
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
                                  self.field[row][col].turn == 0 and
                                  self.field[row1][col1].turn == 0):
                                step = -1 if col >= col1 else 1
                                if castling(self.field, row, col, col1, step):
                                    rook = self.field[row1][col1]
                                    if step == -1:
                                        self.field[row][col] = None
                                        self.field[row][col - 2] = piece
                                        self.field[row1][col1] = None
                                        self.field[row1][col1 + 3] = rook
                                        piece.rect.x, piece.rect.y = get_pixels((col - 2, row))
                                        rook.rect.x, piece.rect.y = get_pixels((col1 + 3, row1))
                                    elif step == 1:
                                        self.field[row][col] = None
                                        self.field[row][col + 2] = piece
                                        self.field[row1][col1] = None
                                        self.field[row1][col1 - 2] = rook
                                        piece.rect.x, piece.rect.y = get_pixels((col + 2, row))
                                        rook.rect.x, piece.rect.y = get_pixels((col1 - 2, row1))
                                    figure.play()
                                    self.color = opponent(self.color)
                                    piece.turn += 1
                                    check(self)
                                    return True
                                else:
                                    return False
                            else:
                                return False
                        figure.play()

                        self.protocol.append(('ABCDEFGH'[col] + str(8 - row), 'ABCDEFGH'[col1] + str(8 - row1)))
                        if protocol is not None:
                            protocol.write(f'{col} {row} {col1} {row1}\n')

                        self.field[row][col] = None  # Снять фигуру.
                        self.field[row1][col1] = piece  # Поставить на новое место.
                        piece.rect.x, piece.rect.y = get_pixels((col1, row1))
                        if type(piece) is Pawn and piece.taking:
                            piece.taking = (None, None)
                        if abs(row1 - row) == 2:
                            taking_on_the_pass(piece, board)
                        self.color = opponent(self.color)
                        if piece.char() == 'K' or piece.char() == 'R':
                            piece.turn += 1
                        checks = check(self)
                        if checks[0]:
                            self.checks[0] += 1
                        else:
                            self.checks[0] = 0
                        if checks[1]:
                            self.checks[1] += 1
                        else:
                            self.checks[1] = 0
                        print(self.checks)
                        pawn_conversion(board)
                        return True
                draw_possible_moves(board, row, col)
        else:
            self.protocol.append(('ABCDEFGH'[col] + str(8 - row), 'ABCDEFGH'[col1] + str(8 - row1)))
            piece = self.field[row][col]
            self.field[row][col] = None  # Снять фигуру.
            self.field[row1][col1] = piece  # Поставить на новое место.
            piece.rect.x, piece.rect.y = get_pixels((col1, row1))
            self.color = opponent(self.color)
            if piece.char() == 'P':
                if piece.pass_eating[0]:
                    all_sprites.remove(
                        board.field[
                            piece.pass_eating[1] - 1 if self.color == WHITE else piece.pass_eating[1] + 1][
                            piece.pass_eating[2]])
                    board.field[
                        piece.pass_eating[1] - 1 if self.color == WHITE else piece.pass_eating[1] + 1][
                        piece.pass_eating[2]] = None
                    piece.pass_eating = [False, 0, 0]
            if piece.char() == 'K' or piece.char() == 'R':
                piece.turn += 1
            check(self)
            pawn_conversion(board)
            checkmate(self.color, self)
            return True


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
        self.turn = 0

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
        self.taking = (None, None)
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
        if self.taking[1] == col1 and self.taking[0] == row1:
            return True

        if col != col1:
            return False

        if self.color == BLACK:
            direction = 1
            start_row = 1
        else:
            direction = -1
            start_row = 6

        if row + direction == row1 and board.field[row1][col] is None:
            return True

        if abs(row1 - row) == 2:
            self.taking_on_the_pass(board, row1, col1, row)

        if (row == start_row
                and row + 2 * direction == row1
                and board.field[row + direction][col] is None
                and board.field[row1][col] is None):
            return True

        return False

    def can_attack(self, board, row, col, row1, col1):

        if row1 == row and col1 == col:
            return False

        direction = 1 if (self.color == BLACK) else -1

        if board.field[row1][col1]:
            if board.field[row1][col1] != self.color:
                return (row + direction == row1
                        and (col + 1 == col1 or col - 1 == col1))
        return False

    def taking_on_the_pass(self, board, row1, col1, row):
        if col1 < 7:
            figure1 = board.field[row1][col1 + 1]
            figure2 = board.field[row1][col1 - 1]
            if type(figure1) is Pawn:
                if figure1.color == opponent(self.color):
                    figure1.pass_eating = [True, row1 - 1 if row == 1 else row1 + 1, col1, self]
            if type(figure2) is Pawn:
                if figure2.color == opponent(self.color):
                    figure2.pass_eating = [True, row1 - 1 if row == 1 else row1 + 1, col1, self]
        else:
            figure2 = board.field[row1][col1 - 1]
            if type(figure2) is Pawn:
                if figure2.color == opponent(self.color):
                    figure2.pass_eating = [True, row1 - 1 if row == 1 else row1 + 1, col1, self]


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
        if delta_row <= 1 and delta_col <= 1 and \
                (not board.get_piece(row1, col1)
                 or board.get_piece(row1, col1).color != self.color) and correct_coords(row1, col1):
            if any(map(lambda x: x.can_attack(board, get_cell((x.rect.x, x.rect.y))[1],
                                              get_cell((x.rect.x, x.rect.y))[0],
                                              row1,
                                              col1),
                       filter(lambda x: x.color == opponent(self.color), all_pieces.sprites()))
                   ):
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


class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, frames, x, y):
        super().__init__(animated_sprite)
        self.frames = []
        self.create_frames(frames)
        self.cur_frame = 0
        self.image = pygame.transform.scale(self.frames[self.cur_frame], (100 * SCALE_X, 100 * SCALE_Y))
        self.rect = self.rect.move(x * SCALE_X, y * SCALE_Y)

    def create_frames(self, frames):
        self.rect = pygame.Rect(0, -10 * SCALE_Y, 100 * SCALE_X, 100 * SCALE_Y)
        for i in range(frames):
            self.frames.append(load_image(f'knight/{str(i)}.png'))

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = pygame.transform.scale(self.frames[self.cur_frame], (100 * SCALE_X, 100 * SCALE_Y))


def game():
    global board, check_alarm, all_sprites, all_pieces
    protocol = open(f'protocols/{dt.datetime.now().strftime("%d-%m-%Y %H-%M-%S")}.txt', mode='w+')
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
                        figure.play()
                        board.move_piece(x, y, protocol=protocol)
                elif 25 * SCALE_X <= x <= 325 * SCALE_X and 25 * SCALE_Y <= y <= 85 * SCALE_Y:
                    click.play()
                    return
                elif 150 * SCALE_X <= x <= 675 * SCALE_X and 750 * SCALE_Y <= y <= 875 * SCALE_Y:
                    gameover.play()
                    choice = surrender(opponent(board.color))
                    if choice == 1:
                        click.play()
                        return
                    elif choice == 2:
                        click.play()
                        all_sprites.empty()
                        all_pieces.empty()
                        board = Board()
                        check_alarm = False
        screen.fill('#404147')
        draw_game_menu(screen, board)
        all_sprites.update()
        all_sprites.draw(screen)
        winner = checkmate(board.color, board)
        if board.checks[1] > 1:
            winner = WHITE
        elif board.checks[0] > 1:
            winner = BLACK
        if winner:
            gameover.play()
            choice = draw_win_screen(winner)
            if choice == 1:
                click.play()
                return
            elif choice == 2:
                click.play()
                all_sprites.empty()
                all_pieces.empty()
                board = Board()
                check_alarm = False
        pygame.display.flip()


def analysis():
    global board, check_alarm
    arrow = []
    arrows = []
    borders = []
    circles = []
    filename = ''
    protocol = None
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if protocol is not None:
                    protocol.close()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if (board.indent_h <= x <= board.indent_h + BOARD_SIZE and
                        board.indent_v <= y <= board.indent_v + BOARD_SIZE):
                    x, y = get_cell((x, y))

                    if event.button == 3:  # пкм
                        if not arrow:
                            arrow = [x, y]
                            borders += [get_pixels((x, y))]
                        elif len(arrow) == 2:
                            arrow = list(map(lambda z: z + cell_size // 2, get_pixels((arrow[0], arrow[1])))) + \
                                    list(map(lambda z: z + cell_size // 2, get_pixels((x, y))))
                            arrows.append(arrow)
                            arrow = []
                            borders += [get_pixels((x, y))]

                    if event.button == 1:  # лкм
                        if (x, y) not in circles:
                            circles.append((x, y))
                        else:
                            circles.remove((x, y))

                    if event.button == 2:  # колёсико мыши
                        circles = []
                        arrows = []
                        arrow = []
                        borders = []

                elif 25 * SCALE_X <= x <= 325 * SCALE_X and 25 * SCALE_Y <= y <= 85 * SCALE_Y:
                    click.play()
                    if protocol is not None:
                        protocol.close()
                    return
                elif ((100 * SCALE_X <= x <= 180 * SCALE_X and 750 * SCALE_Y <= y <= 855 * SCALE_Y) or
                      (100 * SCALE_X <= x <= 330 * SCALE_X and 775 * SCALE_X <= y <= 835 * SCALE_Y)):
                    if current_turn != -1:
                        col1, row1, col, row = turns[current_turn]
                        board.move_piece(col, row, row1=row1, col1=col1)
                        figure.play()
                        del board.protocol[-1]
                        del board.protocol[-1]
                        current_turn -= 1
                        circles = []
                        arrows = []
                        arrow = []
                        borders = []
                elif ((600 * SCALE_X <= x <= 680 and 750 * SCALE_Y <= y <= 855 * SCALE_Y) or
                      (450 * SCALE_X <= x <= 680 and 775 * SCALE_Y <= y <= 835 * SCALE_Y)):
                    if current_turn + 1 <= len(turns) - 1:
                        current_turn += 1
                        col, row, col1, row1 = turns[current_turn]
                        board.move_piece(col, row, row1=row1, col1=col1)
                        figure.play()
                        circles = []
                        arrows = []
                        arrow = []
                        borders = []

        screen.fill('#404147')
        draw_game_menu(screen, board, analysis=True)
        all_sprites.update()
        all_sprites.draw(screen)

        for elem in borders:
            pygame.draw.rect(screen, 'orange', (elem[0], elem[1], cell_size, cell_size), round(5 * SCALE_X))
        for elem in arrows:
            if len(elem) == 4:
                pygame.draw.line(screen, 'orange', (elem[0], elem[1]), (elem[2], elem[3]), round(5 * SCALE_X))
        for elem in circles:
            pygame.draw.circle(screen, 'green',
                               tuple(map(lambda z: z + cell_size // 2, get_pixels((elem[0], elem[1])))),
                               cell_size // 2, round(5 * SCALE_X))

        winner = checkmate(board.color, board)
        if winner:
            gameover.play()
            choice = draw_win_screen(winner)
            if choice == 1:
                click.play()
                if protocol is not None:
                    protocol.close()
                return
            elif choice == 2:
                click.play()
                all_sprites.empty()
                all_pieces.empty()
                board = Board()
                check_alarm = False
        pygame.display.flip()

        if not filename:
            filename = get_filename()
            protocol = open(filename, mode='r')
            turns = [tuple(map(int, x.rstrip().split())) for x in protocol.readlines()]
            current_turn = -1

        else:
            protocol = open(filename, mode='r')


if __name__ == "__main__":
    running = True
    pygame.mixer.pre_init(44100, -16, 1, 512)
    pygame.init()
    w, h = pygame.display.Info().current_w, pygame.display.Info().current_h
    SCALE_X, SCALE_Y = float(w) / 1920, float(h) / 1080
    WIDTH = int(1700 * SCALE_X)
    HEIGHT = int(900 * SCALE_Y)
    cell_size = int(100 * SCALE_X)
    BOARD_SIZE = cell_size * 8
    INDENT = int(25 * SCALE_X)
    main_menu = pygame.display.set_mode((800 * SCALE_X, 600 * SCALE_Y))
    pygame.display.set_caption('Главное меню')

    intro = pygame.mixer.Sound('sounds/intro.wav')
    click = pygame.mixer.Sound('sounds/click.wav')
    check_sound = pygame.mixer.Sound('sounds/check.wav')
    figure = pygame.mixer.Sound('sounds/figure.wav')
    gameover = pygame.mixer.Sound('sounds/gameover.wav')
    sounds = [intro, click, check_sound, figure, gameover]
    intro.play()
    volume = 1

    animated_sprite = pygame.sprite.Group()
    knight = AnimatedSprite(9, 100, 100)
    fps = 6
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and (250 * SCALE_X <= event.pos[0] <= 550 * SCALE_X and
                                                           225 * SCALE_Y <= event.pos[1] <= 300 * SCALE_Y):
                click.play()
                check_alarm = False

                pygame.display.quit()
                screen = pygame.display.set_mode((WIDTH, HEIGHT))
                pygame.display.set_caption('Играть')
                all_sprites = pygame.sprite.Group()
                all_pieces = pygame.sprite.Group()
                board = Board()
                game()
                pygame.display.quit()
                main_menu = pygame.display.set_mode((800 * SCALE_X, 600 * SCALE_Y))
                pygame.display.set_caption('Главное меню')
            elif event.type == pygame.MOUSEBUTTONDOWN and (250 * SCALE_X <= event.pos[0] <= 550 * SCALE_X and
                                                           320 * SCALE_Y <= event.pos[1] <= 395 * SCALE_Y):
                click.play()
                check_alarm = False

                pygame.display.quit()
                screen = pygame.display.set_mode((WIDTH, HEIGHT))
                pygame.display.set_caption('Анализ партии')
                all_sprites = pygame.sprite.Group()
                all_pieces = pygame.sprite.Group()
                board = Board()
                analysis()
                pygame.display.quit()
                main_menu = pygame.display.set_mode((800 * SCALE_X, 600 * SCALE_Y))
                pygame.display.set_caption('Главное меню')
            elif event.type == pygame.MOUSEBUTTONDOWN and (250 * SCALE_X <= event.pos[0] <= 550 * SCALE_X and
                                                           405 * SCALE_Y <= event.pos[1] <= 480 * SCALE_Y):
                click.play()
                check_alarm = False

                pygame.display.quit()
                screen = pygame.display.set_mode((WIDTH, HEIGHT))
                challenges(screen)
                pygame.display.quit()
                main_menu = pygame.display.set_mode((800 * SCALE_X, 600 * SCALE_Y))
                pygame.display.set_caption('Главное меню')
            elif event.type == pygame.MOUSEBUTTONDOWN and (10 * SCALE_X <= event.pos[0] <= 60 * SCALE_X and
                                                           540 * SCALE_Y <= event.pos[1] <= 590 * SCALE_Y):
                volume = 0 if volume else 1
                for sound in sounds:
                    sound.set_volume(volume)
        main_menu.fill('#404147')
        draw_main_menu(main_menu)
        animated_sprite.update()
        animated_sprite.draw(main_menu)
        pygame.display.flip()
        clock.tick(fps)
    pygame.quit()
