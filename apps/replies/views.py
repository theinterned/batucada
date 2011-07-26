from django import http
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.translation import ugettext as _

from l10n.urlresolvers import reverse
from drumbeat import messages
from users.decorators import login_required
from projects.decorators import participation_required
from content.models import Page

from replies.models import PageComment
from replies.forms import CommentForm


def show_comment(request, slug, page_slug, comment_id):
    comment = get_object_or_404(PageComment, page__project__slug=slug,
        page__slug=page_slug, id=comment_id)
    page_url = comment.page.get_absolute_url()
    if comment.deleted:
        if page_slug == 'sign-up' and not comment.reply_to:
            msg = _('This answer was deleted.')
        else:
            msg = _('This comment was deleted.')
        messages.error(request, msg)
        if comment.can_edit(request.user):
            return http.HttpResponseRedirect(reverse('comment_restore',
                kwargs={'slug': comment.page.project.slug,
                'page_slug': comment.page.slug, 'comment_id': comment.id}))
        else:
            return http.HttpResponseRedirect(page_url)
    else:
        return http.HttpResponseRedirect(page_url + '#%s' % comment.id)


@login_required
@participation_required
def comment_page(request, slug, page_slug, comment_id=None):
    page = get_object_or_404(Page, project__slug=slug, slug=page_slug)
    if not page.editable:
        return http.HttpResponseForbidden(_("You can't edit this page"))
    user = request.user.get_profile()
    reply_to = abs_reply_to = None
    if comment_id:
        reply_to = page.comments.get(pk=comment_id)
        abs_reply_to = reply_to
        while abs_reply_to.reply_to:
            abs_reply_to = abs_reply_to.reply_to
    comment = None
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.page = page
            comment.author = user
            comment.reply_to = reply_to
            comment.abs_reply_to = abs_reply_to
            if 'show_preview' not in request.POST:
                comment.save()
                messages.success(request, _('Comment posted!'))
                return http.HttpResponseRedirect(comment.get_absolute_url())
        else:
            messages.error(request, _('Please correct errors below.'))
    else:
        form = CommentForm()
    return render_to_response('replies/comment_page.html', {
        'form': form,
        'project': page.project,
        'page': page,
        'reply_to': reply_to,
        'comment': comment,
        'create': True,
        'preview': ('show_preview' in request.POST),
    }, context_instance=RequestContext(request))




@login_required
@participation_required
def edit_comment(request, slug, page_slug, comment_id):
    comment = get_object_or_404(PageComment, id=comment_id,
        page__slug=page_slug, page__project__slug=slug)
    if not comment.can_edit(request.user):
        return http.HttpResponseForbidden(_("You can't edit this page"))
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            comment = form.save(commit=False)
            if 'show_preview' not in request.POST:
                comment.save()
                messages.success(request, _('Comment updated!'))
                return http.HttpResponseRedirect(comment.get_absolute_url())
        else:
            messages.error(request, _('Please correct errors below.'))
    else:
        form = CommentForm(instance=comment)
    return render_to_response('replies/comment_page.html', {
        'form': form,
        'comment': comment,
        'page': comment.page,
        'project': comment.page.project,
        'reply_to': comment.reply_to,
        'preview': ('show_preview' in request.POST),
    }, context_instance=RequestContext(request))


@login_required
def delete_restore_comment(request, slug, page_slug, comment_id):
    comment = get_object_or_404(PageComment, id=comment_id,
        page__slug=page_slug, page__project__slug=slug)
    if not comment.can_edit(request.user):
        return http.HttpResponseForbidden(_("You can't edit this comment"))
    if request.method == 'POST':
        comment.deleted = not comment.deleted
        comment.save()
        if comment.page.slug == 'sign-up' and not comment.reply_to:
            if comment.deleted:
                msg = _('Answer deleted!')
            else:
                msg = _('Answer restored!')
        else:
            if comment.deleted:
                msg = _('Comment deleted!')
            else:
                msg = _('Comment restored!')
        messages.success(request, msg)
        if comment.deleted:
            return http.HttpResponseRedirect(comment.page.get_absolute_url())
        else:
            return http.HttpResponseRedirect(comment.get_absolute_url())
    else:
        return render_to_response('replies/delete_restore_comment.html', {
            'comment': comment,
            'page': comment.page,
            'project': comment.page.project,
        }, context_instance=RequestContext(request))


