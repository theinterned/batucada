from django import http
from django.utils.translation import ugettext as _
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from l10n.urlresolvers import reverse
from drumbeat import messages
from users.decorators import login_required
from users.forms import ProfileEditForm, ProfileImageForm
from relationships.models import Relationship
from projects.decorators import organizer_required
from pagination.views import get_pagination_context

from signups.models import Signup
from signups.forms import SignupForm, SignupAnswerForm


@login_required
@organizer_required
def edit_signup(request, slug):
    sign_up = get_object_or_404(Signup, project__slug=slug)
    project = sign_up.project
    if request.method == 'POST':
        form = SignupForm(request.POST, instance=sign_up)
        if form.is_valid():
            sign_up = form.save(commit=False)
            sign_up.author = request.user.get_profile()
            sign_up.save()
            messages.success(request, _('Signup updated!'))
            return http.HttpResponseRedirect(
                reverse('edit_signup', kwargs=dict(slug=project.slug)))
    else:
        form = SignupForm(instance=sign_up)

    return render_to_response('signups/edit_signup.html', {
        'form': form,
        'project': project,
        'sign_up': sign_up,
        'signup_tab': True,
    }, context_instance=RequestContext(request))


def show_signup(request, slug):
    sign_up = get_object_or_404(Signup, project__slug=slug)
    pending_answers = sign_up.answers.filter(deleted=False, accepted=False)
    project = sign_up.project
    is_organizing = is_participating = can_post_answer = False
    if request.user.is_authenticated():
        profile = request.user.get_profile()
        is_organizing = project.organizers().filter(user=profile).exists()
        is_participating = project.participants().filter(user=profile).exists()
        if not is_organizing:
            if sign_up.status != Signup.CLOSED and not is_participating:
                can_post_answer = (not pending_answers.filter(
                    author=profile).exists())
    pending_answers_count = pending_answers.count()
    answers = sign_up.get_visible_answers(request.user)
    context = {
        'sign_up': sign_up,
        'project': project,
        'organizing': is_organizing,
        'participating': is_participating,
        'can_post_answer': can_post_answer,
        'pending_answers_count': pending_answers_count,
    }
    context.update(get_pagination_context(request, answers))
    return render_to_response('signups/sign_up.html', context,
        context_instance=RequestContext(request))


def show_signup_answer(request, slug, answer_id):
    sign_up = get_object_or_404(Signup, project__slug=slug)
    answer = get_object_or_404(sign_up.answers, id=answer_id)
    if answer.deleted:
        messages.error(request, _('This answer was deleted.'))
        if answer.can_edit(request.user):
            return http.HttpResponseRedirect(reverse('signup_answer_restore',
                kwargs={'slug': slug, 'answer_id': answer.id}))
        else:
            return http.HttpResponseRedirect(sign_up.get_absolute_url())
    else:
        return http.HttpResponseRedirect(sign_up.get_answer_url(answer, request.user))


@login_required
def answer_sign_up(request, slug):
    sign_up = get_object_or_404(Signup, project__slug=slug)
    project = sign_up.project
    profile = request.user.get_profile()
    is_organizing = project.organizers().filter(user=profile).exists()
    is_participating = project.participants().filter(user=profile).exists()
    if is_organizing or is_participating:
        messages.error(request,
            _("You already joined this %s.") % project.kind)
        return http.HttpResponseRedirect(sign_up.get_absolute_url())
    elif sign_up.status == Signup.CLOSED:
        msg = _("Sign-up is currently closed." \
                "You can clone the %s if is full.")
        messages.error(request, msg % project.kind)
        return http.HttpResponseRedirect(sign_up.get_absolute_url())
    else:
        answers = sign_up.answers.filter(deleted=False, accepted=False,
            author=profile)
        if answers.exists():
            messages.error(request,
                _("You already posted an answer to the signup questions."))
            return http.HttpResponseRedirect(answers[0].get_absolute_url())
    answer = None
    if request.method == 'POST':
        form = SignupAnswerForm(request.POST)
        profile_form = ProfileEditForm(request.POST, instance=profile)
        profile_image_form = ProfileImageForm()
        if form.is_valid() and profile_form.is_valid():
            profile = profile_form.save()
            answer = form.save(commit=False)
            answer.sign_up = sign_up
            answer.author = profile
            if 'show_preview' not in request.POST:
                profile.save()
                new_rel, created = Relationship.objects.get_or_create(
                    source=profile, target_project=project)
                new_rel.deleted = False
                new_rel.save()
                answer.save()
                if sign_up.status == Signup.NON_MODERATED:
                    answer.accept()
                    messages.success(request, _('You are now a participant!'))
                else:
                    messages.success(request, _('Answer submitted!'))
                return http.HttpResponseRedirect(answer.get_absolute_url())
        else:
            messages.error(request, _('Please correct errors below.'))
    else:
        profile_form = ProfileEditForm(instance=profile)
        profile_image_form = ProfileImageForm()
        form = SignupAnswerForm()
    return render_to_response('signups/answer_sign_up.html', {
        'profile_image_form': profile_image_form,
        'profile_form': profile_form,
        'profile': profile,
        'form': form,
        'project': project,
        'sign_up': sign_up,
        'answer': answer,
        'create': True,
        'preview': ('show_preview' in request.POST),
    }, context_instance=RequestContext(request))


