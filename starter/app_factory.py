"""Flask application factory for the Sudoku project."""

from flask import Flask

from .game_service import GameService
from .routes import create_routes


def create_app(test_config=None):
    """Create and configure the Flask application.

    The app factory keeps configuration and registrations centralized while
    preserving the existing URL behavior for the front end.
    """
    app = Flask(__name__, template_folder='templates', static_folder='static')

    if test_config is not None:
        app.config.update(test_config)

    game_service = GameService()
    app.extensions['game_service'] = game_service
    app.register_blueprint(create_routes(game_service))

    return app


app = create_app()
