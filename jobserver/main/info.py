from flask_restful import Resource

from jobserver.main import main_api


class MainApi(Resource):
    def get(self):
        """Return general info

        This route will return general information about the jobserver. This
        response is usually used to verify that the instance is running and
        listening.

        Returns
        -------
        info : JSON
            JSON serialized response containing server info.

        """
        return {
            'status': 200,
            'message': 'Server is up and running',
            'version': 'a version number',
        }, 200


main_api.add_resource(MainApi, '/', '/info', endpoint='main')
