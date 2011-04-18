=========
Lernanta
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

Next, you'll need to install ``virtualenv`` and ``pip`` if you don't already have them.  Using `virtualenvwrapper`_ is also recommended. ::

   sudo easy_install virtualenv
   sudo easy_install pip
   pip install virtualenvwrapper
   
Be sure to configure your shell so that pip knows where to find your virtual environments: ::

   # in .bashrc or .bash_profile
   export WORKON_HOME=$HOME/.virtualenvs
   export PIP_VIRTUALENV_BASE=$WORKON_HOME
   export PIP_RESPECT_VIRTUALENV=true
   source /usr/local/bin/virtualenvwrapper.sh

.. _virtualenvwrapper: http://www.doughellmann.com/docs/virtualenvwrapper/

Once installed, create your virtual environment for ``lernanta`` and install the dependencies. There's a chance that packages listed in ``requirements/compiled.txt`` won't install cleanly if your system is missing some key development libraries. For example, lxml requires ``libxml2-dev`` and ``libxslt-dev``. These should be available from your system's package manager. ::

   cd lernanta
   mkvirtualenv --no-site-packages lernanta 
   workon lernanta
   pip install -r requirements/compiled.txt
   pip install -r requirements/prod.txt
   pip install -r requirements/dev.txt
   
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

Get Involved
------------

To help out with lernanta, join the `P2PU dev mailing list`_ and introduce yourself. We're currently looking for help from Django / Python and front-end (HTML, CSS, Javascript) developers. 

.. _P2PU dev mailing list: http://lists.p2pu.org/mailman/listinfo/p2pu-dev

Setup in Production with Apache and WSGI
------------

Configure a new virtualhost for the site ::

    vim /etc/apache2/sites-available/lernanta

This is an example of configuration (replace the values between brackets) ::

    <VirtualHost *:80>
        ServerAdmin webmaster@localhost
        ServerName [domain]
        ErrorLog /var/log/apache2/lernanta-error.log

        # Possible values include: debug, info, notice, warn, error, crit,
        # alert, emerg.
        LogLevel warn
        CustomLog /var/log/apache2/lernanta-access.log combined

        # run mod_wsgi process for django in daemon mode
        # this allows avoiding confused timezone settings when
        # another application runs in the same virtual host
        WSGIDaemonProcess Lernanta
        WSGIProcessGroup Lernanta

        # force all content to be served as static files
        # otherwise django will be crunching images through itself wasting time
        Alias /media/ "[path to the source code]/media/"
        <Directory "[path to the source code]/media">
            Order deny,allow
            Allow from all
            Options Indexes MultiViews FollowSymLinks
            AllowOverride None
        </Directory>

        Alias /en/admin-media/ "[path to the virtualenv]/lib/python2.6/site-packages/django/contrib/admin/media/"
        <Directory "[path to the virtualenv]/lib/python2.6/site-packages/django/contrib/admin/media">
            Order deny,allow
            Allow from all
            Options Indexes MultiViews FollowSymLinks
            AllowOverride None
        </Directory>

        #this is your wsgi script described in the prev section
        WSGIScriptAlias / [path to the source code]/wsgi/batucada.wsgi
    </VirtualHost>

Add the necessary paths to sitedir (replace the values between brackets) ::

   site.addsitedir(os.path.abspath(os.path.join(wsgidir, '[path to the virtualenv]/lib/python2.6/site-packages')))
   site.addsitedir(os.path.abspath(os.path.join(wsgidir, '[path to the virtualenv]/src')))

Reload apache ::

   /etc/init.d/apache reload

Update the Site instance's domain from the admin interface and configure your SUPERFEEDR username and password (now in settings.py, but soon in settings_local.py).

Configure email settings (DEFAULT_FROM_EMAIL, EMAIL_HOST, EMAIL_HOST_PASSWORD, EMAIL_HOST_USER) and the email backend ::

   EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

If you have to update the source code in production, remember to mark the .wsgi file as updated ::

   touch wsgi/batucada.wsgi

