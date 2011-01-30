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

To install Lernanta, you must clone the repository: ::

   git clone git://github.com/p2pu/lernanta.git

To get started, you'll need to make sure that ``virtualenv`` and ``pip`` are installed. ::

   sudo easy_install virtualenv
   sudo easy_install pip

You'll also need to have mysql installed (mysql-client, mysql-server, libmysqlclient-dev).  

I recommend using ``virtualenvwrapper`` to manage your virtual environments. Follow the `installation instructions`_. 
Once installed, create your virtual environment for ``lernanta`` and install the dependencies ::

   cd lernanta
   mkvirtualenv lernanta 
   workon lernanta
   pip install -r requirements/compiled.txt
   pip install -r requirements/prod.txt
   pip install -r requirements/dev.txt

.. _installation instructions: http://www.doughellmann.com/docs/virtualenvwrapper/

If you are doing an update, you might find it helps to delete pyc files: ::

    find . -name "*.pyc" | xargs rm

You should create a settings_local.py. Most people will be able to get away with the template provided. ::

   cp settings_local.dist.py settings_local.py

If the mysql database doesn't exist yet, create it:

   mysqladmin -u <user> -p create <database name>
 
Next, sync the database and run migrations. ::

   python manage.py syncdb --noinput 

There's a problem with real databases (read: not sqlite) where south migrations are run in an order that violates 
foreign key constraints. See `Bug # 623612`_ for details. Until that is fixed, you're best off running migrations 
in this order. ::

   python manage.py migrate projects
   python manage.py migrate users
   python manage.py migrate activity
   python manage.py migrate statuses
   python manage.py migrate links
   python manage.py migrate dashboard
   python manage.py migrate relationships

What a pain! 

.. _Bug # 623612: https://bugzilla.mozilla.org/show_bug.cgi?id=623612

Finally, start the development server to take it for a spin. ::

   python manage.py runserver 

To run the test framework. ::

   python manage.py test

To recreate the test database before running the tests. ::

   FORCE_DB=True python manage.py test

