"""
General
-------
The scripts module will be imported on application startup. All available
tools can be imported here. Any content necessary can be located in a
submodule of scripts. Any connecting function, that will be processed by the
default Process class, should accept the data as first argument, followed by
various args and kwargs. All of the imports will be specified in the Job
instance and can be of any JSONifyable type.
The output should preferably be a pandas.DataFrame, pandas.Series,
numpy.ndarray or a plain text.

Notes
-----

It is also possible to import functions from third python packages. Then,
these packages have to be importable by the Python environment running the
Flask server, or they have to be installable by pip and be defined in the
requirements.txt upon setup.

In case a process needs some kind of warmup, a warmup-function call can be
added to the on_init function. That function will be called, after the Flask
app will be fully initialized. That means, that all the database connections
used by the application and all of its routes are already bound to the
application.

"""
# the process import go here
from .timeseries import summary


# call your warm-up functions in the on_init function
def on_init(flask_app):
    pass
