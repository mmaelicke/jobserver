"""
RESTful endpoint for meta data about the available scripts
"""
import inspect

from flask_restful import Resource

from jobserver.util import load_script_func
from jobserver.app import scripts
from jobserver.api import apiv1


class ScriptApi(Resource):
    def get(self, name):
        # load the function
        try:
            func = load_script_func(module='scripts', name=name)
        except Exception as e:
            # TODO: catch more specific here
            return {'status': 500, 'message': str(e)}, 500

        return {
            'name': name,
            'description': func.__doc__,
            'parameters': func.__code__.co_varnames
        }


class ScriptsApi(Resource):
    def get(self):
        # define little helper
        def _check(func_name):
            if func_name.startswith('_'):
                return False
            elif func_name == 'on_init':
                return False
            elif inspect.ismodule(getattr(scripts, func_name)):
                return False
            else:
                return True

        # get all functions in scripts
        f_list = [getattr(scripts, n) for n in scripts.__dir__() if _check(n)]

        # return
        return {
            'found': len(f_list),
            'scripts': [{
                'name': f.__name__,
                'description': f.__doc__,
                'parameters': f.__code__.co_varnames
            } for f in f_list]
        }


# add the resources
apiv1.add_resource(ScriptApi, '/script/<string:name>', endpoint='script')
apiv1.add_resource(ScriptsApi, '/scripts', endpoint='scripts')
