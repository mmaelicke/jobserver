"""
RESTful endpoint for Job
"""
from flask import request, jsonify
from flask_restful import Resource
from bson.errors import InvalidId

from jobserver.models.job import Job
from jobserver.api import api_v1_blueprint, apiv1


class JobApi(Resource):
    def get(self, job_id):
        """GET Job

        GET request for an Job of id job_id

        Parameters
        ----------
        job_id : string
            ObjectId of the requested Job.

        Returns
        -------
        response : dict
            JSON response to this GET Request

        """
        # get the Job
        job = Job.get(job_id)

        # return
        if job is None:
            return {'status': 404, 'message': 'No Job of id %s' % job_id}
        else:
            return job.to_dict(stringify=True)

    def post(self, job_id):
        """POST request

        Handle a POST request to the job of job_id. This will update the
        job, as long as it was created, but not jet started. The data to be
        updated has to be sent as request data.

        Parameters
        ----------
        job_id : string
            ObjectId of the requested Job.

        Returns
        -------
        response : dict
            JSON response to this POST Request

        """
        # get the job
        job = Job.get(job_id)

        if job is None:
            return {'status': 404, 'message': 'No Job of id %s' % job_id}

        # get the data
        data = request.get_json()
        if len(data.keys()) == 0:
            return {'stauts': 412, 'message': 'No data received.'}, 412

        try:
            job.update(data=data)
        except Exception as e:
            return {'status': 500, 'message': str(e)}

        return job.to_dict(stringify=True), 200

    def put(self, job_id):
        """PUT request

        Handle a PUT request. A new job will be created using the passed
        data. If job_id is given, The function will try to create a Job of
        that given job_id.

        Parameters
        ----------
        job_id : string
            ObjectId of the Job to be created. Has to be a 12 byte name or a
            24 byte hex.

        Returns
        -------
        response : dict
            JSON response to this PUT Request

        """
        if Job.id_exists(job_id):
            return {
                'status': 409,
                'message': 'A job of id %s already exists' % job_id
            }, 409

        data = request.get_json()
        if data is None:
            data = dict()

        # create the Job
        try:
            job = Job(_id=job_id, **data)
            job.create()
        except InvalidId as e:
            return {'status': 505, 'message': str(e)}, 505
        except Exception as e:
            return {'status': 500, 'message': str(e)}, 500

        # return
        return job.to_dict(stringify=True), 201

    def delete(self, job_id):
        # get the job
        job = Job.get(job_id)
        if job is None:
            return {'status': 404,
                    'message': 'No job of id %s found' % job_id}, 404

        # delete
        if job.delete():
            return {'status': 200,
                    'acknowledged': True,
                    'message': 'Job of ID %s deleted.' % job_id}, 200
        else:
            return {
                'status': 500,
                'message': 'Something went horribly wrong.'
            }, 500


class JobsApi(Resource):
    def get(self):
        jobs = Job.get_all()

        return {
            'found': len(jobs),
            'jobs': [job.to_dict(stringify=True) for job in jobs]
        }, 200

    def delete(self):
        success, total = Job.delete_all()

        return {'status': 200,
                'acknowledged': success == total,
                'deleted': success,
                'total': total,
                'message': 'Deleted %d of %d Jobs' % (success, total)}, 200


# add the resources
apiv1.add_resource(JobApi, '/job/<string:job_id>', endpoint='job')
apiv1.add_resource(JobsApi, '/jobs', endpoint='jobs')


@api_v1_blueprint.route('/job', methods=['PUT'])
def put_job_without_id():
    """PUT Job without id

    Create a new Job entry without specifying the job_id. This is the
    preferred method for creating new jobs, as the job_id input has to match
    the MongoDB id pattern.

    Returns
    -------
    response : dict
        JSON response to this PUT Request

    """
    # get the data
    data = request.get_json()
    if data is None:
        data = dict()

    # create the Job
    try:
        job = Job(**data)
        job.create()
    except Exception as e:
        return jsonify({'status': 500, 'message': str(e)}), 500

    return jsonify(job.to_dict(stringify=True)), 201


@api_v1_blueprint.route('/job/<string:job_id>/run', methods=['GET', 'POST', 'PUT'])
def run_job(job_id):
    # get the requested Job
    job = Job.get(job_id)

    if job is None:
        return jsonify({
            'status': 404,
            'message': 'No Job of id %s' % job_id
        }), 404

    # start the job
    if job.started is None:
#        try:
        job.start()
#        except Exception as e:
#            return jsonify({'status': 500, 'message': str(e)}), 500

        # return the job
        return jsonify(job.to_dict(stringify=True)), 202

    # job was already started
    else:
        return jsonify({
            'status': 409,
            'message': 'The job %s was already started' % job_id
        }), 409
