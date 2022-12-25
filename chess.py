import os
import sys
import pygame

WHITE = 1
BLACK = 2
WIDTH = 800
HEIGHT = 800


def load_image(name, colorkey=None):
    fullname = os.path.join('figures', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    return image


def opponent(color):
    if color == WHITE:
        return BLACK
    else:
        return WHITE


def main():
    # Создаём шахматную доску
    board = Board()
    # Цикл ввода команд игроков
    while True:
        # Выводим положение фигур на доске
        # Выводим приглашение игроку нужного цвета
        if board.current_player_color() == WHITE:
            print('Ход белых:')
        else:
            print('Ход чёрных:')
        command = input()
        if command == 'exit':
            break
        move_type, row, col, row1, col1 = command.split()
        row, col, row1, col1 = int(row), int(col), int(row1), int(col1)
        if board.move_piece(row, col, row1, col1):
            print('Ход успешен')
        else:
            print('Координаты некорректы! Попробуйте другой ход!')


def correct_coords(row, col):
    '''Функция проверяет, что координаты (row, col) лежат
    внутри доски'''
    return 0 <= row < 8 and 0 <= col < 8

def get_cell(coords):
    ny = coords[1] // cell_size
    nx = coords[0] // cell_size
    return nx, ny

def get_pixels(coords):
    ny = coords[1] * cell_size
    nx = coords[0] * cell_size
    return nx, ny


class Board(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(all_sprites)
        self.color = WHITE
        self.field = []
        for row in range(8):
            self.field.append([None] * 8)
        self.field[0] = [
            Rook(WHITE, 0, 0), Knight(WHITE, cell_size, 0),
            Bishop(WHITE, cell_size * 2, 0), Queen(WHITE, cell_size * 3, 0),
            King(WHITE, cell_size * 4, 0), Bishop(WHITE, cell_size * 5, 0),
            Knight(WHITE, cell_size * 6, 0), Rook(WHITE, cell_size * 7, 0)
        ]
        self.field[1] = [
            Pawn(WHITE, 0, cell_size), Pawn(WHITE, cell_size, cell_size),
            Pawn(WHITE, cell_size * 2, cell_size), Pawn(WHITE, cell_size * 3, cell_size),
            Pawn(WHITE, cell_size * 4, cell_size), Pawn(WHITE, cell_size * 5, cell_size),
            Pawn(WHITE, cell_size * 6, cell_size), Pawn(WHITE, cell_size * 7, cell_size)
        ]
        self.field[6] = [
            Pawn(BLACK, 0, cell_size * 6), Pawn(BLACK, cell_size, cell_size * 6),
            Pawn(BLACK, cell_size * 2, cell_size * 6), Pawn(BLACK, cell_size * 3, cell_size * 6),
            Pawn(BLACK, cell_size * 4, cell_size * 6), Pawn(BLACK, cell_size * 5, cell_size * 6),
            Pawn(BLACK, cell_size * 6, cell_size * 6), Pawn(BLACK, cell_size * 7, cell_size * 6)
        ]
        self.field[7] = [
            Rook(BLACK, 0, cell_size * 7), Knight(BLACK, cell_size, cell_size * 7),
            Bishop(BLACK, cell_size * 2, cell_size * 7), Queen(BLACK, cell_size * 3, cell_size * 7),
            King(BLACK, cell_size * 4, cell_size * 7), Bishop(BLACK, cell_size * 5, cell_size * 7),
            Knight(BLACK, cell_size * 6, cell_size * 7), Rook(BLACK, cell_size * 7, cell_size * 7)
        ]
        self.image = pygame.Surface((WIDTH, HEIGHT))
        self.rect = pygame.Rect(0, 0, WIDTH, HEIGHT)
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
                if event.type == pygame.MOUSEBUTTONDOWN:
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
                        else:
                            return False
                    self.field[row][col] = None  # Снять фигуру.
                    self.field[row1][col1] = piece  # Поставить на новое место.
                    piece.rect.x, piece.rect.y = get_pixels((col1, row1))
                    self.color = opponent(self.color)
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

    def get_color(self):
        return self.color

    def char(self):
        return 'R'

    def can_move(self, board, row, col, row1, col1):
        # Невозможно сделать ход в клетку, которая не лежит в том же ряду
        # или столбце клеток.
        if row != row1 and col != col1:
            return False

        step = 1 if (row1 >= row) else -1
        for r in range(row + step, row1, step):
            # Если на пути по горизонтали есть фигура
            if not (board.get_piece(r, col) is None):
                return False

        step = 1 if (col1 >= col) else -1
        for c in range(col + step, col1, step):
            # Если на пути по вертикали есть фигура
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
        # Пешка может ходить только по вертикали
        # "взятие на проходе" не реализовано
        if col != col1:
            return False

        # Пешка может сделать из начального положения ход на 2 клетки
        # вперёд, поэтому поместим индекс начального ряда в start_row.
        if self.color == WHITE:
            direction = 1
            start_row = 1
        else:
            direction = -1
            start_row = 6

        # ход на 1 клетку
        if row + direction == row1:
            return True

        # ход на 2 клетки из начального положения
        if (row == start_row
                and row + 2 * direction == row1
                and board.field[row + direction][col] is None):
            return True

        return False

    def can_attack(self, board, row, col, row1, col1):
        direction = 1 if (self.color == WHITE) else -1
        return (row + direction == row1
                and (col + 1 == col1 or col - 1 == col1))

    def can_attack(self, board, row, col, row1, col1):
        return self.can_move(board, row, col, row1, col1)


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

    def get_color(self):
        return self.color

    def char(self):
        return 'K'

    def can_move(self, board, row, col, row1, col1):
        delta_row = abs(row - row1)
        delta_col = abs(col - col1)
        if delta_row <= 1 and delta_col <= 1:
            return True
        return False

    def can_attack(self, board, row, col, row1, col1):
        return self.can_move(self, board, row, col, row1, col1)

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
            for i in range(row + step, row1, step):
                if not (board.get_piece(row + i, col + i) is None):
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
        self.image = pygame.transform.scale(self.image, (100, 100))
        self.rect = self.image.get_rect().move(x, y)
        self.rect.x, self.rect.y = x, y

    def get_color(self):
        return self.color

    def char(self):
        return 'B'

    def can_move(self, board, row, col, row1, col1):
        delta_row = abs(row1 - row)
        delta_col = abs(col1 - col)

        if delta_row != delta_col:
            return False

        step = 1 if (row1 >= row) else -1
        for i in range(row + step, row1, step):
            if not (board.get_piece(row + i, col + i) is None):
                return False

    def can_attack(self, board, row, col, row1, col1):
        return self.can_move(board, row, col, row1, col1)


if __name__ == "__main__":
    running = True
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    all_sprites = pygame.sprite.Group()
    all_pieces = pygame.sprite.Group()
    flag = False
    cell_size = WIDTH // 8
    board = Board()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = get_cell(event.pos)
                if (not (board.field[y][x] is None) and
                        board.color == board.field[y][x].get_color()):
                    board.move_piece(x, y)
        all_sprites.update()
        all_sprites.draw(screen)
        pygame.display.flip()
    pygame.quit()
