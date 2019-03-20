from flask import Blueprint

from informatics_front.view.auth.authorization import LoginApi, LogoutApi, RefreshTokenApi, PasswordResetApi

auth_blueprint = Blueprint('auth', __name__, url_prefix='/api/v1/auth')

auth_blueprint.add_url_rule('/signin', methods=('POST',),
                            view_func=LoginApi.as_view('login'))

auth_blueprint.add_url_rule('/signout', methods=('POST',),
                            view_func=LogoutApi.as_view('logout'))

auth_blueprint.add_url_rule('/refresh', methods=('POST',),
                            view_func=RefreshTokenApi.as_view('refresh'))

auth_blueprint.add_url_rule('/reset', methods=('POST',),
                            view_func=PasswordResetApi.as_view('reset'))
