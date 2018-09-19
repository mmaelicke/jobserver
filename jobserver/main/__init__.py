from flask import Blueprint
from flask_restful import Api

main_blueprint = Blueprint('main', __name__)
main_api = Api(main_blueprint)

from . import info