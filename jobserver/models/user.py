"""User Model

General
-------

The User model is used to register and authenticate users. The User model
also implements the permissions on different routes of the REST api. For that
purpose, it can generate tokens, that have to be sent with each RESTful
request. Users can have different Roles. Roles define permissions.
"""
from hashlib import sha256
import uuid

from flask import current_app
from itsdangerous import BadSignature, SignatureExpired, \
    TimedJSONWebSignatureSerializer as Serializer

from .mongo import MongoModel


class User(MongoModel):
    collection = 'users'

    def __init__(self, email, password=None, activated=False, **kwargs):
        super(User, self).__init__(**kwargs)

        self.email = email.lower()
        if password is not None:
            self.password = password
        self.activated = activated

    @classmethod
    def get_by_email(cls, email):
        res = cls.mongo.db.users.find_one({'email': email})
        if res is None:
            return None
        else:
            return User(**res)

    @property
    def password(self):
        if self._pw_hash is not None:
            return '*****'
        return None

    def __setattr__(self, key, value):
        # save a password hash instead of a password
        if key == 'password':
            key = '_pw_hash'
            value = sha256(value.encode()).hexdigest()
        super(User, self).__setattr__(key=key, value=value)

    @classmethod
    def email_exists(cls, email):
        return cls.mongo.db.users.count_documents({'email': email}) > 0

    def verify_password(self, password):
        return sha256(password.encode()).hexdigest() == self._pw_hash

    def is_activated(self):
        return self.activated is True

    def get_activation_token(self):
        self.activated = '%s::%s' % (str(self.id), uuid.uuid4().hex)
        self.save()
        return self.activated

    def activate(self, token):
        if self.activated == token:
            self.activated = True
            self.save()
            return True
        else:
            return False

    def get_access_token(self):
        # create a JSON Web Signature
        serializer = Serializer(
            current_app.config['SECRET_KEY'],
            expires_in=current_app.config.get('ACCESS_TOKEN_LIFESPAN', 600)
        )

        return serializer.dumps({'id': str(self.id)})

    @classmethod
    def get_from_access_token(cls, token):
        # create JSON Web Signature
        serializer = Serializer(
            current_app.config['SECRET_KEY'],
            expires_in=current_app.config.get('ACCESS_TOKEN_LIFESPAN', 600)
        )

        # extract the payload
        payload = serializer.loads(token)

        return User.get(_id=payload['id'])

    def create(self):
        if User.email_exists(self.email):
            raise ValueError('The mail %s already exists.' % self.email)
        super(User, self).create()

    def update(self, data={}):
        # check if a new mail shall be set
        new_mail = data.get('email', self.email)

        # get the stored email from the db
        remote_mail = self.db.users.find_one({'_id': self.id}).get('email')

        # check
        if remote_mail != new_mail and User.email_exists(new_mail):
            raise ValueError('The new email %s is already registered.' %
                             new_mail)

        # call parent method
        super(User, self).update(data=data)


