from flask import g
from flask.views import MethodView

from informatics_front.model.base import db
from informatics_front.model import Comment

from informatics_front.utils.auth import login_required
from informatics_front.utils.response import jsonify

from informatics_front.view.comment.serializers.comment import CommentSchema


class CommentApi(MethodView):
    @login_required
    def get(self, run_id):
        '''
        Returns List[Comment] for current authorized user for requested run_id
        '''
        user = g.user

        # if provided run_id not not found, return []
        comments = db.session.query(Comment) \
            .filter(Comment.py_run_id == run_id,
                    Comment.user_id == user.get('id')) \
            .all()

        comment_schema = CommentSchema(many=True)
        response = comment_schema.dump(comments)

        return jsonify(response.data)
