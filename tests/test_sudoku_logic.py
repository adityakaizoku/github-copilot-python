import pytest

from starter import sudoku_logic


@pytest.mark.parametrize('clues', [40, 32, 25])
def test_generated_puzzle_has_unique_solution(clues):
    puzzle, solution = sudoku_logic.generate_puzzle(clues)
    assert sum(cell != sudoku_logic.EMPTY for row in puzzle for cell in row) == clues
    assert puzzle != solution
    assert sudoku_logic.count_solutions(sudoku_logic.deep_copy(puzzle), limit=2) == 1


def test_is_valid_move_flags_conflicts_in_row_column_and_box():
    board = sudoku_logic.create_empty_board()
    board[0][0] = 1
    board[0][1] = 2
    board[1][0] = 3
    board[2][2] = 4

    assert sudoku_logic.is_valid_move(board, 0, 2, 1) is False
    assert sudoku_logic.is_valid_move(board, 2, 0, 3) is False
    assert sudoku_logic.is_valid_move(board, 1, 1, 4) is False
    assert sudoku_logic.is_valid_move(board, 0, 2, 5) is True
