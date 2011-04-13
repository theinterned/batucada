import datetime

from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, Http404, HttpResponseForbidden
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.db.models import Q
from django.template.loader import render_to_string
from django.db import IntegrityError

from users.decorators import login_required
from users.forms import ProfileEditForm, ProfileImageForm
from drumbeat import messages
from projects.decorators import participation_required, ownership_required
from projects.models import Project, Participation
from relationships.models import Relationship

from content.forms import PageForm, NotListedPageForm, CommentForm, OwnersPageForm, OwnersNotListedPageForm
from content.models import Page, PageVersion, PageComment


def show_page(request, slug, page_slug):
    page = get_object_or_404(Page, project__slug=slug, slug=page_slug)
    first_level_comments = page.comments.filter(reply_to__isnull=True)
    return render_to_response('content/page.html', {
        'page': page,
        'project': page.project,
        'can_edit': page.can_edit(request.user),
        'first_level_comments': first_level_comments,
    }, context_instance=RequestContext(request))


@login_required
@participation_required
def edit_page(request, slug, page_slug):
    page = get_object_or_404(Page, project__slug=slug, slug=page_slug)
    if not page.editable:
        return HttpResponseForbidden()
    user = request.user.get_profile()
    if request.user.is_superuser or user == page.project.created_by:
        form_cls = OwnersPageForm if page.listed else OwnersNotListedPageForm
    elif page.collaborative:
        form_cls = PageForm if page.listed else NotListedPageForm
    else:
        # Restrict permissions for non-collaborative pages.
        return HttpResponseForbidden()
    if request.method == 'POST':
        old_version = PageVersion(title=page.title, content=page.content,
            author=page.author, date=page.last_update, page=page)
        form = form_cls(request.POST, instance=page)
        if form.is_valid():
            old_version.save()
            page = form.save(commit=False)
            page.author = user
            page.last_update = datetime.datetime.now()
            page.save()
            messages.success(request, _('%s updated!') % page.title)
            return HttpResponseRedirect(reverse('page_show', kwargs={
                'slug': slug,
                'page_slug': page_slug,
            }))
        else:
            messages.error(request,
                           _('There was a problem saving %s.' % page.title))
    else:
        form = form_cls(instance=page)
    return render_to_response('content/edit_page.html', {
        'form': form,
        'page': page,
        'project': page.project,
    }, context_instance=RequestContext(request))


@login_required
@participation_required
def create_page(request, slug):
    project = get_object_or_404(Project, slug=slug)
    user = request.user.get_profile()
    if request.user.is_superuser or user == project.created_by:
        form_cls = OwnersPageForm
    else:
        form_cls = PageForm
    if request.method == 'POST':
        form = form_cls(request.POST)
        if form.is_valid():
            page = form.save(commit=False)
            page.project = project
            page.author = user
            page.save()
            messages.success(request, _('Task created!'))
            return HttpResponseRedirect(reverse('page_show', kwargs={
                'slug': slug,
                'page_slug': page.slug,
            }))
        else:
            messages.error(request,
                           _('There was a problem creating the task.'))
    else:
        form = form_cls()
    return render_to_response('content/create_page.html', {
        'form': form,
        'project': project,
    }, context_instance=RequestContext(request))


@login_required
@participation_required
def comment_page(request, slug, page_slug, comment_id=None):
    page = get_object_or_404(Page, project__slug=slug, slug=page_slug)
    if not page.editable:
        return HttpResponseForbidden()
    user = request.user.get_profile()
    reply_to = abs_reply_to = None
    if comment_id:
        reply_to = page.comments.get(pk=comment_id)
        abs_reply_to = reply_to
        while abs_reply_to.reply_to:
            abs_reply_to = abs_reply_to.reply_to
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.page = page
            comment.author = user
            comment.reply_to = reply_to
            comment.abs_reply_to = abs_reply_to
            comment.save()
            messages.success(request, _('Comment posted!'))
            return HttpResponseRedirect(reverse('page_show', kwargs={
                'slug': slug,
                'page_slug': page.slug,
            }))
        else:
            messages.error(request,
                           _('There was a problem posting the comment.'))
    else:
        form = CommentForm()
    return render_to_response('content/comment_page.html', {
        'form': form,
        'project': page.project,
        'page': page,
        'reply_to': reply_to,
    }, context_instance=RequestContext(request))


