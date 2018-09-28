"""
RESTful endpoint for handling data files
"""
from flask import request, jsonify, make_response
from flask_restful import Resource

from jobserver.models.data_file import DataFile
from jobserver.api import api_v1_blueprint, apiv1


class DataFileApi(Resource):
    def post(self, name):
        if DataFile.name_exists(name):
            return {
                       'status': 409,
                       'message': 'Data file of name %s already exists.' % name
                   }, 409

        # upload
        try:
            pointer = request.files['file']
        except KeyError:
            return {'status': 400, 'message': 'No file passed'}, 400

        f = DataFile.upload(file_name=name, file_pointer=pointer)

        # return
        return {
            'name': f.name(),
            'path': f.path,
            'status': 201,
            'message': 'The resource was created'
               }, 201

    def put(self, name):
        return self.post(name=name)

    def delete(self, name):
        if not DataFile.name_exists(name):
            return {
                       'status': 404,
                       'message': 'Data file of name %s not found.' % name
                   }, 409
        else:
            f = DataFile.get_from_name(name=name)
            f.delete()

        return {'status': 200, 'message': 'Resource %s deleted.' % name}, 200


class DataFilesApi(Resource):
    def get(self):
        files = DataFile.find_all()

        file_list = [f.to_dict() for f in files]

        return {
            'found': len(file_list),
            'files': file_list
               }, 200

    def delete(self):
        files = DataFile.find_all()

        # delete
        for f in files:
            f.delete()
        return {'status': 200, 'message': 'All files deleted'}, 200


# add the resources
apiv1.add_resource(DataFilesApi, '/datafiles')
apiv1.add_resource(DataFileApi, '/datafile/<string:name>', endpoint='datafile')


@api_v1_blueprint.route('/datafile/<string:name>', methods=['GET'])
def get(name):
    """GET request for DataFile

    Load a data file from the DATA_DIR. if the url parameter format was
    set, the content of the file will be returned. Supported formats are
    'csv', 'json', 'html' and 'txt'.
    If the parameter is omitted, only the DataFile instance is returned
    as JSON response

    Parameters
    ----------
    name : string
        The name of the file, including fle extension, located in the
        DATA_DIR.

    Returns
    -------
    response : dict
        JSON response to this GET Request

    """
    # get the file
    f = DataFile.get_from_name(name=name)

    # return 404 if file does not exist
    if f is None:
        return jsonify({
                   'status': 404,
                   'message': 'A data file of name %s was not found.' % name
               }), 404

    # check if params are given
    if 'format' not in request.args:
        return jsonify({
            'name': f.name(),
            'path': f.path,
            'size': f.size()
        })
    else:
        # load data
        data = f.read()
        fmt = request.args['format']
        if fmt.lower() == 'csv':
            mime = 'text/pain'
            content = data.to_csv(sep=',', index=None)
        elif fmt.lower() == 'json':
            mime = 'application/json'
            content = data.to_json()
        elif fmt.lower() == 'html':
            mime = 'text/html'
            content = data.to_html()
        else:
            mime = 'text/plain'
            content = data.to_csv(sep='\t')
        response = make_response(content)
        response.headers['Content-type'] = mime
        return response


