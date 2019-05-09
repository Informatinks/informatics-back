from unittest.mock import patch

from informatics_front.utils.run import EjudgeStatuses
from informatics_front.view.course.monitor.monitor_preprocessor import IOIResultMaker, BaseResultMaker, \
    MonitorPreprocessor


class TestBaseResultMaker:
    def test_make_result(self):
        expected = {
            'on_testing': True,
            'is_ignored': True,
            'mark': 12345,
            'time': 12346,
            'success': True,
            'wrong_tries': 1000500,
        }
        resp = BaseResultMaker._make_result(**expected)

        assert resp == expected

    def test_is_still_testing(self):
        in_queue = EjudgeStatuses.IN_QUEUE.value
        any_other = EjudgeStatuses.CE.value

        runs = [{'ejudge_status': any_other},
                {'ejudge_status': any_other},
                {'ejudge_status': any_other}]

        assert not BaseResultMaker._is_still_testing(runs)

        runs = [{'ejudge_status': any_other},
                {'ejudge_status': in_queue},
                {'ejudge_status': any_other}]

        assert BaseResultMaker._is_still_testing(runs)

    def test_is_last_ignored(self):
        ignored = EjudgeStatuses.IGNORED.value
        any_other = EjudgeStatuses.CE.value
        runs = [{'ejudge_status': any_other},
                {'ejudge_status': any_other},
                {'ejudge_status': ignored}]

        assert BaseResultMaker._is_last_ignored(runs)

        runs = [{'ejudge_status': any_other},
                {'ejudge_status': ignored},
                {'ejudge_status': any_other}]

        assert not BaseResultMaker._is_last_ignored(runs)

    def test_render(self):
        expected = {123: '456'}
        patch_pref = 'informatics_front.view.course.monitor.monitor_preprocessor.IOIResultMaker'
        with patch(
                f'{patch_pref}._make_result') \
                as make_result:
            make_result.return_value = expected
            maker = IOIResultMaker()
            with \
                    patch(f'{patch_pref}._is_still_testing') as is_testing, \
                    patch(f'{patch_pref}.update_score_by_statuses') as update_score_by_statuses, \
                    patch(f'{patch_pref}.get_wrong_tries_count') as get_wrong_tries_count, \
                    patch(f'{patch_pref}._is_last_ignored') as _is_last_ignored, \
                    patch(f'{patch_pref}.get_current_mark') as get_current_mark, \
                    patch(f'{patch_pref}.is_success') as is_success:

                is_testing.return_value = False
                get_wrong_tries_count.return_value = 3
                _is_last_ignored.return_value = False
                get_current_mark.return_value = 5
                is_success.return_value = 'meh'

                result = maker.render([])

        is_testing.assert_called_once()
        update_score_by_statuses.assert_called_once()
        get_wrong_tries_count.assert_called_once()
        _is_last_ignored.assert_called_once()
        get_current_mark.assert_called_once()
        is_success.assert_called_once()
        make_result.assert_called_once()

        assert result == expected

        _, kwargs = make_result.call_args
        assert kwargs == {
            'on_testing': False,
            'is_ignored': False,
            'mark': 5,
            'time': 0,
            'success': 'meh',
            'wrong_tries': 3,
        }


class TestIOIResultMaker:

    def test_get_wrong_tries_count(self):
        wrong_status = EjudgeStatuses.TL.value
        good_status = EjudgeStatuses.OK.value
        runs = [{'ejudge_status': wrong_status},
                {'ejudge_status': wrong_status},
                {'ejudge_status': good_status},
                {'ejudge_status': wrong_status}]

        assert IOIResultMaker.get_wrong_tries_count(runs) == 3

    def test_get_current_mark(self):
        max_mark = 100500
        runs = [
            {'ejudge_score': 1},
            {'ejudge_score': 2},
            {'ejudge_score': 3},
            {'ejudge_score': max_mark},
            {'ejudge_score': 4},
        ]

        assert IOIResultMaker.get_current_mark(runs) == str(max_mark)

    def test_update_score_by_statuses(self):
        wrong_status = EjudgeStatuses.TL.value
        ok_status = EjudgeStatuses.OK.value
        pt_status = EjudgeStatuses.PARTIAL.value

        runs = [{'ejudge_status': ok_status,
                 'ejudge_score': 1}]
        IOIResultMaker.update_score_by_statuses(runs)
        assert runs[0]['ejudge_score'] == IOIResultMaker.MAX_POINTS

        runs = [{'ejudge_status': pt_status,
                 'ejudge_score': 123}]
        IOIResultMaker.update_score_by_statuses(runs)
        assert runs[0]['ejudge_score'] == 123

        runs = [{'ejudge_status': wrong_status,
                 'ejudge_score': 123}]
        IOIResultMaker.update_score_by_statuses(runs)
        assert runs[0]['ejudge_score'] == 0


class TestMonitorPreprocessor:
    def test_group_by_users(self):
        runs = [
            {'user': {'id': 1}},
            {'user': {'id': 1}},
            {'user': {'id': 2}},
            {'user': {'id': 2}},
            {'user': {'id': 2}},
            {'user': {'id': 3}},
        ]

        expects = {
            1: [{'user': {'id': 1}}, {'user': {'id': 1}}],
            2: [{'user': {'id': 2}}, {'user': {'id': 2}}, {'user': {'id': 2}}],
            3: [{'user': {'id': 3}}]
        }

        resp = MonitorPreprocessor._group_by_users(runs)

        assert dict(resp) == expects

    # TODO: test MonitorPreprocessor.render
