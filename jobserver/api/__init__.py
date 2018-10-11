from flask import Blueprint, jsonify, current_app, g, request
from flask_restful import Api

from jobserver.auth.authorization import load_user_from_header_authorization

api_v1_blueprint = Blueprint('apiv1', __name__)
apiv1 = Api(api_v1_blueprint)

from . import data_file, data_mongo, job, script


@api_v1_blueprint.before_request
def check_login_state():
    """Check Login state

    This validator checks the request for authentication information. It
    should protect the whole API. It can be replaced by Blueprints holding
    only part of the API, in case a more refined auth is required. The check
    can be turned off in development mode by setting the config variable
    API_V1_LOGIN to False.
    
    Returns
    -------

    """
    # check if it is a OPTIONS request
    if request.method.lower() == 'options':
        return None

    # check if the login status shall be tested
    if not current_app.config.get('API_V1_LOGIN'):
        g.user = None
        return None

    # check
    response, status = load_user_from_header_authorization()

    # check was ok
    if status == 200:
        g.user = response
        return None

    # there was a non None response
    else:
        g.user = None
        return response, status


@api_v1_blueprint.route('/protected', methods=['GET', 'POST'])
def protected():
    return jsonify({'user': g.user.to_dict(stringify=True)})