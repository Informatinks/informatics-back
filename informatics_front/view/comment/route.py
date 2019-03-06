from flask import Blueprint

from informatics_front.view.comment.comment import CommentApi

comment_blueprint = Blueprint('comment', __name__, url_prefix='/api/v1/comment')

comment_blueprint.add_url_rule('/get/<int:run_id>', methods=('GET',),
                               view_func=CommentApi.as_view('comment'))
