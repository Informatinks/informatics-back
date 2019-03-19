from time import sleep
from unittest.mock import Mock, MagicMock

import pytest
from flask import url_for
from flask.views import MethodView

from informatics_front.plugins import tokenizer
from informatics_front.utils.tokenizer.handlers import map_action_routes

BLUEPRINT_PREFIX_NAME = 'actions'
ROUTE_NAME = 'test'
ACTION_PAYLOAD = {}


@pytest.mark.handlers
def test_create_blueprint(app):
    """Test Handler adds new blueprint to app instance
    """
    view = MagicMock()
    view.__name__ = ROUTE_NAME
    view.get.return_value = 'foo'
    initial_blueprints_len = len(app.blueprints)

    # create handler with one route
    map_action_routes(app, ((ROUTE_NAME, view, 60),), f'/{BLUEPRINT_PREFIX_NAME}')

    # test blueprints added
    assert len(app.blueprints) == initial_blueprints_len + 1
    assert BLUEPRINT_PREFIX_NAME in app.blueprints

    # test separate route was created for blueprint
    blueprint = app.blueprints.pop(BLUEPRINT_PREFIX_NAME)
    blueprint_routes_len = len(blueprint.deferred_functions)
    assert blueprint_routes_len == 1


@pytest.mark.handlers
def test_call_methodview(local_app, local_client):
    """Test added blueprint runs appropriate request method for provided
    MethodView instance
    """

    View = MethodView
    View.get = Mock()
    View.get.return_value = 'foo'

    # create handler with one route
    map_action_routes(local_app,
                      ((ROUTE_NAME, View.as_view(ROUTE_NAME), 60),),
                      f'/{BLUEPRINT_PREFIX_NAME}')

    url = url_for(f'actions.{ROUTE_NAME}', token=tokenizer.pack(ACTION_PAYLOAD))
    local_client.get(url, )

    View.get.assert_called()


@pytest.mark.handlers
def test_call_plan_function(local_app, local_client):
    """Test added blueprint runs provided plain function
    """
    view = MagicMock()
    view.__name__ = ROUTE_NAME
    view.return_value = ''

    # create handler with one route
    map_action_routes(local_app,
                      ((ROUTE_NAME, view, 60),),
                      f'/{BLUEPRINT_PREFIX_NAME}')

    url = url_for(f'actions.{ROUTE_NAME}', token=tokenizer.pack(ACTION_PAYLOAD))
    local_client.get(url)

    view.assert_called()


@pytest.mark.handlers
def test_invalid_token_decoding(local_app, local_client):
    """Test if handler should not be invoked if token decoding fails
    """
    VALID_TOKEN = tokenizer.pack(ACTION_PAYLOAD)
    INVALID_TOKEN = f'INVALID_{VALID_TOKEN}'
    TOKEN_TTL = 5

    view = MagicMock()
    view.__name__ = ROUTE_NAME
    view.return_value = ''

    # create handler with one route
    map_action_routes(local_app,
                      ((ROUTE_NAME, view, TOKEN_TTL),),
                      f'/{BLUEPRINT_PREFIX_NAME}')

    # test token expiration
    url = url_for(f'{BLUEPRINT_PREFIX_NAME}.{ROUTE_NAME}', token=VALID_TOKEN)

    # wait until token expires
    sleep(TOKEN_TTL + 1)

    local_client.get(url)
    view.assert_not_called()
    view.reset_mock()

    # test invalid token
    url = url_for(f'{BLUEPRINT_PREFIX_NAME}.{ROUTE_NAME}', token=INVALID_TOKEN)
    local_client.get(url)
    view.assert_not_called()
    view.reset_mock()


