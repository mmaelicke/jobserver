"""
Main Job model class. This class handles CRUD operations on the MongoDB
instance to manage the Jobs.

A Job is a descriptive model of a user starting a script, monitoring the
execution and viewing the results.
"""
from threading import Thread
from datetime import datetime as dt

from jobserver.models.mongo import MongoModel
from jobserver.models.process import Process
from jobserver.models.data_file import DataFile
from jobserver.models.data import BaseDataModel
from jobserver.app import scripts
from jobserver.util import load_script_func


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
        # This is heavy development
#        summary = getattr(scripts, 'summary')

        # load data
        data = self.load_input_data()

        # load the process
        proc = self.load_process(data=data)
#        # set empty args
#        args = []

#        proc = Process(summary, data.read(), args, kwargs=dict(), job=self)
        # if no exceptions occured, start the Thread
        Thread(target=proc.run).start()

#        # DEV
#        # after process started, save the settings
#        self.scipt_name = 'timeseries'
#        self.process_name = 'summary'
#        self.process_args = args
        # As the Thread started, save the data and process object
        self.data = data.to_dict()

        # Process object
        proc_dict = self.script
        if proc_dict is None:
            proc_dict = {}
        proc_dict.update(proc.to_dict())
        self.script = proc_dict

        # save everything
        self.save()

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
