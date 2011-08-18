from django import template

from schools.models import School


register = template.Library()


def schools_menu():
    schools = School.objects.all()
    return {'schools': schools}


register.inclusion_tag('schools/menu.html')(schools_menu)
