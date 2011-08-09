# $Id:$

# Determine the command used to start Python.  This will be the
# shell's Python unless the variable ${PYTHON} is set.
ifndef PYTHON
	PYTHON=python
endif

# Command for running management tool.
MANAGE=${PYTHON} manage.py

# Prepares existing .po for localizations and compiles them
# Public domain
# To make first time localization (for example for de_DE) run
# $ python manage.py makemessages -e ".html,.txt" -l de_DE
int :
	${MANAGE} makemessages -e ".html,.txt,.py" --all
	${MANAGE} compilemessages

# Handle schema migration for all applications.
schemamigration :
	for i in `find apps -type d -depth 1 -print`; \
	do \
	  echo `basename $$i`; \
	  ${PYTHON} ./manage.py schemamigration `basename $$i` --auto; \
	done

# Synchronize the database.
syncdb :
	${PYTHON} manage.py syncdb --noinput
	for i in `find apps -type d -depth 1 -print`; \
	do \
	  echo `basename $$i`; \
	  ${PYTHON} ./manage.py migrate `basename $$i`; \
	done

# Tidy up by removing .pyc files.
tidy :
	rm -f `find . -name '*.pyc'`

# Display the settings.
settings :
	echo "PYTHON:" ${PYTHON}
