========
Batucada
========

Batucada is a ground up rewrite of drumbeat.org in `Django`_. 

.. _Django: http://www.djangoproject.com/

Installation
------------

To install Batucada, you must clone the repository: ::

   git clone git://github.com/paulosman/batucada.git

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

Now create a virtual environment for ``batucada`` and install its dependencies: ::

   cd batucada
   mkvirtualenv --no-site-packages batucada
   workon batucada
   pip install -r requirements/compiled.txt
   pip install -r requirements/prod.txt

Substitute ``requirements/prod.txt`` with ``requirements/dev.txt`` if you'll be doing development. It includes a few extra packages related to testing and debugging.

There's a chance that packages listed in ``requirements/compiled.txt`` won't install cleanly if your system is missing some key development libraries. For example, lxml requires ``libxsml2-dev`` and ``libxslt-dev``. These should be available from your system's package manager.
   
To be extra sure you're working from a clean slate, you might find it helps to delete ``.pyc`` files: ::

    find . -name "*.pyc" | xargs rm

Create a ``settings_local.py`` based on the template provided in the checkout. Edit the database parameters as needed ::

   cp settings_local.dist.py settings_local.py

Now sync the database and run migrations. ::

   python manage.py syncdb --noinput 

There's a problem with real databases (read: not sqlite) where south migrations are run in an order that violates foreign key constraints. See `Bug # 623612`_ for details. Until that is fixed, you're best off running migrations in this order. ::

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

Get Involved
------------

To help out with batucada, join the `Drumbeat mailing list`_ and introduce yourself. We're currently looking for help from Django / Python and front-end (HTML, CSS, Javascript) developers. 

.. _Drumbeat mailing list: http://www.mozilla.org/about/forums/#drumbeat-website
