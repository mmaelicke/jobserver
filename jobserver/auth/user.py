"""
RESTful endpoint for user management
"""
import json

from flask import request, url_for, current_app
from flask_restful import Resource

from jobserver.auth import auth_api
from jobserver.auth.authorization import login_required, user_route,\
    role_required
from jobserver.models.user import User
from jobserver.util.mail import Mail

ACTIVATION_MAIL_TEMPLATE = """
<h3>Account activation</h3>
<p>In order to activate your account: {0} click the link below, or copy the 
address to your browser.</p>

<a href="{1}">{1}</a>
"""


class UserApi(Resource):
    @login_required
    @user_route
    def get(self, user_id):
        """GET User

        Returns all information associated to the user of user_id. This route
        requires an active login and is limited to the user himself and all
        user of role permission defined in user_route decorator. Defaults to
        users of role 'superuser' or 'admin'

        Parameters
        ----------
        user_id : str
            id of the requested user

        Returns
        -------
        user : JSON
            JSON serialized content of the User information.

        """
        # get User
        user = User.get(_id=user_id)

        # check user exists
        if user is None:
            return {
                'status': 404,
                'message': 'User not found'
            }, 405

        return user.to_dict(stringify=True), 200

    @login_required
    @role_required(roles=['admin'])
    def post(self, user_id):
        """Edit user

        Request an edit to the user of user_id. Any JSON encoded content
        passed to this route will update the user of user_id.

        Parameters
        ----------
        user_id : str
            id of the requested user

        Returns
        -------
        user : JSON
            JSON serialized content of the updated User information.

        """
        # get User
        user = User.get(_id=user_id)

        # check user exists
        if user is None:
            return {
                'status': 404,
                'message': 'User not found'
            }, 405

        # get the data
        data = request.get_json()
        if len(data.keys()) == 0:
            return {'status': 412, 'message': 'No content recieved'}, 412

        # update the user
        try:
            user.update(data=data)
        except Exception as e:
            return {'status': 500, 'message': str(e)}, 500

        # return updated user
        return user.to_dict(stringify=True), 200

    @login_required
    @user_route(roles=['admin'])
    def delete(self, user_id):
        """Delete the user

        Delete the requested user. This action can only be performed by the
        user of user_id himself or any user of role superuser and users of
        decorated roles (usually 'admin').

        The user information will be stored into the backup folder into the
        json backup file specified in the application cofig

        Parameters
        ----------
        user_id : str
            id of the requested user

        Returns
        -------
        response : JSON
            acknowledgement message

        """
        # get the user
        user = User.get(_id=user_id)

        if user is None:
            return {
                'status': 404,
                'message': 'User not found.'
            }, 404

        # get the user info
        d = user.to_dict(stringify=True)

        # delete
        user.delete()

        # store
        with open(current_app.config.get('DELETED_USER_PATH'), 'w+') as backup:
            data = json.load(backup)
            data['users'].append(d)
            backup.write(data)

        # return
        return {
            'status': 200,
            'acknowledged': True,
            'message': 'User has been deleted.'
        }, 200


class UsersApi(Resource):
    @login_required
    @role_required(roles=['admin'])
    def get(self):
        """GET all users

        Get all users registered in the database. This can only be performed
        by a superuser or users of a role defined in the decorator function.

        Returns
        -------
        users : JSON
            JSON serialized list of all Users

        """
        # get the users
        users = User.get_all()

        return {
            'status': 200,
            'found': len(users),
            'users': users
        }, 200


class UserRegistrationApi(Resource):
    def put(self):
        """User registration

        PUT a new user to the database. This user will be registered but not
        activated. Thus, he will not be able to authorize for any protected
        routes. Users can be activated by clicking the link sent to the
        registered email address.

        Returns
        -------
        user : JSON
            JSON serialized content of the new User information.

        """
        # get the data
        data = request.get_json()

        email = data.get('email')
        pw = data.get('password')

        # at least email and password is needed
        if email is None or pw is None:
            return {
                'status': 400,
                'message': 'At least a email and password is needed.'
            }, 400

        # Check if this email already exists
        if User.email_exists(email=email):
            return {
                'status': 409,
                'message': 'The email %s is already registered.' % email
            }, 409

        # create the user
        user = User(
            email=email,
            password=pw,
            role='user',
            job_credit=10
        )
        user.create()

        # get an activation token
        token = user.get_activation_token()

        # build the activation link
        url = url_for('auth.activation', token=token, user_id=str(user.id),
                      _external=True)

        # build the activation mail and sent
#        msg = Message(
#            'Your account activation',
#            recipients=[user.email],
#            html=ACTIVATION_MAIL_TEMPLATE.format(email, url)
#        )
        # send the activation mail
        mail = Mail()
        mail.send(
            _to=user.email,
            subject='Your account activation',
            message=ACTIVATION_MAIL_TEMPLATE.format(email, url)
        )

        return {
            'status': 201,
            'message': 'An activation mail has been sent to: %s. Your user '
                       'ID is: %s.' % (email, str(user.id))
        }, 201


class UserActivationApi(Resource):
    def get(self, user_id):
        """Link Activation

        This route is used to activate a user account by a GET request. Then
        the activation token has to be passed by url PARAM like:
        SERVER/user/user_id/activate?token=YOURTOKEN

        Parameters
        ----------
        user_id : str
            id of the requested user

        Returns
        -------
        user : JSON
            JSON serialized content of the activated User information.

        """
        # make sure a token was passed
        token = request.args.get('token')
        if token is None:
            return {
                'status': 409,
                'message': 'No activation token was passed.'
            }, 409

        # load the user
        user = User.get(_id=user_id)

        if user is None:
            return {
                'status': 404,
                'message': 'User not found.'
            }, 404

        # activate
        if user.activate(token=token):
            return {
                'status': 200,
                'acknowledged': True,
                'user': user.to_dict(stringify=True)
            }, 200
        else:
            return {
                'status': 400,
                'message': 'The activation token is invalid.'
            }, 400

    def put(self, user_id):
        """Request new activation link

        A PUT request to request a new activation link. This route will
        overwrite old activation tokens and needs a email client configured.

        Parameters
        ----------
        user_id : str
            id of the requested user

        Returns
        -------
        response : JSON
            JSON serialized acknowledgement message

        """
        # load the user
        user = User.get(_id=user_id)

        if user is None:
            return {
                'status': 404,
                'message': 'User not found.'
            }, 404

        # create a new activation token
        token = user.get_activation_token()

        # build the activation link
        url = url_for('auth.activation', token=token, user_id=str(user.id),
                      _external=True)

        # build the activation mail and sent
#        msg = Message(
#            'Your account activation',
#            recipients=[user.email],
#            html=ACTIVATION_MAIL_TEMPLATE.format(user.email, url)
#        )
        mail = Mail()
        mail.send(
            user.email,
            'Your new activation link',
            ACTIVATION_MAIL_TEMPLATE.format(user.email, url)
        )

        return {
            'status': 200,
            'message': 'A new activation mail has been sent to: %s.' +
                       'Your user ID is: %s' % (user.email, str(user.id))
        }, 200


auth_api.add_resource(UserApi, '/user/<string:user_id>', endpoint='user')
auth_api.add_resource(UsersApi, '/users', endpoint='users')
auth_api.add_resource(UserRegistrationApi, '/user', endpoint='registration')
auth_api.add_resource(UserActivationApi, '/user/<string:user_id>/activate',
                      endpoint='activation')
