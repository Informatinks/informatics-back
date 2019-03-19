from logging.config import dictConfig

from flask import Flask

from informatics_front import cli
from informatics_front.model import db
from informatics_front.model.comment import Comment
from informatics_front.model.course_module import CourseModule, CourseModuleInstance
from informatics_front.model.problem import Problem
from informatics_front.model.statement import Statement
from informatics_front.model.user.user import User
from informatics_front.plugins import internal_rmatics, tokenizer, gmail
from informatics_front.utils.auth import authenticate
from informatics_front.utils.error_handlers import register_error_handlers
from informatics_front.utils.tokenizer.handlers import map_action_routes
from informatics_front.view import handle_api_exception
from informatics_front.view.auth.authorization import PasswordChangeApi
from informatics_front.view.auth.routes import auth_blueprint
from informatics_front.view.course.contest.route import contest_blueprint

ACTIONS_URL_MOUNTPOINT = 'actions'
CHANGE_PASSWORD_ACTION_ROUTENAME = 'change_password'


def create_app(config=None):
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

    app.config.from_pyfile('settings.cfg', silent=True)
    app.config.from_envvar('INFROMATICS_FRONT_SETTINGS', silent=True)
    if config:
        app.config.update(config)
    app.url_map.strict_slashes = False

    db.init_app(app)

    internal_rmatics.init_app(app)

    tokenizer.init_app(app)

    gmail.init_mailer(app)

    # register password change action to app
    map_action_routes(app, (
        (CHANGE_PASSWORD_ACTION_ROUTENAME, PasswordChangeApi.as_view(CHANGE_PASSWORD_ACTION_ROUTENAME), 86000),
    ), ACTIONS_URL_MOUNTPOINT)

    app.before_request(authenticate)
    register_error_handlers(app)

    app.register_blueprint(auth_blueprint)
    app.register_blueprint(contest_blueprint)

    app.cli.add_command(cli.test)
    return app


if __name__ == "__main__":
    app = create_app()

    app.run(debug=False)
