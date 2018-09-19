import base64
from functools import wraps, partial

from flask import jsonify, request, g, current_app

from jobserver.models.user import User


def check_user_logged_in(user, password=None, check_activation=True):
    # check if a user was found
    if user is None:
        return jsonify({
            'status': 404,
            'message': 'User not found.'
        }), 404

    # check activation status
    if check_activation and not user.is_activated():
        return jsonify({
            'status': 405,
            'message': 'Your account has not been activated.'
        }), 405

    if password is not None:
        if not user.verify_password(password=password):
            return jsonify({
                'status': 405,
                'message': 'The password was incorrect'
            }), 405

    return user, 200


def login_required(route):
    @wraps(route)
    def login_checker(*args, **kwargs):
        if g.user is None:
            return {
                'status': 405,
                'message': 'Login required'
            }, 405
        else:
            return route(*args, **kwargs)
    return login_checker


def user_route(route=None, roles=['admin']):
    if route is None:
        return partial(user_route, roles=roles)

    @wraps(route)
    def content_checker(*args, **kwargs):
        # check that there is a active user
        if g.user is None:
            return {
                'status': 405,
                'message': 'Login required'
            }, 405

        # check if active user has a permission role
        if g.user.role == 'superuser' or g.user.role in roles:
            return route(*args, **kwargs)

        # get the user id from the route
        user_id = kwargs.geet('user_id')
        if user_id is None:
            return {
                       'status': 404,
                       'message': 'No user_id specified.'
                   }, 404

        # check if the active user is the requested
        if str(g.user.id) != user_id:
            return {
                'status': 405,
                'message': 'Unauthorized. Wrong user and no permission.'
            }, 405
        else:
            return route(*args, **kwargs)
    return content_checker


def role_required(route=None, roles=['admin']):
    if route is None:
        return partial(role_required, roles=roles)

    @wraps(route)
    def role_checker(*args, **kwargs):
        # check that there is a active user
        if g.user is None:
            return {
                       'status': 405,
                       'message': 'Login required'
                   }, 405

        # check if active user has a permission role
        if g.user.role == 'superuser' or g.user.role in roles:
            return route(*args, **kwargs)
        else:
            return {
                'status': 405,
                'message': 'Unauthorized. Your role is not permitted'
            }, 405

    return role_checker


def load_user_from_header_authorization():
    if 'Authorization' not in request.headers:
        return jsonify({
            'status': 401,
            'message': 'No HTTP Authorization HEADER found.'
        }), 401
    else:
        auth_header = request.headers.get('Authorization')

    # check the different supported Authorization methods
    if 'basic' in auth_header.lower():
        enc = base64.b64decode(auth_header[6:]).decode()
        email, password = enc.split(':')

        # get the user
        user = User.get_by_email(email=email)

    elif 'bearer' in auth_header.lower():
        token = auth_header[7:]

        # get the user
        user = User.get_from_access_token(token=token)

        # password is not required
        password = None

    else:
        return jsonify({
            'status': 501,
            'message': 'Only Basic and Bearer Authorization are implemented'
        }), 501

    return check_user_logged_in(user, password, check_activation=True)
