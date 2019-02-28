import os
import sys

import click
import pytest
from flask.cli import with_appcontext

THIS_FILE = os.path.abspath(os.path.dirname(__file__))
TESTS_DIR = os.path.join(THIS_FILE, 'tests/')


@click.command('test')
@click.option('--teamcity', is_flag=True, default=False)
@with_appcontext
def test(teamcity):
    """Command for running tests under CI.

    For development purposes please use pytest directly:

    $ PYTHONPATH=. pytest -sv  # or similar
    """
    pytest_args = [TESTS_DIR, '-v']
    if teamcity:
        pytest_args.append('--teamcity')

    sys.exit(pytest.main(pytest_args))


if __name__ == '__main__':
    test()
