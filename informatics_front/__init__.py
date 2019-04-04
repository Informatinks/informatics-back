from logging.config import dictConfig

from flask import Flask

from informatics_front import cli
from informatics_front.model import db
from informatics_front.plugins import gmail
from informatics_front.plugins import internal_rmatics
from informatics_front.plugins import tokenizer
from informatics_front.utils.auth import authenticate
from informatics_front.utils.error_handlers import register_error_handlers
from informatics_front.utils.tokenizer.handlers import map_action_routes
from informatics_front.view import handle_api_exception
from informatics_front.view.auth.authorization import PasswordChangeApi
from informatics_front.view.auth.routes import auth_blueprint
from informatics_front.view.course.contest.route import contest_blueprint

ACTIONS_URL_MOUNTPOINT = '/api/v1/actions'
CHANGE_PASSWORD_ACTION_ROUTENAME = 'change-password'


def create_app(config):
    dictConfig({
        'version': 1,
        'formatters': {'default': {
            'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        }},
        'handlers': {'stdout': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://flask.logging.wsgi_errors_stream',
            'formatter': 'default'
        }},
        'root': {
            'level': 'INFO',
            'handlers': ['stdout']
        }
    })

    app = Flask(__name__)
    app.config.from_object(config)
    app.url_map.strict_slashes = False
    app.logger.info(f'Running with {config} module')

    db.init_app(app)
    internal_rmatics.init_app(app)
    tokenizer.init_app(app)
    gmail.init_app(app)

    # register password change action to app
    map_action_routes(app, (
        (CHANGE_PASSWORD_ACTION_ROUTENAME,
         PasswordChangeApi.as_view(CHANGE_PASSWORD_ACTION_ROUTENAME), 86000),
    ), ACTIONS_URL_MOUNTPOINT)

    app.before_request(authenticate)
    register_error_handlers(app)

    app.register_blueprint(auth_blueprint)
    app.register_blueprint(contest_blueprint)

    app.cli.add_command(cli.test)

    return app
