from django import template

register = template.Library()


def join_p2pu(request):
    display_join_p2pu = not request.user.is_authenticated()
    if not display_join_p2pu:
        request.session['mark_registered'] = True
    elif 'mark_registered' in request.session:
        display_join_p2pu = False
    return {'display_join_p2pu': display_join_p2pu}

register.inclusion_tag('dashboard/_join_p2pu.html')(join_p2pu)