def history_page(request, slug, page_slug):
    page = get_object_or_404(Page, project__slug=slug, slug=page_slug)
    if not page.editable:
        return HttpResponseForbidden()
    versions = PageVersion.objects.filter(page=page).order_by('-date')
    return render_to_response('content/history_page.html', {
        'page': page,
        'versions': versions,
        'project': page.project,
    }, context_instance=RequestContext(request))


def version_page(request, slug, page_slug, version_id):
    version = get_object_or_404(PageVersion, page__project__slug=slug,
        page__slug=page_slug, id=version_id)
    page = version.page
    if not page.editable:
        return HttpResponseForbidden()
    return render_to_response('content/version_page.html', {
        'page': page,
        'version': version,
        'project': page.project,
        'can_edit': page.can_edit(request.user),
    }, context_instance=RequestContext(request))


@login_required
@participation_required
def restore_version(request, slug, page_slug, version_id):
    version = get_object_or_404(PageVersion, page__project__slug=slug,
        page__slug=page_slug, id=version_id)
    page = version.page
    if not page.editable:
        return HttpResponseForbidden()
    user = request.user.get_profile()
    if request.user.is_superuser or user == page.project.created_by:
        form_cls = OwnersPageForm if page.listed else OwnersNotListedPageForm
    elif page.collaborative:
        form_cls = PageForm if page.listed else NotListedPageForm
    else:
        # Restrict permissions for non-collaborative pages.
        return HttpResponseForbidden()
    if request.method == 'POST':
        old_version = PageVersion(title=page.title, content=page.content,
            author=page.author, date=page.last_update, page=page)
        form = form_cls(request.POST, instance=page)
        if form.is_valid():
            old_version.save()
            page = form.save(commit=False)
            page.author = user
            page.last_update = datetime.datetime.now()
            page.save()
            messages.success(request, _('%s restored!') % page.title)
            return HttpResponseRedirect(reverse('page_show', kwargs={
                'slug': slug,
                'page_slug': page_slug,
            }))
        else:
            messages.error(request,
                           _('There was a problem saving %s.' % page.title))
    else:
        page.title = version.title
        page.content = version.content
        form = form_cls(instance=page)
    return render_to_response('content/restore_version.html', {
        'form': form,
        'page': page,
        'version': version,
        'project': page.project,
    }, context_instance=RequestContext(request))


def sign_up(request, slug):
    page = get_object_or_404(Page, project__slug=slug, slug='sign-up')
    project = page.project
    if request.user.is_authenticated():
        profile = request.user.get_profile()
        first_level_comments = page.comments.filter(reply_to__isnull=True)
        if profile != project.created_by:
            participants = project.participants()
            if participants.filter(user=profile).exists():
                approved = Q(author__in=participants.values('user_id')) | Q(author=project.created_by)
                first_level_comments = first_level_comments.filter(approved)
            else:
                first_level_comments = first_level_comments.filter(author=profile)
    else:
        first_level_comments = []
    return render_to_response('content/sign_up.html', {
        'page': page,
        'project': project,
        'first_level_comments': first_level_comments,
    }, context_instance=RequestContext(request))


