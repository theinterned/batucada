# Prepares .po for localizations and compiles them
# Public domain

for lang in $l; do
	echo $lang;
	django-admin.py makemessages -e ".html,.txt" -l $lang
done;
django-admin.py compilemessages
