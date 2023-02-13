from datetime import timedelta
from typing import Optional

from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.views import LoginView
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views import View

from accounts.dataclasses import SignedURLReturnObject
from accounts.forms import SignInForm, FileUploadForm, SignUpForm
from accounts.models import File


BOOK_CONTENT_TYPES = (
    'application/vnd.amazon.ebook',
    'application/epub+zip',
)


IMAGE_CONTENT_TYPES = (
    'image/avif',
    'image/bmp',
    'image/gif',
    'image/jpeg',
    'image/png',
    'image/tiff',
    'image/webp',
)


ARCHIVE_CONTENT_TYPES = (
    'application/x-bzip',
    'application/x-bzip2',
    'application/gzip',
    'application/vnd.rar',
    'application/x-tar',
    'application/zip',
    'application/x-7z-compressed',
)


DOCUMENT_CONTENT_TYPES = (
    'application/x-abiword',
    'application/x-freearc',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.oasis.opendocument.presentation',
    'application/vnd.oasis.opendocument.spreadsheet',
    'application/vnd.oasis.opendocument.text',
    'application/pdf',
    'application/vnd.ms-powerpoint',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    'application/rtf',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
)


AUDIO_CONTENT_TYPES = (
    'audio/aac',
    'audio/midi',
    'audio/x-midi',
    'audio/mpeg',
    'audio/ogg',
    'audio/wav',
    'audio/webm',
    'audio/3gpp',
    'audio/3gpp2',
)


VIDEO_CONTENT_TYPES = (
    'video/mp4',
    'video/mpeg',
    'video/ogg',
    'video/mp2t',
    'video/webm',
    'video/3gpp',
    'video/3gpp2',
)


CATEGORIES = {
    'books': {
        'content_types': BOOK_CONTENT_TYPES,
        'verbose_name': _('Books'),
    },
    'images': {
        'content_types': IMAGE_CONTENT_TYPES,
        'verbose_name': _('Images'),
    },
    'archives': {
        'content_types': ARCHIVE_CONTENT_TYPES,
        'verbose_name': _('Archives'),
    },
    'documents': {
        'content_types': DOCUMENT_CONTENT_TYPES,
        'verbose_name': _('Documents'),
    },
    'audios': {
        'content_types': AUDIO_CONTENT_TYPES,
        'verbose_name': _('Audios'),
    },
    'videos': {
        'content_types': VIDEO_CONTENT_TYPES,
        'verbose_name': _('Videos'),
    },
    'default': {
        'content_types': None,
        'verbose_name': _('All files'),
    },
}


class Account(View):
    template_name = 'accounts/account.html'
    page_size = 10

    def get(self, request, *args, **kwargs):
        file_upload_form: FileUploadForm = FileUploadForm(request=request)

        if not request.user.is_authenticated:
            return render(
                request=request,
                template_name=self.template_name,
                context={
                    'file_upload_form': file_upload_form,
                    'files': None,
                }
            )

        category: str = request.GET.get('category', 'default')
        cond: dict = dict(
            owner=request.user
        )

        try:
            current_category: dict = CATEGORIES[category]
        except KeyError:
            raise PermissionDenied()

        current_category.update(dict(name=category))

        content_types = current_category['content_types']

        if content_types is not None:
            # In case of default - all files content_types can be None
            cond.update(dict(content_type__in=content_types))

        paginator: Paginator = Paginator(
            File.objects.filter(**cond),
            self.page_size
        )
        files: Paginator = paginator.get_page(request.GET.get('page'))

        return render(
            request=request,
            template_name=self.template_name,
            context={
                'file_upload_form': file_upload_form,
                'files': files,
                'categories': CATEGORIES,
                'current_category': current_category,
            }
        )

    def post(self, request, *args, **kwargs):
        file_upload_form: FileUploadForm = FileUploadForm(
            data=request.POST,
            files=request.FILES,
            request=request
        )

        if file_upload_form.is_valid():
            file_upload_form.save()

            return redirect(
                reverse(
                    'accounts:file',
                    kwargs={
                        'url_path': file_upload_form.instance.url_path
                    }
                )
            )

        return render(
            request=request,
            template_name=self.template_name,
            context={
                'file_upload_form': file_upload_form
            }
        )


class FileView(View):
    template_name = 'accounts/file.html'
    ONE_HOUR: int = 60 * 60

    def get(self, request, *args, **kwargs):
        url_path = kwargs.get('url_path')

        if url_path is None:
            return redirect(reverse('accounts:index'))

        try:
            file = File.objects.get(url_path=url_path)
        except File.DoesNotExist:
            return redirect(reverse('accounts:index'))

        if not file.is_user_has_access(request.user):
            raise PermissionDenied()

        return render(
            request=request,
            template_name=self.template_name,
            context={
                'file': file,
                'upload_url': None,
                'expiration': None,
            }
        )

    def post(self, request, *args, **kwargs):
        url_path = kwargs.get('url_path')

        if url_path is None:
            return redirect(reverse('accounts:index'))

        try:
            file = File.objects.get(url_path=url_path)
        except File.DoesNotExist:
            return redirect(reverse('accounts:index'))

        expiration = self.ONE_HOUR
        signed_url_object: SignedURLReturnObject = file.generate_download_signed_url(expiration=expiration)

        return render(
            request=request,
            template_name=self.template_name,
            context={
                'file': file,
                'upload_url': signed_url_object.url,
                'expiration': timedelta(seconds=expiration),
            }
        )


class SignUpView(View):
    template = 'accounts/auth/signup.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(reverse('accounts:index'))

        return super(SignUpView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        signup_form = SignUpForm()

        return render(
            request=request,
            template_name=self.template,
            context={
                'signup_form': signup_form
            }
        )

    def post(self, request, *args, **kwargs):
        signup_form: SignUpForm = SignUpForm(
            data=request.POST
        )

        if signup_form.is_valid():
            signup_form.save()
            messages.success(request, _('%s, you can sign in now!' % signup_form.cleaned_data.get('username')))

            return redirect(reverse('accounts:signin'))

        return render(
            request=request,
            template_name=self.template,
            context={
                'signup_form': signup_form
            }
        )


class SigInView(LoginView):
    template = 'accounts/auth/signin.html'
    redirect_authenticated_user = True

    def get(self, request, *args, **kwargs):
        signin_form = SignInForm()

        return render(
            request=request,
            template_name=self.template,
            context={
                'signin_form': signin_form
            }
        )

    def post(self, request, *args, **kwargs):
        signin_form: SignInForm = SignInForm(
            data=request.POST
        )

        if signin_form.is_valid():
            username = signin_form.cleaned_data.get('username')
            password = signin_form.cleaned_data.get('password')

            user = authenticate(username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect(reverse('accounts:index'))

        messages.error(request, _('Invalid username or password.'))

        return render(
            request=request,
            template_name=self.template,
            context={
                'signin_form': signin_form
            }
        )
