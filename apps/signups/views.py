from django import http
from django.utils.translation import ugettext as _
from django.template.loader import render_to_string
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.core.paginator import Paginator, EmptyPage

from drumbeat import messages
from users.decorators import login_required
from users.forms import ProfileEditForm, ProfileImageForm
from replies.models import PageComment
from replies.forms import CommentForm
from projects.models import Participation
from relationships.models import Relationship
from content.models import Page
from projects.decorators import organizer_required


def sign_up(request, slug, pagination_page=1):
    page = get_object_or_404(Page, project__slug=slug, slug='sign-up')
    project = page.project
    if request.user.is_authenticated():
        profile = request.user.get_profile()
        is_organizing = project.organizers().filter(user=profile).exists()
        is_participating = project.participants().filter(user=profile).exists()
        first_level_comments = page.comments.filter(
            reply_to__isnull=True).order_by('-created_on')
        can_post_answer = False
        if not is_organizing:
            if is_participating:
                participants = project.participants()
                first_level_comments = first_level_comments.filter(
                    author__in=participants.values('user_id'))
            else:
                first_level_comments = first_level_comments.filter(
                    author=profile)
                can_post_answer = not first_level_comments.filter(
                    deleted=False).exists()
    else:
        first_level_comments = []
        is_organizing = is_participating = can_post_answer = False
    if project.signup_closed:
        can_post_answer = False
    pending_answers_count = 0
    if first_level_comments:
        for answer in first_level_comments.filter(deleted=False):
            if not project.participants().filter(user=answer.author).exists():
                pending_answers_count += 1
    if is_organizing:
        for comment in first_level_comments:
            comment.is_participating = project.participants().filter(
                user=comment.author)
    paginator = Paginator(first_level_comments, 7)
    try:
        current_page = paginator.page(pagination_page)
    except EmptyPage:
        raise http.Http404
    return render_to_response('signups/sign_up.html', {
        'page': page,
        'project': project,
        'organizing': is_organizing,
        'participating': is_participating,
        'first_level_comments': first_level_comments,
        'can_post_answer': can_post_answer,
        'pending_answers_count': pending_answers_count,
        'paginator': paginator,
        'page_num': pagination_page,
        'next_page': int(pagination_page) + 1,
        'prev_page': int(pagination_page) - 1,
        'num_pages': paginator.num_pages,
        'pagination_page': current_page,
    }, context_instance=RequestContext(request))


@login_required
def comment_sign_up(request, slug, comment_id=None):
    page = get_object_or_404(Page, project__slug=slug, slug='sign-up')
    project = page.project
    profile = request.user.get_profile()
    is_organizing = project.organizers().filter(user=profile).exists()
    is_participating = project.participants().filter(user=profile).exists()
    reply_to = abs_reply_to = None
    if comment_id:
        reply_to = page.comments.get(pk=comment_id)
        abs_reply_to = reply_to
        while abs_reply_to.reply_to:
            abs_reply_to = abs_reply_to.reply_to
        if not is_organizing:
            if is_participating:
                if not project.is_participating(abs_reply_to.author.user):
                    return http.HttpResponseForbidden(
                        _("You can't see this page"))
            elif abs_reply_to.author != profile:
                return http.HttpResponseForbidden(_("You can't see this page"))
    elif is_organizing or is_participating:
        messages.error(request,
            _("You already joined this %s.") % project.kind)
        return http.HttpResponseRedirect(page.get_absolute_url())
    elif project.signup_closed:
        msg = _("Sign-up is currently closed." \
                "You can clone the %s if is full.")
        messages.error(request, msg % project.kind)
        return http.HttpResponseRedirect(page.get_absolute_url())
    else:
        answers = page.comments.filter(reply_to__isnull=True, deleted=False,
            author=profile)
        if answers.exists():
            messages.error(request,
                _("You already posted an answer to the signup questions."))
            return http.HttpResponseRedirect(page.get_absolute_url())
    comment = None
    if request.method == 'POST':
        form = CommentForm(request.POST)
        profile_form = ProfileEditForm(request.POST, instance=profile)
        profile_image_form = ProfileImageForm()
        if form.is_valid() and (reply_to or profile_form.is_valid()):
            if not reply_to:
                profile = profile_form.save()
            comment = form.save(commit=False)
            comment.page_object = page
            comment.scope_object = project
            comment.author = profile
            comment.reply_to = reply_to
            comment.abs_reply_to = abs_reply_to
            if 'show_preview' not in request.POST:
                if not reply_to:
                    profile.save()
                    new_rel, created = Relationship.objects.get_or_create(
                        source=profile, target_project=project)
                    new_rel.deleted = False
                    new_rel.save()
                comment.save()
                if reply_to:
                    success_msg = _('Reply posted!')
                else:
                    success_msg = _('Answer submitted!')
                messages.success(request, success_msg)
                return http.HttpResponseRedirect(comment.get_absolute_url())
        else:
            messages.error(request, _('Please correct errors below.'))
    else:
        profile_form = ProfileEditForm(instance=profile)
        profile_image_form = ProfileImageForm()
        form = CommentForm()
    return render_to_response('signups/comment_sign_up.html', {
        'profile_image_form': profile_image_form,
        'profile_form': profile_form,
        'profile': profile,
        'form': form,
        'project': project,
        'page': page,
        'reply_to': reply_to,
        'comment': comment,
        'create': True,
        'preview': ('show_preview' in request.POST),
    }, context_instance=RequestContext(request))


