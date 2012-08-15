from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count

from tags.models import GeneralTaggedItem
from projects.models import Project


def get_active_languages():
    """ Return a list of the active language currently in use """
    language_list = Project.objects.all().values_list('language').distinct('language')
    language_dict = dict(settings.LANGUAGES)
    languages = [(l[0], language_dict[l[0]],) for l in language_list]
    return languages


def search(keyword, limit = 10):
    """ a simple 1 word search for courses, will match partial name
        or any tag.
    """
    results = []
    results += Project.objects.filter(name__icontains=keyword)[:limit]
    results += get_tagged_projects(keyword)[:limit]
    return list(set(results))[:limit]


def get_listed_projects():
    """ return all the projects that should be listed """
    listed = Project.objects.filter(
        not_listed=False,
        deleted=False,
        archived=False,
        under_development=False,
        test=False)
    return listed


def get_popular_tags(max_count=10):
    ct = ContentType.objects.get_for_model(Project)
    listed = list(get_listed_projects().values_list('id', flat=True))
    return GeneralTaggedItem.objects.filter(
        content_type=ct, object_id__in=listed).values(
        'tag__name').annotate(tagged_count=Count('object_id')).order_by(
        '-tagged_count')[:max_count]


def get_weighted_tags(min_count=2, min_weight=1.0, max_weight=7.0):
    ct = ContentType.objects.get_for_model(Project)
    listed = get_listed_projects().values('id')
    tags = GeneralTaggedItem.objects.filter(
        content_type=ct, object_id__in=listed).values(
        'tag__name').annotate(tagged_count=Count('object_id')).filter(
        tagged_count__gte=min_count)
    if tags.count():
        min_tagged_count = tags.order_by('tagged_count')[0]['tagged_count']
        max_tagged_count = tags.order_by('-tagged_count')[0]['tagged_count']
        if min_tagged_count == max_tagged_count:
            factor = 1.0
        else:
            factor = float(max_weight - min_weight) / float(max_tagged_count - min_tagged_count)
    tags = tags.order_by('tag__name')
    for tag in tags:
        tag['weight']  = max_weight - (max_tagged_count - tag['tagged_count']) * factor
    return tags


def get_tagged_projects(tag_name, projects=None):
    ct = ContentType.objects.get_for_model(Project)
    items = GeneralTaggedItem.objects.filter(
        content_type=ct, tag__name=tag_name).values(
        'object_id')
    if not projects:
        projects = Project.objects
    return projects.filter(id__in=items)

