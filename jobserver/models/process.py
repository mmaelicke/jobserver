"""
Main model class for handling a process
"""
from datetime import datetime as dt
import subprocess

import pandas as pd

from jobserver.errors import CodeBlockMissingError

class Process:
    def __init__(self, f, data, args, kwargs, job):
        self.type = 'function'
        self.f = f
        self.data = data
        self.args = args
        self.kwargs = kwargs
        self.job = job

    def run(self):
        """Run this tool

        Returns
        -------

        """
        # set the start date
        self.job.started = dt.utcnow()
        self.job.save()
        print('Process started')

        # run
        try:
            output = self._run()
        except Exception as e:
            print('Process errored')
            self.job.error = True
            self.job.message = str(e)
            self.job.save()
            self.job.on_error(user=self.job.user)
            return None

        if isinstance(output, pd.DataFrame):
            output = output.to_dict()

        # finished
        self.job.finished = dt.utcnow()
        self.job.time_sec = (self.job.finished -
                             self.job.started).total_seconds()
        self.job.result = output
        self.job.save()
        print('Process finished')
        return None

    def _run(self):
        return self.f(self.data, *self.args, **self.kwargs)

    def to_dict(self):
        return {
            'name': self.f.__name__,
            'type': self.type,
            'args': self.args,
            'kwargs': self.kwargs
        }


class EvalProcess(Process):
    def __init__(self, code, data, args, kwargs, job):
        if callable(code):
            raise CodeBlockMissingError('An EvalProcess needs a python '
                                        'keyword configured.')
        else:
            self.codeblock = code

        # call parent init method
        super(EvalProcess, self).__init__(None, data, args, kwargs, job)
        self.type = 'eval'

    def _run(self):
        return eval(
            self.codeblock, 
            {
                'data': self.data,
                'job': self.job
            }, 
            {**self.kwargs}
        )
    
    
class FileProcess(Process):
    def __init__(self, filename, data, args, kwargs, job):
        self.filename = filename
        
        # call parent init method
        super(FileProcess, self).__init__(None, data, args, kwargs, job)
        self.type = 'file'

    def _run(self):
        process_result = subprocess.run(
            [self.filename, self.data, *self.args],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # check if an error occured
        if process_result.stderr != b'':
            raise RuntimeError(process_result.stderr.decode())
        else:
            return process_result.stdout.decode()
