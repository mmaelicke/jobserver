"""Job model class.

General
-------
This class handles CRUD operations on the MongoDB instance to manage the Jobs.

A Job is a descriptive model of a user starting a script, monitoring the
execution and viewing the results.

Examples
--------
Build a new Job, containing information about the Process to be executed.

>>> job = Job(scipt_name='summary')
>>> job.create()

"""
from threading import Thread
from datetime import datetime as dt

from flask import g

from jobserver.models.mongo import MongoModel
from jobserver.models.process import Process
from jobserver.models.data_file import DataFile
from jobserver.models.data import BaseDataModel
from jobserver.util import load_script_func
from jobserver.errors import JobExecutionRestrictedError


class Job(MongoModel):
    collection = 'jobs'

    def __init__(self, created=None, started=None, finished=None,
                 result=None, **kwargs):
        super(Job, self).__init__()
        self.created = created
        self.started = started
        self.finished = finished
        self.result = result

        # set the remaining keyword arguments
        for key in kwargs.keys():
            setattr(self, key, kwargs[key])
            
    def update(self, data=None):
        self.edited = dt.utcnow()
        super(Job, self).update(data=data)

    def start(self):
        """Execute Job

        Starts the execution of this Job instance. The job will check any
        defined restrictions on job execution by checking the flask.g object
        for a user holding empty quota information. No user, a user without
        quota, a superuser or admin are assumed to be unrestricted.

        The data and process are loaded from the configured 'data' and
        'script' information. The Job execution itself is called in a new
        Thread that runs the Process.run method. After starting the thread,
        meta data about the data object and the Process class are stored into
        the Job instance and are persisted into the database.

        Returns
        -------
        void

        """
        # check, if the job execution is restricted
        self.check_restrictions()

        # load data
        data = self.load_input_data()

        # load the process
        process = self.load_process(data=data)

        # start the Process in a new Thread
        # TODO: here, I could use joblib memcache
        Thread(target=process.run).start()

        # store data information
        self.data = data.to_dict()

        # Process object
        process_dict = self.script
        if process_dict is None:
            process_dict = {}
        process_dict.update(process.to_dict())
        self.script = process_dict

        # save everything
        self.save()

    def check_restrictions(self):
        """Check Job availability

        In the standard configuration a job can only be executed if the user
        is a superuser or admin or if the user has a attribute 'job_quota' > 1,
        which will be decreased. If the passed user is None, API login is
        assumed to be turned off and the job execution is unlimited

        Parameters
        ----------
        user : User
            The user requesting to start the job.

        Returns
        -------
        None

        Raises
        ------
        error : JobExecutionRestrictedError
            In case the Job execution is restricted, this error will be raised.

        """
        # get the user
        user = getattr(g, 'user', None)
        # if no user is given, Job execution is not restricted
        if user is None:
            return None

        # superusers and admins are not restricted
        if user.role in ['superuser', 'admin']:
            return None

        # check if quota is deactivated for this user:
        if user.job_quota is None:
            return None

        # check if user has quota
        if user.job_quota is not None and user.job_quota >= 1:
            user.job_quota -= 1
            user.save()
            return None
        else:
            raise JobExecutionRestrictedError('No Job execution time left.')

    def on_error(self):
        """Error handler

        This error handler is used to handle the active user on job errors.
        As default behaviour any user with a configured quota will get an
        increase of 1 unit on his quota as the job errored.

        Returns
        -------
        None

        """
        # get user
        user = getattr(g, 'user', None)

        if user is not None and user.job_quota is not None:
            user.job_quota += 1
            user.save()

    def load_input_data(self):
        """Check input data and load model

        Will check if any of the valid data identifier are set on this Job
        instance. If found, the appropriate model class will be instantiated
        and returned.

        Returns
        -------
        data: BaseDataModel
            Returns an instance of BaseDataModel or inheriting class. It
            needs to have the BaseDataModel.read function defined.

        Notes
        -----
        The following attributes in the job instance will be recognized:

        * datafile: a DataFile instance of given name is instantiated
        * raw_data: a BaseDataModel with raw_data as content will be set

        It is also possible to set a 'data' attribute to Job, which has to be
        of type dict. Then, the dict needs the key 'type', which has to
        identify one of the types above. All other key:value pairs in the
        dict will be set to the Type class as keyword arguments.

        """
        if self.data is not None and isinstance(self.data, dict):
            # switch type
            if self.data.get('type') == 'datafile':
                return DataFile(
                    **{k: v for k, v in self.data.items() if k != 'type'}
                )
            elif self.data.get('type') == 'raw_data':
                return BaseDataModel(
                    **{k: v for k, v in self.data.items() if k != 'type'}
                )
            else:
                ValueError('Data Type %s is not known.'
                           % self.data.get('type', 'NotSet'))

        elif self.datafile is not None:
            return DataFile.get_from_name(self.datafile)

        elif self.raw_data is not None:
            return BaseDataModel(data=self.raw_data)

        else:
            raise ValueError('No data-like setting found on this Job.')

    def load_process(self, data):
        """Check script settings and load

        The specified script settings will be checked and then the
        function/file/eval content will be loaded to be passed to the Process
        as soon as the Job is started.

        Parameters
        ----------
        data : BaseDataModel
            Instance of BaseDataModel or inheriting. Will be bound to the
            Process. The Process will pass the data down to the loaded
            function. This way, a custom Process class can handle data
            differently for its respective types of functions.

        Returns
        -------
        process : Process
            Process instance. The job start method will execute the Process.run
            method in an extra Thread.

        Notes
        -----

        The script attributes can be specified in the script property of the
        Job instance. The general form is:

        .. code-block:: json

            {
                "script": {
                    "type": "function",
                    "name": "func_name",
                    "args": [],
                    "kwargs": {}
                }
            }

        All settings except 'name' show default values and can be omitted. As
        of this writing, other values are not supported. In case only the
        script name shall be specified, the "script_name" property can be
        used over the "script" dictionary.

        """
        # script was defined
        if self.script is not None and isinstance(self.script, dict):
            # switch script type
            if self.script.get('type', 'function') == 'function':
                # use the correct class
                ProcessClass = Process

                # load the function
                func = load_script_func('scripts', self.script['name'])
#                    self.script.get('module', 'scripts'),
#                    'scripts',
#                    self.script['name']
#                )

            elif self.script.get('type', 'function') == 'file':
                raise NotImplementedError(
                    'File Processes are not supported yet'
                )
            elif self.script.get('type', 'function') == 'eval':
                raise NotImplementedError(
                    'Eval Processes are not supported yet'
                )
            else:
                raise ValueError('Script Type %s is not known.'
                                 % self.script.get('type', 'NotSet'))

            # return the Process instance
            return ProcessClass(
                f=func,
                data=data.read(),
                args=self.script.get('args', []),
                kwargs=self.script.get('kwargs', {}),
                job=self
            )

        # script_name shortcut used
        elif self.script_name is not None:
            return Process(
                load_script_func('scripts', self.script_name),
                data.read(),
                args=[],
                kwargs={},
                job=self
            )

        # no script set
        else:
            raise ValueError('No script to process was specified')

    def create(self):
        if self.created is None:
            self.created = dt.utcnow()

        super(Job, self).create()
