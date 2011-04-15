# Prepares existing .po for localizations and compiles them
# Public domain
# To make first time localization (for example for de_DE) run
#     django-admin.py makemessages -e ".html,.txt" -l de_DE

l=`(cd locale; ls)`
for lang in $l; do
	django-admin.py makemessages -e ".html,.txt" -l $lang
done;
django-admin.py compilemessages
