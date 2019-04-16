from sqlalchemy.orm import relationship

from informatics_front.model.base import db
from informatics_front.utils.decorators import deprecated
from informatics_front.utils.json_type import JsonType


class Problem(db.Model):
    __table_args__ = {'schema':'moodle'}
    __tablename__ = 'mdl_problems'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(255))
    content = db.Column(db.Text)
    review = db.Column(db.Text)
    hidden = db.Column(db.Boolean)
    timelimit = db.Column(db.Float)
    memorylimit = db.Column(db.Integer)
    description = db.Column(db.Text)
    analysis = db.Column(db.Text)
    sample_tests = db.Column(db.Unicode(255))
    sample_tests_html = db.Column(db.Text)
    sample_tests_json = db.Column(JsonType)
    show_limits = db.Column(db.Boolean)
    output_only = db.Column(db.Boolean)
    pr_id = db.Column(db.Integer, db.ForeignKey('moodle.mdl_ejudge_problem.id'))
    ejudge_problem = relationship('EjudgeProblem', lazy='select')

    def __init__(self, *args, **kwargs):
        super(Problem, self).__init__(*args, **kwargs)
        self.hidden = 1
        self.show_limits = True


class EjudgeProblem(Problem):
    """
    Модель задачи из ejudge

    ejudge_prid -- primary key, на который ссылается Problem.pr_id.
        После инициализации, соответствтующему объекту Problem проставляется корректный pr_id

    contest_id --

    ejudge_contest_id -- соответствует contest_id из ejudge

    secondary_ejudge_contest_id --

    problem_id -- соответствует problem_id из ejudge

    short_id -- короткий id (обычно буква)

    Здесь используется наследование и polymorphic_identity
    Это значит, что можно написать
    problem_id = Problem.id
    query(EjudgeProblem).filter(EjudgeProblem.id == problem_id)  # вернет Problem
    При этом неявно приджойнится Problem.pr_id == EjudgeProblem.id

    Ещё это даёт нам интересные эффекты, например
    query(EjudgeProblem).all() вернёт как EjudgeProblem, так и Problem, a
    query(EjudgeProblem).filter(EjudgeProblem.id == 6).all() -- только Problem
    А вот такое query(EjudgeProblem).get(6) -- вообще вернёт None, потому что join не отработает
    Ещё в Runs у нас ссылка на обе таблицы, и это тоже работает нормально
    """

    __table_args__ = (
        {'schema':'moodle', 'extend_existing': True}
    )
    __tablename__ = 'mdl_ejudge_problem'
    __mapper_args__ = {'polymorphic_identity': 'ejudgeproblem'}

    ejudge_prid = db.Column('id', db.Integer, primary_key=True) #global id in ejudge
    contest_id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=False)
    ejudge_contest_id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=False)
    secondary_ejudge_contest_id = db.Column(db.Integer, nullable=True)
    problem_id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=False) #id in contest
    short_id = db.Column(db.Unicode(50))
    ejudge_name = db.Column('name', db.Unicode(255))

    @staticmethod
    def create(**kwargs):
        """
        При создании EjudgeProblem сначала в базу пишет Problem потом EjudgeProblem,
        из-за чего pr_id не проставляется
        """
        instance = EjudgeProblem(**kwargs)
        db.session.add(instance)
        db.session.flush([instance])

        problem_id = instance.id
        ejudge_problem_id = instance.pr_id
        db.session.commit()

        problem_instance = db.session.query(Problem).filter_by(id=problem_id).one()
        problem_instance.pr_id = ejudge_problem_id
        db.session.commit()

        return db.session.query(EjudgeProblem).filter_by(id=problem_id).one()

    @deprecated('view.serializers.ProblemSchema')
    def serialize(self):
        if self.sample_tests:
            self.generateSamplesJson(force_update=True)

        attrs = [
            'id',
            'name',
            'content',
            'timelimit',
            'memorylimit',
            'show_limits',
            'sample_tests_json',
            'output_only',
        ]
        problem_dict = {
            attr: getattr(self, attr, 'undefined')
            for attr in attrs
        }
        # problem_dict['languages'] = context.get_allowed_languages()
        return problem_dict

    def generateSamples(self):
        res = ""
        if self.sample_tests != '':
            res = "<div class='problem-statement'><div class='sample-tests'><div class='section-title'>Примеры</div>"

            for i in self.sample_tests.split(","):
                inp = self.get_test(i, 4096)
                if inp[-1] == '\n':
                    inp = inp[:-1]
                corr = self.get_corr(i, 4096)
                if corr[-1] == '\n':
                    corr = corr[:-1]
                res += "<div class='sample-test'>"
                res += "<div class='input'><div class='title'>Входные данные</div><pre class='content'>"
                res += inp
                res += "</pre></div><div class='output'><div class='title'>Выходные данные</div><pre class='content'>"
                res += corr
                res += "</pre></div></div>"

            res += "</div></div>"

        self.sample_tests_html = res
        return self.sample_tests

    def generateSamplesJson(self, force_update=False):
        if self.sample_tests != '':
            if not self.sample_tests_json:
                self.sample_tests_json = {}
            for test in self.sample_tests.split(','):
                if not force_update and test in self.sample_tests_json:
                    continue

                test_input = self.get_test(test, 4096)
                test_correct = self.get_corr(test, 4096)

                self.sample_tests_json[test] = {
                    'input': test_input,
                    'correct': test_correct,
                }
