============
Installation
============

Jobserver needs Python 3.5 or higher. Jobserver is only available on Github
as of this writing.


Create an environment
=====================

It is highly recommended to use
Anaconda for managing your Python installations. A new environment for the
enigma project could be created like:

.. code-block:: bash

    conda create -n jobserver python=3.6 ipython numpy pandas flask dnspython

.. note::

    It is recommended to install all available dependencies for jobserver via
    conda, as you will find pandas or numpy installations to be way easier,
    than using pip only. The jobserver itself is not (yet) available on pypi.


Activate the conda environement (if you build it like shown above):

Linux / macOS:

.. code-block:: bash

    source activate jobserver

Windows:

.. code-block:: bash

    activate jobserver


Get the files
=============

Then clone the repository:

.. code-block:: bash

    git clone https://github.com/mmaelicke/jobserver.git
    cd jobserver
    pip install -r requirements.txt
    python setup.py install

There is no automatic installation script so far, therefore a few changes are
necessary. Above all, the Flask server needs a valid configuration to run.
There is a ``config.default`` file in the ``jobserver`` subfolder. Basically,
this has to be copied and renamed to ``config.py`` and the jobserver will
technically run.

.. code-block:: bash

    cp config.default config.py

It assumes to find a MongoDB on localhost, standard port 27017.

Configuration
=============

The only thing that will not work is the e-mail service. You will have to add
valid information into the Config object. The code example below shows the
important part of the then created ``config.py``.

.. code-block:: python

    class Config:
        [...]
        MAIL_SERVER = 'smtp.yourserver.com'
        MAIL_PORT = 587
        MAIL_USERNAME = 'username'
        MAIL_PASSWORD = 'password'
        MAIL_DEFAULT_SENDER = 'registration@yourserver.com'


In case you are not using a local MongoDB instance, you can use any
connection string suported by pymongo. This way you can also connect to cloud
MongoDB instances, like MongoDB Atlas. Jobserver can handle the old style
driver version (up to 3.4) and new style driver version (from 3.6 on)
connection strings.

.. danger::

    In both cases, the connection will contain your password in plain text.
    Therefore the ``config.py`` is by default listed in the ``.gitignore``.
    Make sure that the config files is kept private!

In order to switch the server instance, you have to change a line in
``jobserver/config.py``.

.. code-block:: python

    class Config:
        [...]
        MONGO_URI = "mongodb://localhost:27017/enigma"

Then, you'll have to replace the connection string with the one served on
MongoDB Atlas. It can be found in the connection settings.

.. note::

    In case you are planning to run jobserver as a Google App Engine, you'll
    need to use the old styled connection strings to reach a MongoDB instance
    outside of the Gloogle Cloud World. For AWS I couldn't successfully
    connect so far.
