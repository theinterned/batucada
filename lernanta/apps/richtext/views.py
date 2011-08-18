import os
from datetime import datetime

from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext

from ckeditor.views import upload as ckeditor_upload
from ckeditor.views import get_available_name, get_media_url

from richtext.forms import FileBrowser


@csrf_exempt
def upload_image(request):
    # Allow the view to callback ckeditor's dialog.
    response = ckeditor_upload(request)
    response['X-Frame-Options'] = 'SAMEORIGIN'
    return response


def get_file_browse_urls(user=None):
    """
    Recursively walks all dirs under file upload dir and generates a list of
    relative paths and full file URL's for each file found.
    """
    files = []

    # If a user is provided and CKEDITOR_RESTRICT_BY_USER is True,
    # limit images to user specific path, but not for superusers.
    restrict_by_user = getattr(settings, 'CKEDITOR_RESTRICT_BY_USER', False)
    if user and not user.is_superuser and restrict_by_user:
        user_path = user.username
    else:
        user_path = ''

    browse_path = os.path.join(settings.CKEDITOR_FILE_UPLOAD_PATH, user_path)

    for root, dirs, filenames in os.walk(browse_path):
        for filename in [os.path.join(root, x) for x in filenames]:
            files.append((get_media_url(filename), filename[len(browse_path) + 1:]))

    return files


def browse_file(request):
    files = get_file_browse_urls(request.user)
    if request.method == 'POST':
        form = FileBrowser(files, request.POST)
        if form.is_valid():
            ckeditor_func_num = form.cleaned_data['CKEditorFuncNum']
            url = form.cleaned_data['file']
            response = HttpResponse("""
                <script type='text/javascript'>
                    window.opener.CKEDITOR.tools.callFunction(%s, '%s');
                    window.close();
                </script>""" % (ckeditor_func_num, url))
            response['X-Frame-Options'] = 'SAMEORIGIN'
            return response
    else:
        form = FileBrowser(files,
            initial=dict(CKEditorFuncNum=request.GET['CKEditorFuncNum']))
    context = RequestContext(request, {
        'files': files,
        'form': form,
    })
    return render_to_response('richtext/browse.html', context)


def get_upload_filename(upload_name, user):
    # If CKEDITOR_RESTRICT_BY_USER is True upload file to user specific path.
    if getattr(settings, 'CKEDITOR_RESTRICT_BY_USER', False):
        user_path = user.username
    else:
        user_path = ''

    # Generate date based path to put uploaded file.
    date_path = datetime.now().strftime('%Y/%m/%d')

    # Complete upload path (upload_path + date_path).
    upload_path = os.path.join(settings.CKEDITOR_FILE_UPLOAD_PATH, user_path, date_path)

    # Make sure upload_path exists.
    if not os.path.exists(upload_path):
        os.makedirs(upload_path)

    # Get available name and return.
    return get_available_name(os.path.join(upload_path, upload_name))


@csrf_exempt
def upload_file(request):
    # Get the uploaded file from request.
    upload = request.FILES['upload']

    # Open output file in which to store upload.
    upload_filename = get_upload_filename(upload.name, request.user)
    out = open(upload_filename, 'wb+')

    # Iterate through chunks and write to destination.
    for chunk in upload.chunks():
        out.write(chunk)
    out.close()

    # Respond with Javascript sending ckeditor upload url.
    url = get_media_url(upload_filename)
    response = HttpResponse("""
        <script type='text/javascript'>
            window.parent.CKEDITOR.tools.callFunction(%s, '%s');
        </script>""" % (request.GET['CKEditorFuncNum'], url))
    response['X-Frame-Options'] = 'SAMEORIGIN'
    return response
