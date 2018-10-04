"""
RESTful endpoint for handling data in MongoDB
"""
from flask import request
from flask_restful import Resource
from bson.errors import InvalidId, InvalidDocument

from jobserver.api import apiv1
from jobserver.models.data_mongo import DataMongo
from jobserver.auth.authorization import get_user_bound_filter


class DataMongoApi(Resource):
    def get(self, data_id):
        """GET a Data Object

        Returns a Data Object, which is any kind of JSON serializable object.
        These objects might return big amounts of data in the response body
        of this request.

        Parameters
        ----------
        data_id : str
            ObjectId of the requested data object.

        Returns
        -------
        response : dict
            JSON response to this GET data request

        """
        # get the filter
        _filter = get_user_bound_filter(['admin'])

        # get the data object
        data = DataMongo.get(_id=data_id, filter=_filter)
        if data is None:
            return {
                'status': 405,
                'message': 'Data Object ID not found'
            }, 405
        else:
            return data.to_dict(stringify=True), 200

    def post(self, data_id):
        """ Edit a Data Object

        Edit an existing Data Object. This route does not return the edited
        Data Object as these might be quite big. Instead an acknowledge
        message is returned. If the applications needs the object itself,
        the GET route needs to be called.

        Parameters
        ----------
        data_id : str
            ObjectId of the requested data object.

        Returns
        -------
        response : dict
            JSON response to this POST edit request

        """
        # get the filter
        _filter = get_user_bound_filter(['admin'])

        # get the data object
        data = DataMongo.get(_id=data_id, filter=_filter)
        if data is None:
            return {
                'status': 405,
                'message': 'Data Object ID not found'
            }, 405

        # get the passed JSON body with edits
        body = request.get_json()
        if body is None:
            return {
                'status': 409,
                'message': 'No edited data was passed'
            }, 409

        # update the data
        data.update(data=body)

        # do not return the updated data object, just acknowledge the update
        return {
            'status': 200,
            'acknowledged': True,
            'id': str(data.id),
            'message': 'Data Object of ID %s has been updated.' % str(data.id)
        }, 200

    def put(self, data_id):
        """Create Data Object

        A new Data Object of given ID will be created and stored in the
        database. An database.

        Parameters
        ----------
        data_id : str
            ObjectId of the requested data object.

        Returns
        -------
        response : dict
            JSON response to this PUT create request

        """
        # check if this data_id already exists
        if DataMongo.id_exists(_id=data_id):
            return {
                'status': 409,
                'message': 'An Data Object of ID %s already exists' % data_id
            }, 409

        # get the passed data
        data = request.get_json()
        if data is None:
            return {
                'status': 409,
                'message': 'No Data body passed.'
            }, 409

        # get user info filter
        _filter = get_user_bound_filter(['admin'])
        data.update(_filter)

        # create the Data Object
        try:
            data = DataMongo(_id=data_id, **data)
            data.create()
        except InvalidId as e:
            return {
                'status': 409,
                'message': str(e)
            }, 409
        except InvalidDocument as e:
            return {
                'status': 409,
                'message': str(e)
            }, 409

        # no errors occurred return a acknowledgement message
        return {
            'status': 201,
            'acknowledged': True,
            'message': 'Data Object of ID %s created.' % str(data_id)
        }, 201

    def delete(self, data_id):
        """DELETE a Data Object

        The requested Data Object will be deleted from the database.

        Parameters
        ----------
        data_id : str
            ObjectId of the requested data object.

        Returns
        -------
        response : dict
            JSON response to this DELETE data request

        """
        # get the filter
        _filter = get_user_bound_filter(['admin'])

        # get the data object
        data = DataMongo.get(_id=data_id, filter=_filter)
        if data is None:
            return {
                'status': 405,
                'message': 'Data Object ID not found'
            }, 405

        if data.delete():
            return {
                'status': 200,
                'acknowledged': True,
                'message': 'Data Object of ID %s deleted.' % str(data_id)
            }, 200
        else:
            return {
                'status': 500,
                'message': 'Something went horribly wrong.'

            }, 500


apiv1.add_resource(DataMongoApi, '/data/<string:data_id>', endpoint='data')
