"""Application service layer for the Sudoku Flask app.

This module keeps the in-memory game state separate from the Flask routes so
that the routes remain focused on request handling and the game logic can be
reused and tested more easily.
"""
import time
from . import sudoku_logic


class GameService:
    """Manage the current puzzle and its solution for the active game."""

    def __init__(self):
        self.current = {
            'puzzle': None,
            'solution': None,
            'hints_used': 0,
            'timer_running': False,
            'timer_started_at': None,
            'timer_elapsed_seconds': 0,
            'completed': False,
            'leaderboard': [],
            'leaderboard_recorded': False,
        }

    def new_game(self, clues):
        """Generate a fresh puzzle and store the matching solution."""
        puzzle, solution = sudoku_logic.generate_puzzle(clues)
        self.current['puzzle'] = puzzle
        self.current['solution'] = solution
        self.current['hints_used'] = 0
        self.current['completed'] = False
        self.current['leaderboard_recorded'] = False
        self._start_timer()
        return puzzle, solution

    def apply_hint(self):
        """Fill one empty cell with the correct solution value and lock it."""
        puzzle = self.current.get('puzzle')
        solution = self.current.get('solution')
        if puzzle is None or solution is None:
            return None

        for i in range(sudoku_logic.SIZE):
            for j in range(sudoku_logic.SIZE):
                if puzzle[i][j] == 0:
                    puzzle[i][j] = solution[i][j]
                    self.current['hints_used'] += 1
                    return {'row': i, 'col': j, 'value': solution[i][j]}
        return None

    def check_solution(self, board, player_name=None, difficulty_level=None, hints_used=None):
        """Return the positions that do not match the stored solution."""
        solution = self.current.get('solution')
        if solution is None:
            return None

        incorrect = []
        for i in range(sudoku_logic.SIZE):
            for j in range(sudoku_logic.SIZE):
                if board[i][j] != solution[i][j]:
                    incorrect.append([i, j])

        if not incorrect:
            self._stop_timer()
            self.current['completed'] = True
            if player_name and not self.current['leaderboard_recorded']:
                self.record_leaderboard_entry(
                    player_name,
                    difficulty_level=difficulty_level,
                    hints_used=hints_used,
                )
                self.current['leaderboard_recorded'] = True
        return incorrect

    def record_leaderboard_entry(self, player_name, difficulty_level=None, hints_used=None):
        """Store a leaderboard entry with metadata and keep the top 10 fastest times."""
        time_state = self.get_timer_state()
        entry = {
            'player_name': player_name,
            'completion_time_seconds': time_state['elapsed_seconds'],
            'completion_time': time_state['formatted_time'],
            'difficulty_level': difficulty_level or 'unknown',
            'hints_used': hints_used if hints_used is not None else self.current.get('hints_used', 0),
        }
        self.current['leaderboard'].append(entry)
        self.current['leaderboard'] = sorted(
            self.current['leaderboard'],
            key=lambda item: (
                item['completion_time_seconds'],
                item['player_name'].lower(),
            ),
        )[:10]
        return entry

    def get_timer_state(self):
        """Return a serializable snapshot of the current timer state."""
        elapsed_seconds = self._get_elapsed_seconds()
        return {
            'running': self.current['timer_running'],
            'elapsed_seconds': elapsed_seconds,
            'formatted_time': self._format_time(elapsed_seconds),
        }

    def _start_timer(self):
        self.current['timer_running'] = True
        self.current['timer_started_at'] = time.time()
        self.current['timer_elapsed_seconds'] = 0

    def _stop_timer(self):
        if self.current['timer_running']:
            self.current['timer_elapsed_seconds'] = self._get_elapsed_seconds()
        self.current['timer_running'] = False
        self.current['timer_started_at'] = None

    def _get_elapsed_seconds(self):
        if not self.current['timer_running'] or self.current['timer_started_at'] is None:
            return self.current['timer_elapsed_seconds']
        return int(time.time() - self.current['timer_started_at']) + self.current['timer_elapsed_seconds']

    @staticmethod
    def _format_time(total_seconds):
        total_seconds = max(0, int(total_seconds))
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f'{minutes:02d}:{seconds:02d}'