@login_required
def edit_comment_sign_up(request, slug, comment_id):
    comment = get_object_or_404(PageComment, id=comment_id)
    if not comment.can_edit(request.user):
        return http.HttpResponseForbidden(_("You can't edit this comment"))
    abs_reply_to = comment
    while abs_reply_to.reply_to:
        abs_reply_to = abs_reply_to.reply_to
    if abs_reply_to == comment:
        abs_reply_to = reply_to = None
    else:
        reply_to = comment.reply_to
    profile = comment.author
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        profile_form = ProfileEditForm(request.POST, instance=profile)
        profile_image_form = ProfileImageForm()
        if form.is_valid() and (reply_to or profile_form.is_valid()):
            if not reply_to:
                profile = profile_form.save(commit=False)
            comment = form.save(commit=False)
            if 'show_preview' not in request.POST:
                if not reply_to:
                    profile.save()
                comment.save()
                if reply_to:
                    success_msg = _('Comment updated!')
                else:
                    success_msg = _('Answer updated!')
                messages.success(request, success_msg)
                return http.HttpResponseRedirect(comment.get_absolute_url())
        else:
            messages.error(request, _('Please correct errors below.'))
    else:
        profile_form = ProfileEditForm(instance=comment.author)
        profile_image_form = ProfileImageForm()
        form = CommentForm(instance=comment)
    return render_to_response('signups/comment_sign_up.html', {
        'profile_image_form': profile_image_form,
        'profile_form': profile_form,
        'profile': profile,
        'form': form,
        'project': comment.scope_object,
        'page': comment.page_object,
        'reply_to': reply_to,
        'comment': comment,
        'preview': ('show_preview' in request.POST),
    }, context_instance=RequestContext(request))


@login_required
@organizer_required
def accept_sign_up(request, slug, comment_id, as_organizer=False):
    page = get_object_or_404(Page, project__slug=slug, slug='sign-up')
    project = page.project
    answer = page.comments.get(pk=comment_id)
    organizing = project.organizers().filter(user=answer.author.user).exists()
    participating = project.participants().filter(
        user=answer.author.user).exists()
    can_accept = not (answer.reply_to or organizing or participating)
    if not can_accept or request.method != 'POST':
        return http.HttpResponseForbidden(_("You can't see this page"))
    participation = Participation(project=project, user=answer.author,
        organizing=as_organizer)
    participation.save()
    new_rel, created = Relationship.objects.get_or_create(source=answer.author,
        target_project=project)
    new_rel.deleted = False
    new_rel.save()
    accept_content = render_to_string(
            "signups/accept_sign_up_comment.html",
            {'as_organizer': as_organizer})
    accept_comment = PageComment(content=accept_content,
        author=request.user.get_profile(), page_object=page,
        scope_object=project, reply_to=answer, abs_reply_to=answer)
    accept_comment.save()
    if as_organizer:
        messages.success(request, _('Organizer added!'))
    else:
        messages.success(request, _('Participant added!'))
    return http.HttpResponseRedirect(answer.get_absolute_url())
