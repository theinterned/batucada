from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q

from projects.models import Project
from signups.models import Signup
from learn.models import add_course_listing
from learn.models import update_course_listing
from learn.models import create_list
from learn.models import add_course_to_list


class Command(BaseCommand):
    args = '<poll_id poll_id ...>'
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        listed = Project.objects.filter(
            not_listed=False,
            deleted=False,
            archived=False,
            under_development=False,
            test=False
        )

        listed = listed.filter(
            Q(category=Project.CHALLENGE)
            | Q(sign_up__status=Signup.MODERATED)
            | Q(sign_up__status=Signup.NON_MODERATED)
        )

        for project in listed:
            project_tags = project.tags.all().values_list('name', flat=True)
            args = dict(
                course_url = "http://p2pu.org/en/groups/{0}/".format(project.slug),
                title = project.name,
                description = project.short_description,
                data_url = "https://p2pu.org/en/groups/{0}/data".format(project.slug),
                language = project.language,
                thumbnail_url = "http://p2pu.org{0}".format(project.get_image_url()),
                tags = project_tags
            )
            try:
                add_course_listing(**args)
            except:
                update_course_listing(**args)

        # create lists
        create_list('community', "Community Picks", "")
        create_list('showcase', "Showcased", "")

        for project in listed.filter(community_featured=True):
            course_url = "http://p2pu.org/en/groups/{0}/".format(project.slug)
            add_course_to_list(course_url, 'community')

        for project in listed.filter(featured=True):
            course_url = "http://p2pu.org/en/groups/{0}/".format(project.slug)
            add_course_to_list(course_url, 'showcase')

