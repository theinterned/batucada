========
Batucada
========

Batucada is a ground up rewrite of drumbeat.org in `Django`_. 

.. _Django: http://www.djangoproject.com/

Installation
------------

To install Batucada, you must clone the repository: ::

   git clone git://github.com/paulosman/batucada.git

Next, create a virtual environment and install dependencies. ::

   pip install virtualenvwrapper
   mkvirtualenv batucada 
   pip install -f requirements.txt 

Finally, sync the database and start the development server. ::

   python manage.py syncdb --noinput 
   python manage.py runserver 

Get Involved
------------

To help out with batucada, join the `Drumbeat mailing list`_ and introduce yourself. We're currently looking for help from Django / Python and front-end (HTML, CSS, Javascript) developers. 

.. _Drumbeat mailing list: https://lists.mozilla.org/listinfo/community-drumbeat
