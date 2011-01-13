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

I recommend using ``virtualenvwrapper`` to manage your virtual environments. Follow the `installation instructions`_. Once installed, create your virtual environment for ``batucada`` and install the dependencies ::

   cd batucada
   mkvirtualenv batucada 
   workon batucada
   pip install -r requirements/compiled.txt
   pip install -r requirements/prod.txt

.. _installation instructions: http://www.doughellmann.com/docs/virtualenvwrapper/

If you are doing an update, you might find it helps to delete pyc files: ::

    find . -name "*.pyc" | xargs rm

You should create a settings_local.py. Most people will be able to get away with the template provided. ::

   cp settings_local.dist.py settings_local.py

Next, sync the database and run migrations. ::

   python manage.py syncdb --noinput 
   python manage.py migrate

Finally, start the development server to take it for a spin. ::

   python manage.py runserver 

Get Involved
------------

To help out with batucada, join the `Drumbeat mailing list`_ and introduce yourself. We're currently looking for help from Django / Python and front-end (HTML, CSS, Javascript) developers. 

.. _Drumbeat mailing list: http://www.mozilla.org/about/forums/#drumbeat-website
