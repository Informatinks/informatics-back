from typing import Optional

from flask import current_app, g, request
from flask.views import MethodView

from marshmallow import fields
from sqlalchemy.orm import joinedload
from webargs.flaskparser import parser
from werkzeug import exceptions as exc
from gmail import Message
from informatics_front import db
from informatics_front.model.refresh_tokens import RefreshToken
from informatics_front.model.user.user import User
from informatics_front.utils.auth import login_required
from informatics_front.utils.auth.make_jwt import decode_jwt_token, generate_refresh_token
from informatics_front.utils.response import jsonify
from informatics_front.view.auth.serializers.auth import UserAuthSerializer
from informatics_front.plugins import tokenizer
from informatics_front.plugins import gmail
from werkzeug.exceptions import BadRequest


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
        refresh_token = RefreshToken(token=token, user_id=user.id)
        db.session.add(refresh_token)
        db.session.commit()

        user_serializer = UserAuthSerializer()
        user.refresh_token = token
        user_data = user_serializer.dump(user)

        return jsonify(user_data.data)


class LogoutApi(MethodView):
    post_args = {
        'refresh_token': fields.String(required=True),
    }

    @login_required
    def post(self):
        user = g.user
        args = parser.parse(self.post_args, request)

        db.session.query(RefreshToken).filter_by(user_id=user['id'],
                                                 token=args.get('refresh_token')).delete()
        db.session.commit()

        current_app.logger.debug(f'user_id={user["id"]} has logged out')

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
    """API handler for invoding password reset action for User.email or User.user_name
    """
    post_args = {
        'email': fields.String(missing=None),
        'username': fields.String(missing=None),
    }

    def post(self):
        # TODO: raise 422 if none of params found
        args = parser.parse(self.post_args, request)

        # prevent equal-None filter query
        user, query_kwars, email, username = \
            None, {}, args.get('email'), args.get('username')

        # prepare request query
        if email:
            query_kwars['email'] = email
        elif username:
            query_kwars['username'] = username

        # run query only if at least one condition exists
        if len(query_kwars) > 0:
            user = db.session.query(User) \
                .filter_by(**query_kwars) \
                .one_or_none()

        if not user:  # user was not populated with parsed conditions
            raise BadRequest()

        payload = {
            'user_id': user.id
        }
        token = tokenizer.pack(payload)

        text = f"Ссылка для сброса пароля: {current_app.config.get('APP_URL')}/change_password?token={token}"

        msg = Message('Test Message', to='xyz <xyz@xyz.com>', text='Hello')
        gmail.send(msg)

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
