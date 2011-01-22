========
Batucada
========

Batucada is a ground up rewrite of drumbeat.org in `Django`_. 

.. _Django: http://www.djangoproject.com/

Installation
------------

To install Batucada, you must clone the repository: ::

   git clone git://github.com/paulosman/batucada.git

To get started, you'll need to make sure that ``virtualenv`` and ``pip`` are installed. ::

   sudo easy_install virtualenv
   sudo easy_install pip

You'll also need to have mysql installed (mysql-client, mysql-server, libmysqlclient-dev).  

I recommend using ``virtualenvwrapper`` to manage your virtual environments. Follow the `installation instructions`_. Once installed, create your virtual environment for ``batucada`` and install the dependencies ::

   cd batucada
   mkvirtualenv batucada 
   workon batucada
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

There's a problem with real databases (read: not sqlite) where south migrations are run in an order that violates foreign key constraints. See `Bug # 623612`_ for details. Until that is fixed, you're best off running migrations in this order. ::

   python manage.py migrate projects
   python manage.py migrate users
   python manage.py migrate activity
   python manage.py migrate statuses
   python manage.py migrate links
   python manage.py migrate dashboard

What a pain! 

.. _Bug # 623612: https://bugzilla.mozilla.org/show_bug.cgi?id=623612

Finally, start the development server to take it for a spin. ::

   python manage.py runserver 

Get Involved
------------

To help out with batucada, join the `Drumbeat mailing list`_ and introduce yourself. We're currently looking for help from Django / Python and front-end (HTML, CSS, Javascript) developers. 

.. _Drumbeat mailing list: http://www.mozilla.org/about/forums/#drumbeat-website
