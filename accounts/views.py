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


class Account(View):
    template_name = 'accounts/account.html'
    page_size = 10

    def get(self, request, *args, **kwargs):
        file_upload_form: FileUploadForm = FileUploadForm(request=request)
        files: Optional[Paginator] = None

        if request.user.is_authenticated:
            paginator: Paginator = Paginator(
                File.objects.filter(owner=request.user),
                self.page_size
            )
            files = paginator.get_page(request.GET.get('page'))

        return render(
            request=request,
            template_name=self.template_name,
            context={
                'file_upload_form': file_upload_form,
                'files': files,
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
