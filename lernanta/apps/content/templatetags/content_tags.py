from django import template
from django.template.loader import render_to_string

from content.forms import TaskLinkSubmitForm, TaskBadgeApplyForm
from content.models import Page
from replies.models import PageComment
from projects.models import PerUserTaskCompletion
from badges.models import Badge, Submission, Award


register = template.Library()


def task_toggle_completion(request, page, ignore_post_data=False):
    project = page.project
    total_count = Page.objects.filter(project__slug=project.slug, listed=True,
        deleted=False).count()
    ajax_data = {
        'upon_completion_redirect': page.project.get_absolute_url(),
        'total_count': total_count,
    }
    progressbar_value = 0
    task_completion = None
    next_badge = None
    is_last_badge = True
    task_link_submit_form = None
    task_badge_apply_form = None
    badges_to_apply = list(page.badges_to_apply.order_by('id'))
    if request.user.is_authenticated():
        profile = request.user.get_profile()
        ajax_data['completed_count'] = PerUserTaskCompletion.objects.filter(
            page__project__slug=project.slug, page__deleted=False,
            unchecked_on__isnull=True, user=profile).count()
        if total_count:
            progressbar_value = (ajax_data['completed_count'] * 100 / total_count)
        try:
            task_completion = PerUserTaskCompletion.objects.filter(
                user=profile, page=page, unchecked_on__isnull=True)[0]
        except IndexError:
            pass
        if badges_to_apply and task_completion:
            next_badge, is_last_badge = page.get_next_badge_can_apply(profile)
            if not task_completion.url:
                if not ignore_post_data and request.method == 'POST':
                    task_link_submit_form = TaskLinkSubmitForm(bool(next_badge), request.POST,
                        instance=task_completion)
                    if task_link_submit_form.is_valid():
                        task_completion = task_link_submit_form.save()
                        if task_link_submit_form.cleaned_data['post_link']:
                            link_comment_content = render_to_string(
                                "content/_post_link_comment.html",
                                {'url': task_completion.url})
                            link_comment = PageComment(content=link_comment_content,
                                author=profile, page_object=page, scope_object=page.project)
                            link_comment.save()
                            ajax_data['posted_link_comment_html'] = render_to_string(
                                'replies/_comment_threads.html', {'comments': [link_comment],
                                'is_challenge': True, 'user': request.user}).strip()
                        if task_link_submit_form.cleaned_data.get('apply_for_badges', False) and next_badge:
                            task_badge_apply_form = TaskBadgeApplyForm(
                                initial={'badge_slug': next_badge.slug})
                        task_link_submit_form = None
                else:
                    task_link_submit_form = TaskLinkSubmitForm(
                        show_badge_apply_option=bool(next_badge))
            elif not ignore_post_data and next_badge and request.method == 'POST':
                task_badge_apply_form = TaskBadgeApplyForm(request.POST)
                if task_badge_apply_form.is_valid():
                    try:
                        badge = page.badges_to_apply.get(slug=task_badge_apply_form.cleaned_data['badge_slug'])
                        submission = task_badge_apply_form.save(commit=False)
                        submission.url = task_completion.url
                        submission.badge = badge
                        submission.author = profile
                        submission.save()
                        next_badge, is_last_badge = page.get_next_badge_can_apply(profile)
                        if next_badge:
                            task_badge_apply_form = TaskBadgeApplyForm(
                                initial={'badge_slug': next_badge.slug})
                        else:
                            task_badge_apply_form = None
                    except Badge.DoesNotExist:
                        task_badge_apply_form = None

        for badge in badges_to_apply:
            try:
                badge.awarded = Award.objects.filter(user=profile,
                    badge=badge)[0]
            except IndexError:
                badge.awarded = False
            try:
                badge.applied = Submission.objects.filter(author=profile,
                    badge=badge)[0]
            except IndexError:
                badge.applied = False
            elegible = badge.is_eligible(profile)
            badge.show_apply = (not badge.awarded and not badge.applied and elegible)

    ajax_data.update({
        'stay_on_page': bool(task_link_submit_form or task_badge_apply_form),
        'progressbar_value':  progressbar_value,
    })

    context = {
        'page': page,
        'request': request,
        'can_comment': page.can_comment(request.user),
        'next_page': page.get_next_page(),
        'task_completion': task_completion,
        'next_badge': next_badge,
        'is_last_badge': is_last_badge,
        'task_link_submit_form': task_link_submit_form,
        'task_badge_apply_form': task_badge_apply_form,
        'badges_to_apply': badges_to_apply,
        'ajax_data': ajax_data,
    }
    return context

register.inclusion_tag('content/_toggle_completion.html')(
    task_toggle_completion)