@login_required
def edit_answer_sign_up(request, slug, answer_id):
    sign_up = get_object_or_404(Signup, project__slug=slug)
    answer = get_object_or_404(sign_up.answers, id=answer_id)
    if not answer.can_edit(request.user):
        return http.HttpResponseForbidden(_("You can't edit this answer"))
    profile = answer.author
    if request.method == 'POST':
        form = SignupAnswerForm(request.POST, instance=answer)
        profile_form = ProfileEditForm(request.POST, instance=profile)
        profile_image_form = ProfileImageForm()
        if form.is_valid() and profile_form.is_valid():
            profile = profile_form.save(commit=False)
            answer = form.save(commit=False)
            if 'show_preview' not in request.POST:
                profile.save()
                answer.save()
                messages.success(request, _('Answer updated!'))
                return http.HttpResponseRedirect(answer.get_absolute_url())
        else:
            messages.error(request, _('Please correct errors below.'))
    else:
        profile_form = ProfileEditForm(instance=profile)
        profile_image_form = ProfileImageForm()
        form = SignupAnswerForm(instance=answer)
    return render_to_response('signups/answer_sign_up.html', {
        'profile_image_form': profile_image_form,
        'profile_form': profile_form,
        'profile': profile,
        'form': form,
        'project': sign_up.project,
        'sign_up': sign_up,
        'answer': answer,
        'preview': ('show_preview' in request.POST),
    }, context_instance=RequestContext(request))


@login_required
@organizer_required
def accept_sign_up(request, slug, answer_id, as_organizer=False):
    sign_up = get_object_or_404(Signup, project__slug=slug)
    answer = get_object_or_404(sign_up.answers, id=answer_id)
    if request.method == 'POST':
        project = sign_up.project
        new_rel, created = Relationship.objects.get_or_create(
            source=answer.author, target_project=project)
        new_rel.deleted = False
        new_rel.save()
        answer.accept(as_organizer, reviewer=request.user.get_profile())
        if as_organizer:
            messages.success(request, _('Organizer added!'))
        else:
            messages.success(request, _('Participant added!'))
    return http.HttpResponseRedirect(answer.get_absolute_url())


@login_required
def delete_restore_signup_answer(request, slug, answer_id):
    sign_up = get_object_or_404(Signup, project__slug=slug)
    answer = get_object_or_404(sign_up.answers, id=answer_id)
    if not answer.can_edit(request.user):
        if answer.deleted:
            msg = _('You can not restore this answer.')
        else:
            msg = _('You can not delete this answer.')
        messages.error(request, msg)
        return http.HttpResponseRedirect(answer.get_absolute_url())
    if request.method == 'POST':
        answer.deleted = not answer.deleted
        answer.save()
        if answer.deleted:
            msg = _('Answer deleted!')
        else:
            msg = _('Answer restored!')
        messages.success(request, msg)
        if answer.deleted:
            return http.HttpResponseRedirect(
                sign_up.get_absolute_url())
        else:
            return http.HttpResponseRedirect(answer.get_absolute_url())
    else:
        return render_to_response('signups/delete_restore_answer.html', {
            'answer': answer,
            'sign_up': sign_up,
            'project': sign_up.project,
        }, context_instance=RequestContext(request))
