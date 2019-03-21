from . import configparser
import os
from collections import OrderedDict


def normalize_memory_limit(limit):
    if limit[-1:] == "G":
        return int(limit[:-1]) * 1024 * 1024 * 1024
    if limit[-1:] == "M":
        return int(limit[:-1]) * 1024 * 1024
    elif limit[-1:] == "K":
        return int(limit[:-1]) * 1024
    else:
        return int(limit)


class EjudgeProblemCfg:
    def __init__(self, d, id, contest):
        self.dict = d
        self.id = id
        self.short_name = str(id).strip("\"")
        if "super" in d:
            self.abstract = d["super"][0].strip("\"")
        else:
            self.abstract = None

        if "short_name" in d:
            self.short_name = d["short_name"][0].strip("\"")

        if "internal_name" in d:
            self.internal_name = d["internal_name"][0].strip("\"")
        else:
            self.internal_name = self.short_name

        self.long_name = ""
        if "long_name" in d:
            self.long_name = d["long_name"][0].strip("\"")
        self.time_limit = -1

        self.output_only = False
        if "type" in d:
            if d["type"][0].strip("\"") == "output-only":
                self.output_only = True
        else:
            if self.abstract is not None and "type" in contest.abstract[self.abstract] \
                    and contest.abstract[self.abstract]["type"][0].strip(
                "\"") == 'output-only':
                self.output_only = True

        if "time_limit_millis" in d:
            self.time_limit = float(d["time_limit_millis"][0]) / 1000
        elif "time_limit" in d:
            self.time_limit = float(d["time_limit"][0])
        else:
            if self.abstract is not None and "time_limit_millis" in contest.abstract[
                self.abstract]:
                self.time_limit = float(
                    contest.abstract[self.abstract]["time_limit_millis"][0]) / 1000
            if self.abstract is not None and "time_limit" in contest.abstract[
                self.abstract]:
                self.time_limit = float(
                    contest.abstract[self.abstract]["time_limit"][0])

        if "max_vm_size" in d:
            self.memory_limit = normalize_memory_limit(d["max_vm_size"][0])
        else:
            if self.abstract is not None and "max_vm_size" in contest.abstract[
                self.abstract]:
                self.memory_limit = normalize_memory_limit(
                    contest.abstract[self.abstract]["max_vm_size"][0])

        if "test_dir" in d:
            self.test_dir = d["test_dir"][0].strip("\"")
        else:
            if self.abstract is not None and "test_dir" in contest.abstract[
                self.abstract]:
                self.test_dir = contest.abstract[self.abstract]["test_dir"][0].strip(
                    "\"")
            else:
                self.test_dir = ""

        if "corr_dir" in d:
            self.corr_dir = d["corr_dir"][0].strip("\"")
        else:
            if self.abstract is not None and "corr_dir" in contest.abstract[
                self.abstract]:
                self.corr_dir = contest.abstract[self.abstract]["corr_dir"][0].strip(
                    "\"")

        problem_dir = contest.test_dir + "/"

        if self.internal_name is not None:
            problem_id = self.internal_name
        else:
            problem_id = self.short_name

        problem_dir += self.test_dir.replace("%lPs", problem_id.lower()).replace("%Ps",
                                    problem_id)

        if contest.advanced_layout:
            self.tests_dir = contest.contest_path + 'problems/' + self.internal_name + '/tests/'
        else:
            self.tests_dir = contest.contest_path + 'tests/' + problem_dir + '/'

        self.tests_dir = os.path.normpath(self.tests_dir) + '/'

        if "test_pat" in d:
            self.test_pat = d["test_pat"][0].strip("\"")
        else:
            if self.abstract is not None and "test_pat" in contest.abstract[self.abstract]:
                self.test_pat = contest.abstract[self.abstract]["test_pat"][0].strip(
                    "\"")

        if "corr_pat" in d:
            self.corr_pat = d["corr_pat"][0].strip("\"")
        else:
            if self.abstract is not None and "corr_pat" in contest.abstract[self.abstract]:
                self.corr_pat = contest.abstract[self.abstract]["corr_pat"][0].strip(
                    "\"")

    def getInfo(self):
        return {"long_name": self.long_name,
                "id": self.id,
                "short_name": self.short_name,
                "timelimit": self.time_limit,
                "abstract": self.abstract}


HOME_JUDGES = '/home/judges/'


class EjudgeContestCfg:
    @staticmethod
    def get_contest_path(number):
        return HOME_JUDGES + '0' * (6 - len(str(number))) + str(number) + '/'

    @staticmethod
    def get_contest_path_conf(number):
        return EjudgeContestCfg.get_contest_path(number) + 'conf/'

    def __init__(self, path='', number=-1):
        if number > 0:
            path = EjudgeContestCfg.get_contest_path_conf(number) + 'serve.cfg'
        if os.path.exists(path):
            self.config = configparser.ConfigParser(allow_no_value=True, strict=False,
                                                    interpolation=None)
            self.config.read(path)
            self.advanced_layout = self.config.has_option("default", 0,
                                                          "advanced_layout")

            if self.config.has_option("default", 0, "test_dir"):
                self.test_dir = self.config.get("default", 0, "test_dir")[0].strip("\"")
            else:
                self.test_dir = ""
            self.contest_path = EjudgeContestCfg.get_contest_path(number)
            self.st_path = EjudgeContestCfg.get_contest_path_conf(number)
            self.init_problem()
        else:
            raise IOError("File not found '" + path + "'")

    def init_problem(self):
        last_id = 0
        self.abstract = OrderedDict()
        self.problems = OrderedDict()
        for e in self.config['problem']:
            if 'abstract' not in e:
                curId = int(last_id) + 1
                if 'id' in e:
                    curId = e['id'][0]
                last_id = curId
                self.problems[int(curId)] = EjudgeProblemCfg(e, curId, self)
            else:
                self.abstract[e['short_name'][0].strip("\"")] = e

    def get_problem(self, id):
        return self.problems[int(id)]
