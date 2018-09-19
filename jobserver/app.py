import os

from flask import Flask
from flask_mail import Mail

from jobserver import scripts
from jobserver.config import config
from jobserver.models.mongo import mongo

mail = Mail()

APP_PATH = os.path.abspath(os.path.dirname(__file__))


def create_app(config_name='default'):
    app = Flask(__name__)

    # load config
    app.config.from_object(config.get(config_name, 'default'))

    # initialize the MongoDB connection
    mongo.init_app(app)

    # initialize Mail client
    mail.init_app(app)

    # add Blueprints
    from jobserver.api import api_v1_blueprint
    app.register_blueprint(api_v1_blueprint)

    from jobserver.auth import auth_blueprint
    app.register_blueprint(auth_blueprint)

    from jobserver.main import main_blueprint
    app.register_blueprint(main_blueprint)

    # as a last step, call the scripts on_init function
    scripts.on_init(app)

    return app


if __name__ == '__main__':
    import sys
    config_name = sys.argv[1] if len(sys.argv) > 1 else 'default'
    app = create_app(config_name)
    app.run()