@login_required
def comment_sign_up(request, slug, comment_id=None):
    page = get_object_or_404(Page, project__slug=slug, slug='sign-up')
    project = page.project
    user = request.user.get_profile()
    reply_to = abs_reply_to = None
    if comment_id:
        reply_to = page.comments.get(pk=comment_id)
        abs_reply_to = reply_to
        while abs_reply_to.reply_to:
            abs_reply_to = abs_reply_to.reply_to
    elif project.signup_closed:
        return HttpResponseForbidden()

    if user != project.created_by:
        participants = project.participants()
        author = abs_reply_to.author if abs_reply_to else user
        if participants.filter(user=user).exists():
            if author != project.created_by and not participants.filter(user=author).exists():
                return HttpResponseForbidden()
        elif author != user:
            return HttpResponseForbidden()

    if request.method == 'POST':
        form = CommentForm(request.POST)
        profile_form = ProfileEditForm(request.POST, instance=user)
        profile_image_form = ProfileImageForm()
        if form.is_valid() and (reply_to or profile_form.is_valid()):
            if not reply_to:
                profile_form.save()
                new_rel = Relationship(source=user, target_project=project)
                try:
                    new_rel.save()
                except IntegrityError:
                    pass
            comment = form.save(commit=False)
            comment.page = page
            comment.author = user
            comment.reply_to = reply_to
            comment.abs_reply_to = abs_reply_to
            comment.save()
            success_msg = _('Reply posted!') if reply_to else _('Answer submitted!')
            messages.success(request, success_msg)
            return HttpResponseRedirect(reverse('page_show', kwargs={
                'slug': slug,
                'page_slug': page.slug,
            }))
        else:
            error_msg = _('There was a problem posting your reply.') if reply_to \
                        else _('There was a problem submitting your answer.')
            messages.error(request, error_msg)
    else:
        profile_form = ProfileEditForm(instance=user)
        profile_image_form = ProfileImageForm()
        form = CommentForm()
    return render_to_response('content/comment_sign_up.html', {
        'profile_image_form': profile_image_form,
        'profile_form': profile_form,
        'profile': user,
        'form': form,
        'project': project,
        'page': page,
        'reply_to': reply_to,
    }, context_instance=RequestContext(request))

@login_required
@ownership_required
def accept_sign_up(request, slug, comment_id):
    page = get_object_or_404(Page, project__slug=slug, slug='sign-up')
    project = page.project
    user = request.user.get_profile()
    answer = page.comments.get(pk=comment_id)
    if answer.reply_to or answer.author == project.created_by or request.method != 'POST':
        return HttpResponseForbidden()
    try:
        participation = answer.participation
        return HttpResponseForbidden()
    except Participation.DoesNotExist:
        pass
    try:
        participation = project.participants().get(user=answer.author)
        if participation.sign_up:
            participation.left_on = datetime.datetime.now()
            participation.save()
            raise Participation.DoesNotExist
        else:
            participation.sign_up = answer
    except Participation.DoesNotExist:
        participation = Participation(project= project, user=answer.author, sign_up=answer)
    participation.save()
    new_rel = Relationship(source=answer.author, target_project=project)
    try:
        new_rel.save()
    except IntegrityError:
        pass
    accept_content = detail_description_content = render_to_string(
            "content/accept_sign_up_comment.html",
            {})
    accept_comment = PageComment(content=accept_content, author=user,
        page=page, reply_to=answer, abs_reply_to=answer)
    accept_comment.save()
    messages.success(request, _('Participant added!'))
    return HttpResponseRedirect(answer.get_absolute_url())


@login_required
@participation_required
def index_up(request, slug, counter):
    """Page goes up in the sidebar index (page.index decreases)."""
    project = get_object_or_404(Project, slug=slug)
    try:
        counter = int(counter)
    except ValueError:
        raise Http404
    content_pages = Page.objects.filter(project__pk=project.pk, listed=True).order_by('index')
    if counter < 1 or content_pages.count() <= counter:
        raise Http404
    prev_page = content_pages[counter - 1]
    page = content_pages[counter]
    prev_page.index, page.index = page.index, prev_page.index
    page.save()
    prev_page.save()
    return HttpResponseRedirect(project.get_absolute_url() + '#tasks')


@login_required
@participation_required
def index_down(request, slug, counter):
    """Page goes down in the sidebar index (page.index increases)."""
    project = get_object_or_404(Project, slug=slug)
    try:
        counter = int(counter)
    except ValueError:
        raise Http404
    content_pages = Page.objects.filter(project__pk=project.pk, listed=True).order_by('index')
    if counter < 0 or content_pages.count() - 1 <= counter:
        raise Http404
    next_page = content_pages[counter + 1]
    page = content_pages[counter]
    next_page.index, page.index = page.index, next_page.index
    page.save()
    next_page.save()
    return HttpResponseRedirect(project.get_absolute_url() + '#tasks')


