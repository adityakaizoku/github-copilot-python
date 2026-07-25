"""Route definitions for the Sudoku Flask application."""

from flask import Blueprint, jsonify, render_template, request


DIFFICULTY_CLUES = {
    'easy': 40,
    'medium': 32,
    'hard': 25,
}


def create_routes(game_service):
    """Create a blueprint that uses the provided game service."""
    bp = Blueprint('main', __name__)

    @bp.route('/')
    def index():
        return render_template('index.html')

    @bp.route('/new')
    def new_game():
        difficulty = request.args.get('difficulty', '').lower()
        clues_param = request.args.get('clues')

        if clues_param is not None:
            clues = int(clues_param)
        else:
            clues = DIFFICULTY_CLUES.get(difficulty, 35)

        puzzle, _ = game_service.new_game(clues)
        return jsonify({'puzzle': puzzle, 'timer': game_service.get_timer_state()})

    @bp.route('/hint', methods=['POST'])
    def hint():
        hint = game_service.apply_hint()
        if hint is None:
            return jsonify({'error': 'No empty cells available'}), 400
        return jsonify({'hint': hint, 'hints_used': game_service.current['hints_used']})

    @bp.route('/check', methods=['POST'])
    def check_solution():
        data = request.json or {}
        board = data.get('board')
        player_name = data.get('player_name')
        difficulty_level = data.get('difficulty_level')
        hints_used = data.get('hints_used')
        incorrect = game_service.check_solution(
            board,
            player_name=player_name,
            difficulty_level=difficulty_level,
            hints_used=hints_used,
        )
        if incorrect is None:
            return jsonify({'error': 'No game in progress'}), 400
        return jsonify({
            'incorrect': incorrect,
            'timer': game_service.get_timer_state(),
            'completed': game_service.current['completed'],
            'leaderboard': game_service.current['leaderboard'],
        })

    return bp
