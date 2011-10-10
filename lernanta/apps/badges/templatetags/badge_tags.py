from django import template


register = template.Library()


def give_badge_action(project, peer):
    project_badges = project.get_project_badges(
        only_peer_community=True)
    context = {'badges': project_badges, 'peer': peer}
    return context

register.inclusion_tag('badges/_give_badge_action.html')(
    give_badge_action)
