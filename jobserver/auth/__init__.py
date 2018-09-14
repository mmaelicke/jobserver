from flask import Blueprint, g
from flask_restful import Api

from jobserver.auth.authorization import load_user_from_header_authorization,\
    login_required, user_route, role_required

auth_blueprint = Blueprint('auth', __name__)
auth_api = Api(auth_blueprint)

from . import login, user


@auth_blueprint.before_request
def check_login_state():
    """
    The Auth route does not require a login for all endpoints. The
    authorization status is set for each route individually
    """
    # get the user state
    response, status = load_user_from_header_authorization()

    # check was ok
    if status == 200:
        g.user = response
        return None
    elif status == 401:
        # No auth header set. this can happen here
        g.user = None
        return None
    else:
        g.user = None
        return response, status
