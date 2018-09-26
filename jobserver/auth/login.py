from flask import jsonify, request

from jobserver.auth import auth_blueprint
from jobserver.models.user import User


@auth_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    # get the login information
    if request.authorization is not None:
        email = request.authorization.get('username')
        pw = request.authorization.get('password')
    else:
        email = request.form.get('email')
        pw = request.form.get('password')

    # get the user from mail
    user = User.get_by_email(email)

    # no user found
    if user is None:
        return jsonify({'status': 404, 'message': 'User not found.'}), 404

    # check activation status
    if not user.is_activated():
        return jsonify({
            'status': 409, 'message':
                'The user account is not activated yet.'
        }), 409

    # verify password
    if user.verify_password(pw):
        return jsonify({
            'user': user.to_dict(stringify=True),
            'access_token': user.get_access_token().decode('ascii')
        })
    else:
        return jsonify({'status': 405, 'message': 'password not correct.'}), 405


# @auth_blueprint.route('/activate', methods=['POST'])
# def activate():
#     # search GET for token
#     if request.args.get('token') is not None:
#         token = request.args.get('token')
#     elif request.form.get('token') is not None:
#         token = request.form.get('token')
#     elif request.json.get('token') is not None:
#         token = request.json.get('token')
#     else:
#         return jsonify({'status': 400, 'message': 'No token was passed.'}), 400
#
#     # split the token
#     user_id, _ = token.split('::')
#     user = User.get(user_id)
#     print(user.to_dict())
#
#     if user is None:
#         return jsonify({'status': 404, 'message': 'User not found.'}), 404
#
#     # activate
#     if user.activate(token):
#         return jsonify({'status': 200, 'acknowledged': True}), 200
#     else:
#         return jsonify({'stauts': 409, 'message': 'Token not valid'}), 409