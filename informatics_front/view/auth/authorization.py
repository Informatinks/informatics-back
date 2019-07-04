from typing import Optional

from flask import current_app, g, request
from flask.views import MethodView
from gmail import Message
from marshmallow import fields
from sqlalchemy.orm import joinedload
from webargs.flaskparser import parser
from werkzeug import exceptions as exc
from werkzeug.exceptions import BadRequest

from informatics_front.utils.auth.request_user import current_user
from informatics_front.model import db
from informatics_front.model.refresh_tokens import RefreshToken
from informatics_front.model.user.user import User
from informatics_front.plugins import gmail
from informatics_front.plugins import tokenizer
from informatics_front.utils.auth.middleware import login_required
from informatics_front.utils.auth.make_jwt import decode_jwt_token, generate_refresh_token
from informatics_front.utils.response import jsonify
from informatics_front.utils.sqla.race_handler import get_or_create
from informatics_front.view.auth.serializers.auth import UserAuthSerializer


class LoginApi(MethodView):
    post_args = {
        'username': fields.String(required=True),
        'password': fields.String(required=True)
    }

    def post(self):

        args = parser.parse(self.post_args, request)

        username, password = args['username'], args['password']

        user = db.session.query(User) \
            .filter(User.username == username) \
            .filter(User.deleted.isnot(True)) \
            .options(joinedload(User.roles)) \
            .one_or_none()

        if user is None:
            raise exc.NotFound('User with this username does not exist')

        is_password_valid = User.check_password(user.password_md5, password)
        if not is_password_valid:
            current_app.logger.warning(f'user_email={args["username"]} '
                                       f'has failed to log in')
            raise exc.Forbidden('Invalid password')

        current_app.logger.debug(f'user_email={args["username"]} has logged in')

        token = generate_refresh_token(user)
        refresh_token, is_created = get_or_create(RefreshToken, token=token, user_id=user.id)
        db.session.add(refresh_token)

        user_serializer = UserAuthSerializer()
        user.refresh_token = token
        user_data = user_serializer.dump(user)

        if is_created:
            db.session.commit()

        return jsonify(user_data.data)


class LogoutApi(MethodView):
    post_args = {
        'refresh_token': fields.String(required=True),
    }

    @login_required
    def post(self):
        args = parser.parse(self.post_args, request)

        db.session.query(RefreshToken).filter_by(user_id=current_user.id,
                                                 token=args.get('refresh_token')).delete()
        db.session.commit()

        current_app.logger.debug(f'user_id={current_user.id} has logged out')

        return jsonify({}, 200)


class RefreshTokenApi(MethodView):
    post_args = {
        'refresh_token': fields.String(required=True),
    }

    @staticmethod
    def _validate_token(token) -> Optional[User]:
        payload = decode_jwt_token(token)

        if not payload or not payload.get('user_id'):
            return None

        refresh_token = db.session.query(RefreshToken) \
            .filter_by(user_id=payload['user_id'], token=token, valid=True) \
            .one_or_none()

        if refresh_token is None:
            return None

        return refresh_token.user

    def post(self):
        args = parser.parse(self.post_args, request)
        token = args.get('refresh_token')

        user = self._validate_token(token)
        if user is None:
            current_app.logger.warning(f'Someone has sent invalid refresh token')
            raise exc.Forbidden('Refresh token has been expired')

        excludes = ('refresh_token',)
        serializer = UserAuthSerializer(exclude=excludes)
        user_data = serializer.dump(user)

        current_app.logger.debug(f'user_id={user.id} '
                                 f'user_email={user.email} token has '
                                 f'been refreshed')

        return jsonify(user_data.data)


class PasswordResetApi(MethodView):
    """API handler for invoking password reset action for User.email or User.user_name
    """
    post_args = {
        'email': fields.String(missing=None),
        'username': fields.String(missing=None),
    }

    def post(self):
        args = parser.parse(self.post_args, request)

        # prevent equal-None filter query
        email, username = args.get('email'), args.get('username')
        if not any((email, username)):
            raise BadRequest()

        user_q = db.session.query(User)
        if email is not None:
            user_q = user_q.filter(User.email == email)
        elif username is not None:
            user_q = user_q.filter(User.username == username)
        user = user_q.one_or_none()

        # if user not found or user has no valid email
        if user is None or user.email is None or user.email == '':
            raise BadRequest('Either user is not found or has no valid email')

        payload = {
            'user_id': user.id
        }
        token = tokenizer.pack(payload)

        text = f"Ссылка для сброса пароля: {current_app.config.get('APP_URL')}/auth/change-password?token={token}"
        msg = Message('Сброс пароля', to=user.email, text=text)
        try:
            gmail.send(msg)
        except Exception as e:  # TODO: handle smtplib errors
            current_app.logger.exception('Unable to send reset password message to', user.email)

        return jsonify({})


class PasswordChangeApi(MethodView):
    """API handler for setting new password

    This method should NOT be mounted directly to route as it relies on external action authorization.
    """
    post_args = {
        'password': fields.String(required=True),
    }

    def post(self):
        args = parser.parse(self.post_args, request)
        user = db.session.query(User). \
            filter_by(id=g.payload.get('user_id')). \
            one_or_none()

        if user:
            user.password_md5 = User.hash_password(args.get('password'))
            db.session.commit()

        return jsonify({})
