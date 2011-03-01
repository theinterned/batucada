=========
Learnanta
=========

Lernanta is the new platform for P2PU. We are building on the codebase from
Batucada, a rewrite of drumbeat.org by Mozilla. 

.. _Django: http://www.djangoproject.com/


Get Involved
------------

Interested in getting involved in Lernanta code development? Check out the development wiki [0] for more info! For a broader view on the development and tech team at P2PU, check out the P2PU Development and Tech team [1] page on the P2PU wiki [2] . 

[0] https://github.com/p2pu/lernanta/wiki
[1] http://wiki.p2pu.org/w/page/31978748/Development-and-tech-team
[2] http://wiki.p2pu.org

Installation
------------

You need a few prerequisites ::

   sudo apt-get install python-setuptools python-dev build-essential

You'll also need to have mysql installed (mysql-client, mysql-server, libmysqlclient-dev).

To install Lernanta, you must clone the repository: ::

   git clone git://github.com/p2pu/lernanta.git

If you're planning on contributing back to the project, `fork the repository`_ instead in the usual GitHub fashion.

.. _fork the repository: http://help.github.com/forking/

Next, you'll need to install ``virtualenv`` and ``pip`` if you don't already have them: ::

   sudo easy_install virtualenv
   sudo easy_install pip
   
Using ``virtualenvwrapper`` is also recommended (see the `installation instructions`_). Be sure to configure your shell so that pip knows where to find your virtual environments: ::

   # in .bashrc or .bash_profile
   export WORKON_HOME=$HOME/.virtualenvs
   export PIP_VIRTUALENV_BASE=$WORKON_HOME
   export PIP_RESPECT_VIRTUALENV=true
   source /usr/bin/virtualenvwrapper.sh

.. _installation instructions: http://www.doughellmann.com/docs/virtualenvwrapper/

Once installed, create your virtual environment for ``lernanta`` and install the dependencies ::

   cd lernanta
   mkvirtualenv --no-site-packages lernanta 
   workon lernanta
   pip install -r requirements/compiled.txt
   pip install -r requirements/prod.txt
   pip install -r requirements/dev.txt

There's a chance that packages listed in ``requirements/compiled.txt`` won't install cleanly if your system is missing some key development libraries. For example, lxml requires ``libxsml2-dev`` and ``libxslt-dev``. These should be available from your system's package manager.
   
To be extra sure you're working from a clean slate, you might find it helps to delete ``.pyc`` files: ::

    ./rmpyc

Create a ``settings_local.py`` based on the template provided in the checkout. Edit the database parameters as needed ::

   cp settings_local.dist.py settings_local.py

If the mysql database doesn't exist yet, create it. ::

   mysqladmin -u <user> -p create <database name>
 
Next, sync the database and run migrations. ::

   python manage.py syncdb --noinput --all

Finally, start the development server to take it for a spin. ::

   python manage.py runserver 

To run the test framework. ::

   python manage.py test

To recreate the test database before running the tests. ::

   FORCE_DB=True python manage.py test

After updating a database model you will have to make a migration for the change, then apply it. ::

   python manage.py schemamigration <appname> --auto
   python manage.py migrate <appname>
