from pathlib import Path

import pytest
from starter.app_factory import create_app
from starter.game_service import GameService


@pytest.fixture
def client():
    app = create_app({'TESTING': True})
    with app.test_client() as client:
        yield client


def test_app_starts_and_homepage_loads(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'Sudoku Game' in response.data


def test_homepage_includes_theme_toggle(client):
    response = client.get('/')
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert 'id="theme-toggle"' in html
    assert 'Switch to Dark Mode' in html


def test_homepage_includes_responsive_layout_and_leaderboard(client):
    response = client.get('/')
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert 'class="page-shell"' in html
    assert 'class="game-layout"' in html
    assert 'id="leaderboard-list"' in html
    assert 'Leaderboard' in html


def test_static_assets_support_alternating_block_colors():
    workspace_root = Path(__file__).resolve().parents[1]
    styles_path = workspace_root / 'starter' / 'static' / 'styles.css'
    main_js_path = workspace_root / 'starter' / 'static' / 'main.js'

    styles = styles_path.read_text(encoding='utf-8')
    main_js = main_js_path.read_text(encoding='utf-8')

    assert 'data-block' in main_js
    assert '--block-bg-odd' in styles
    assert '--block-bg-even' in styles


def test_new_game_route_returns_puzzle(client):
    response = client.get('/new?clues=35')
    assert response.status_code == 200
    payload = response.get_json()
    assert 'puzzle' in payload
    assert isinstance(payload['puzzle'], list)
    assert len(payload['puzzle']) == 9
    assert all(isinstance(row, list) for row in payload['puzzle'])


def test_difficulty_param_selects_clue_count(client):
    easy_response = client.get('/new?difficulty=easy')
    medium_response = client.get('/new?difficulty=medium')
    hard_response = client.get('/new?difficulty=hard')

    assert easy_response.status_code == 200
    assert medium_response.status_code == 200
    assert hard_response.status_code == 200

    easy_puzzle = easy_response.get_json()['puzzle']
    medium_puzzle = medium_response.get_json()['puzzle']
    hard_puzzle = hard_response.get_json()['puzzle']

    assert sum(cell != 0 for row in easy_puzzle for cell in row) == 40
    assert sum(cell != 0 for row in medium_puzzle for cell in row) == 32
    assert sum(cell != 0 for row in hard_puzzle for cell in row) == 25


def test_new_game_route_returns_timer_state(client):
    response = client.get('/new?clues=35')

    assert response.status_code == 200
    payload = response.get_json()
    assert payload['timer']['running'] is True
    assert payload['timer']['formatted_time'] == '00:00'


def test_check_route_stops_timer_when_solution_is_correct(client):
    client.get('/new?difficulty=easy')
    solution = client.application.extensions['game_service'].current['solution']

    response = client.post('/check', json={'board': solution})
    assert response.status_code == 200
    data = response.get_json()
    assert data['incorrect'] == []
    assert data['timer']['running'] is False
    assert data['timer']['formatted_time'] == '00:00'


def test_check_route_marks_completion_and_records_leaderboard_entry(client):
    client.get('/new?difficulty=easy')
    service = client.application.extensions['game_service']
    solution = service.current['solution']

    response = client.post('/check', json={'board': solution, 'player_name': 'Ada'})
    assert response.status_code == 200
    data = response.get_json()
    assert data['completed'] is True
    assert data['incorrect'] == []
    assert data['timer']['running'] is False
    assert data['leaderboard'][-1]['player_name'] == 'Ada'


def test_new_game_resets_completion_state(client):
    client.get('/new?difficulty=easy')
    service = client.application.extensions['game_service']
    solution = service.current['solution']

    client.post('/check', json={'board': solution, 'player_name': 'Ada'})
    response = client.get('/new?clues=35')

    assert response.status_code == 200
    assert service.current['completed'] is False
    assert response.get_json()['timer']['running'] is True


def test_check_route_reports_incorrect_cells(client):
    client.get('/new?difficulty=easy')
    service = client.application.extensions['game_service']
    puzzle = service.current['puzzle']
    solution = service.current['solution']

    board = [row.copy() for row in puzzle]
    for i in range(9):
        for j in range(9):
            if board[i][j] == 0:
                board[i][j] = (solution[i][j] % 9) + 1
                wrong_cell = [i, j]
                break
        else:
            continue
        break

    response = client.post('/check', json={'board': board})
    assert response.status_code == 200
    data = response.get_json()
    assert 'incorrect' in data
    assert wrong_cell in data['incorrect']


def test_check_route_returns_no_incorrect_for_solution(client):
    client.get('/new?difficulty=easy')
    solution = client.application.extensions['game_service'].current['solution']

    response = client.post('/check', json={'board': solution})
    assert response.status_code == 200
    data = response.get_json()
    assert data['incorrect'] == []
    assert data['timer']['running'] is False


def test_hint_route_fills_one_empty_cell_and_tracks_usage(client):
    client.get('/new?difficulty=easy')
    service = client.application.extensions['game_service']
    initial_puzzle = [row.copy() for row in service.current['puzzle']]
    initial_empty_count = sum(cell == 0 for row in initial_puzzle for cell in row)

    response = client.post('/hint')
    assert response.status_code == 200
    data = response.get_json()

    assert data['hints_used'] == 1
    hint = data['hint']
    assert hint['value'] == service.current['solution'][hint['row']][hint['col']]
    assert service.current['puzzle'][hint['row']][hint['col']] == hint['value']
    assert initial_puzzle[hint['row']][hint['col']] == 0
    assert sum(cell == 0 for row in service.current['puzzle'] for cell in row) == initial_empty_count - 1


def test_leaderboard_entries_capture_metadata_and_remain_sorted(client):
    client.get('/new?difficulty=easy')
    service = client.application.extensions['game_service']

    for elapsed_seconds, player_name in [(40, 'Zoe'), (10, 'Ada'), (25, 'Ben'), (5, 'Ivy'), (8, 'Kai'), (6, 'Mia'), (9, 'Nia'), (11, 'Ollie'), (14, 'Pia'), (7, 'Rae'), (15, 'Sam'), (16, 'Tia')]:
        service.current['timer_elapsed_seconds'] = elapsed_seconds
        service.current['timer_running'] = False
        service.current['timer_started_at'] = None
        service.record_leaderboard_entry(player_name, difficulty_level='easy', hints_used=1)

    leaderboard = service.current['leaderboard']
    assert len(leaderboard) == 10
    assert [entry['player_name'] for entry in leaderboard] == ['Ivy', 'Mia', 'Rae', 'Kai', 'Nia', 'Ada', 'Ollie', 'Pia', 'Sam', 'Tia']
    assert leaderboard[0]['completion_time_seconds'] == 5
    assert leaderboard[0]['difficulty_level'] == 'easy'
    assert leaderboard[0]['hints_used'] == 1


def test_check_route_records_leaderboard_metadata(client):
    client.get('/new?difficulty=easy')
    service = client.application.extensions['game_service']
    service.current['hints_used'] = 2
    solution = service.current['solution']

    response = client.post('/check', json={
        'board': solution,
        'player_name': 'Ada',
        'difficulty_level': 'easy',
        'hints_used': service.current['hints_used'],
    })

    assert response.status_code == 200
    data = response.get_json()
    assert data['completed'] is True
    entry = data['leaderboard'][-1]
    assert entry['player_name'] == 'Ada'
    assert entry['difficulty_level'] == 'easy'
    assert entry['hints_used'] == 2
    assert entry['completion_time_seconds'] == 0
    assert entry['completion_time'] == '00:00'
