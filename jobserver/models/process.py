"""
Main model class for handling a process
"""
from datetime import datetime as dt

import pandas as pd


class Process:
    def __init__(self, f, data, args, kwargs, job):
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
            output = self.f(self.data, *self.args, **self.kwargs)
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

    def to_dict(self):
        return {
            'name': self.f.__name__,
            'args': self.args,
            'kwargs': self.kwargs
        }
