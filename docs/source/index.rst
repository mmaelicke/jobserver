=========
Jobserver
=========

Jobserver is a Flask application, which is serving Python functions and scripts
over an RESTful server interface.

Each processing instance is called a *Job* and can be freely configured.
Before the Jobserver can start the execution of Code, information on the
Python function to load and run has to be specified as a Job property.
Usually, information about the data to be used needs to be specified as well.
Beyond that, a Job instance can take almost any information that is JSON
serializable.

The first draft of the application uses MongoDB as a database Backend. The
main advantage is, that as a NoSQL system it does not require a predefined
data model. That means, it can capture almost any algorithm parameters and
algorithm output and save it as is. This saved content is directly usable and
searchable. In a relational system we would have to either implement all
possible outputs and parameters and therefore normalize them, or store them
as JSON strings, which would not be searchable.

That said, you need to install MongoDB locally and run it with default
settings. The other possible soultion is to connect to a Cloud MongoDB
instance, like `MongoDB Atlas <https://www.mongodb.com/cloud/atlas>`_.
It's not really fast and you have just 512 MB on the free plan.

.. toctree::
    :maxdepth: 2
    :caption: Contents:

    installation
    workflow
    usage
