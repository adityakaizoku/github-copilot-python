import copy
import random

SIZE = 9
EMPTY = 0

def deep_copy(board):
    return copy.deepcopy(board)

def create_empty_board():
    return [[EMPTY for _ in range(SIZE)] for _ in range(SIZE)]

def is_safe(board, row, col, num):
    # Check row and column
    for x in range(SIZE):
        if board[row][x] == num or board[x][col] == num:
            return False
    # Check 3x3 box
    start_row = row - row % 3
    start_col = col - col % 3
    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num:
                return False
    return True


def is_valid_move(board, row, col, num):
    if num == EMPTY:
        return True

    for x in range(SIZE):
        if x != col and board[row][x] == num:
            return False

    for x in range(SIZE):
        if x != row and board[x][col] == num:
            return False

    start_row = row - row % 3
    start_col = col - col % 3
    for i in range(3):
        for j in range(3):
            if (start_row + i != row or start_col + j != col) and board[start_row + i][start_col + j] == num:
                return False
    return True


def find_empty(board):
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                return row, col
    return None

def fill_board(board):
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                possible = list(range(1, SIZE + 1))
                random.shuffle(possible)
                for candidate in possible:
                    if is_safe(board, row, col, candidate):
                        board[row][col] = candidate
                        if fill_board(board):
                            return True
                        board[row][col] = EMPTY
                return False
    return True

def count_solutions(board, limit=2):
    empty = find_empty(board)
    if empty is None:
        return 1

    row, col = empty
    total = 0
    for num in range(1, SIZE + 1):
        if is_safe(board, row, col, num):
            board[row][col] = num
            total += count_solutions(board, limit)
            board[row][col] = EMPTY
            if total >= limit:
                return total
    return total

def remove_cells(board, clues):
    target_removals = SIZE * SIZE - clues
    if target_removals <= 0:
        return True

    cells = [(row, col) for row in range(SIZE) for col in range(SIZE)]
    random.shuffle(cells)
    removed = 0

    for row, col in cells:
        if board[row][col] == EMPTY:
            continue

        backup = board[row][col]
        board[row][col] = EMPTY
        if count_solutions(board, limit=2) == 1:
            removed += 1
            if removed >= target_removals:
                return True
        else:
            board[row][col] = backup

    return removed >= target_removals

def generate_puzzle(clues=35, max_attempts=10):
    for _ in range(max_attempts):
        board = create_empty_board()
        fill_board(board)
        solution = deep_copy(board)
        puzzle = deep_copy(board)
        if remove_cells(puzzle, clues):
            return puzzle, solution
    raise RuntimeError('Unable to generate a unique puzzle with the requested clue count')
