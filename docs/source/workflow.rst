====================
Application workflow
====================

Job
===

I have set some definitions in order to be able to model a proper workflow.
We have the actual algorithm, that shall be exposed by Jobserver. These
algorithms can be a Python function, Python script or even any kind of
command line tool. Here we call these algortihms **scripts**.

In the App, a *script* is run by unit called **Process**. There will be
different Process instance, e.g. a Process running a Python function, a
Process operating multicore, a Process running a file and capturing the
output etc.

In case a user wants to start a *Process*, he is creating a **Job**. One Job is
bound to the processing of one single *Process*, so far. But pipelined
scripts executed by a single Job instance is planned for the future.
Jobs do also manage the *Process* parameters and authentication. This way,
the number of Jobs (simultaneously or total, whatever you need) can be limited
by User, if needed. Once a *Process* has finished, the Job will also include
the output. In short: a job collects all the information needed to make a
algorithm model run reproducible, while not exposing any detail about the
algorithm itself. That means Jobs can public, even for restricted code.

Binding data to a Job
---------------------

The Jobserver implements different types of data that are handled in
different ways. This does not model the type of the actual data, like
time series, areal photo and so on, but the way the data is stored.

* **DataFile [type='datafile']** are files that are actually stored on the
  filesystem. The User can set a DataFile by name that is already there or
  he has just uploaded. In a productive version, this could be used for example
  for public files.

* **Data on MongoDB [type='mongodb']** is a data model that represents data,
  which is stored in the MongoDB. It can be any data that is JSON
  serializable. It is further described by a ``datatype`` property, which
  handles the conversion into the correct Python data structure, before being
  passed to the script.

* **Data on the Fly [type='raw_data']** is defined as a Job property. It can
  be of any JSON serializable type. This is usually used in case the data is
  highly specific to the script, or the user is in development process.



Binding a Process to a Job
--------------------------

Any algorithm that is run on the server is represented by a *Process*.
Jobserver offers different Processes, not all are tested so far.

* **Process [type='function']** as the base class of all Processes, that will
  run an importable function with given parameter and pre-loaded data.

* **FileProcess [type='file']** will behave much like the base class, but run
  an executable file from the file system. All requirements for this file
  have to be matched. The STDOUT and STDERR will be cached and bound to the
  Job as result. The *FileProcess* is not limited to Python files.

* **EvalProcess [type='eval']** takes raw Python code as input and will run
  that code with the bound data pre-loaded. **Note**, this Eval will have
  access to the server and should be limited to superusers.

As of this writing, only the base *Process* is tested.


DataFile
========

.. note::

    DataFile are development only. They should not be implemented as is into
    a productive environment. Beforehand, they would need to be bound on user
    level and some kind of permission model.

A DataFile unit represents an actual file in the data subfolder of Jobserver.
Only files of registered file extensions will be recognized as a DataFile.
The model can return meta data about one or all files, read the content of
the file and pass it to a Job instance, upload new files or delete existing
files. It is controlled by the *datafile* and *datafiles* endpoints.
One scenario of implementing DataFiles into a productive system could be
temporary files allowing the users to upload data and test it, before passing
it to the database. If used this way, you'll have to implement a control on
the upload and size of this folder on the server side, as Jobserver will just
save anything of allowed file extension the user uploads.
