import datetime

from informatics_front.model.base import db


class Comment(db.Model):
    __tablename__ = "mdl_run_comments"
    __table_args__ = {'schema': 'ejudge'}

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    contest_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer, nullable=False)
    author_user_id = db.Column(db.Integer, db.ForeignKey('moodle.mdl_user.id'), nullable=False)
    author_user = db.relation("User", uselist=False, lazy='select')
    run_id = db.Column(db.Integer)  # deprecated
    lines = db.Column(db.Text)
    comment = db.Column(db.Text)
    is_read = db.Column(db.Boolean)
    py_run_id = db.Column(db.Integer)

    def get_by(run_id, contest_id):
        try:
            return db.session.query(Comment).filter(Comment.run.run_id == int(run_id)).filter(
                Comment.contest_id == int(contest_id)).first()
        except:
            return None

    get_by = staticmethod(get_by)


RECAPTCHA_URL = "https://www.google.com/recaptcha/api/siteverify"


def check_captcha(secret, resp):
    params = {
       'secret': secret,
       'response': resp
    }

    r = requests.get(RECAPTCHA_URL, params=params)
    return r.json().get("success", False)


def require_captcha(f):
    @functools.wraps(f)
    def wrapper(request, *args, **kwargs):
        recaptha_resp = request.params['g-recaptcha-response']
        if not check_captcha(recaptha_resp, request.registry.settings["recaptcha.secret"]):
            return "Не получилось"
        return f(request, *args, **kwargs)
    return wrapper


@require_captcha
@view_config(route_name="protocol.get_submit_archive", renderer="string")
@check_global_role(("ejudge_teacher", "admin"))
def get_submit_archive(request):

    request_source = "sources" in request.params
    run_id = int(request.matchdict['run_id'])
    problem_id = int(request.matchdict['problem_id'])
    request_all_tests = "all_tests" in request.params

    if not request_all_tests:
        require_test_numbers = request.params.get("tests", "")
        if require_test_numbers:
            tests_numbers_set = list(
                sorted(
                    set(
                        map(int, require_test_numbers.split(' ')))
                )
            )
        else:
            tests_numbers_set = list()
    else:
        # TODO: Здесть не 100, а некое максимальное число тестов
        # TODO: Его можно было найти в EjudgeRun.tests_count,
        # TODO: который брался из протокола
        # TODO: Но мы это пофиксили
        tests_numbers_set = list(range(1, 100))

    archive = BytesIO()
    zip_file = zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED)

    if request_source:
        # Download source and info about run
        url = 'http://localhost:12346/problem/run/{}/source/'.format(run_id)
        try:
            resp = requests.get(url, {'is_admin': True})
            resp.raise_for_status()
        except (requests.RequestException, ValueError) as e:
            print('Request to :12346 failed!')
            print(str(e))
            return {"result": "error", "message": str(e), "stack": traceback.format_exc()}

        content = resp.json()
        data = content['data']
        lang_id = data['language_id']
        request_source = data['source']

        # Write source
        source_name = "{0}{1}".format(run_id, get_lang_ext_by_id(lang_id))
        zip_file.writestr(source_name, request_source)

    # TODO: Перенести логику выкачивания тестов проблем в rmatics/ejudge-core
    ejudge_problem = DBSession.query(EjudgeProblem).get(problem_id)

    # Write tests
    for num in tests_numbers_set:
        try:
            test_data = ejudge_problem.get_test(num, ejudge_problem.get_test_size(num))
            answer_data = ejudge_problem.get_corr(num, ejudge_problem.get_corr_size(num))

            zip_file.writestr("tests/{0:02}".format(num), test_data)
            zip_file.writestr("tests/{0:02}.a".format(num), answer_data)
        except FileNotFoundError:
            break

    # Write checkers
    checker_src, checker_ext = ejudge_problem.get_checker()
    zip_file.writestr("checker{}".format(checker_ext), checker_src)

    zip_file.close()
    archive.seek(0)

    response = Response(content_type="application/zip",
                        content_disposition='attachment; filename="archive_{0}_{1}.zip"'.format(
                            problem_id, run_id),
                        body=archive.read())
    return response