from django.shortcuts import render

from django.contrib import messages
from django.contrib.auth.forms import PasswordResetForm, AuthenticationForm, SetPasswordForm, PasswordChangeForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import PasswordContextMixin, SuccessURLAllowedHostsMixin, INTERNAL_RESET_URL_TOKEN, \
    INTERNAL_RESET_SESSION_TOKEN, LoginView
from django.contrib.sites.shortcuts import get_current_site
from django.core import mail
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render, redirect, resolve_url
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.http import is_safe_url, urlsafe_base64_decode
from django.views import generic
from django.utils import timezone
from django.core.mail import send_mail, EmailMessage
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import TemplateView
from django.views.generic.edit import FormView, CreateView, DeleteView, UpdateView
from django.contrib.auth.models import User

from django.contrib.auth import (
    REDIRECT_FIELD_NAME, get_user_model, login as auth_login,
    logout as auth_logout, update_session_auth_hash,
    authenticate)

from pymongo import MongoClient
from tagging.models import TaggedItem

from MicroLearningPlatform import settings

from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage, send_mail
from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views import generic

from micro_content_manager.models import MicroLearningContent
from users_manager.forms import UserCreateForm
from users_manager.tokens import account_activation_token

UserModel = get_user_model()

MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017
DB_NAME = 'tfg'
COLLECTION_NAME = 'auth_user'

class HomeView(TemplateView):

    def get(self, request, *args, **kwargs):
        return render(request, 'users_manager/user_page.html')

    def post(self, request):
        tags = self.request.POST['search']
        micro_contents_searched = TaggedItem.objects.get_by_model(MicroLearningContent, tags)

       # return render(self.request, 'micro_content_manager/mc_search.html', {"micro_contents_searched": micro_contents_searched})
        return render(self.request, 'users_manager/user_page.html', {"micro_contents_searched": micro_contents_searched})


class UserDataView(TemplateView):
    template_name = 'users_manager/user_data.html'


class LogInView(LoginView):
    def form_valid(self, form):
        """Security check complete. Log the user in."""
        auth_login(self.request, form.get_user())
        return render(self.request, self.get_success_url())
    pass


# Class-based password reset views
# - PasswordResetView sends the mail
# - PasswordResetDoneView shows a success message for the above
# - PasswordResetConfirmView checks the link the user clicked and
#   prompts for a new password
# - PasswordResetCompleteView shows a success message for the above

class PasswordResetView(PasswordContextMixin, FormView):
    email_template_name = 'registration/password_reset_email.html'
    extra_email_context = None
    form_class = PasswordResetForm
    from_email = None
    html_email_template_name = None
    subject_template_name = 'registration/password_reset_subject.txt'
    success_url = reverse_lazy('password_reset_done')
    template_name = 'registration/password_reset_form.html'
    title = ('Password reset')
    token_generator = default_token_generator

    @method_decorator(csrf_protect)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def form_valid(self, form):
        opts = {
            'use_https': self.request.is_secure(),
            'token_generator': self.token_generator,
            'from_email': self.from_email,
            'email_template_name': self.email_template_name,
            'subject_template_name': self.subject_template_name,
            'request': self.request,
            'html_email_template_name': self.html_email_template_name,
            'extra_email_context': self.extra_email_context,
        }
        form.save(**opts)
        return super().form_valid(form)

    def post(self, request):
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
        connection = mail.get_connection()
        connection.open()
        email = EmailMessage(subject='juju',
                             body='We would like to let you know about this week\'s specials....',
                             from_email='inaocosasvarias@gmail.com',
                             to=[email],
                             headers={'Reply-To': 'inaolat@gmail.com'})

        connection.send_messages([email])
        connection.close()
        return render(request, 'registration/password_reset_done.html')


    class LoginView(SuccessURLAllowedHostsMixin, FormView):
        """
        Display the login form and handle the login action.
        """
        form_class = AuthenticationForm
        authentication_form = None
        redirect_field_name = REDIRECT_FIELD_NAME
        template_name = 'registration/login.html'
        redirect_authenticated_user = False
        extra_context = None

        @method_decorator(sensitive_post_parameters())
        @method_decorator(csrf_protect)
        @method_decorator(never_cache)
        def dispatch(self, request, *args, **kwargs):
            if self.redirect_authenticated_user and self.request.user.is_authenticated:
                redirect_to = self.get_success_url()
                if redirect_to == self.request.path:
                    raise ValueError(
                        "Redirection loop for authenticated user detected. Check that "
                        "your LOGIN_REDIRECT_URL doesn't point to a login page."
                    )
                return HttpResponseRedirect(redirect_to)
            return super().dispatch(request, *args, **kwargs)

        def get_success_url(self):
            url = self.get_redirect_url()
            return url or resolve_url(settings.LOGIN_REDIRECT_URL)

        def get_redirect_url(self):
            """Return the user-originating redirect URL if it's safe."""
            redirect_to = self.request.POST.get(
                self.redirect_field_name,
                self.request.GET.get(self.redirect_field_name, '')
            )
            url_is_safe = is_safe_url(
                url=redirect_to,
                allowed_hosts=self.get_success_url_allowed_hosts(),
                require_https=self.request.is_secure(),
            )
            return redirect_to if url_is_safe else ''

        def get_form_class(self):
            return self.authentication_form or self.form_class

        def get_form_kwargs(self):
            kwargs = super().get_form_kwargs()
            kwargs['request'] = self.request
            return kwargs

        def form_valid(self, form):
            """Security check complete. Log the user in."""
            auth_login(self.request, form.get_user())
            return HttpResponseRedirect(self.get_success_url())

        def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            current_site = get_current_site(self.request)
            context.update({
                self.redirect_field_name: self.get_redirect_url(),
                'site': current_site,
                'site_name': current_site.name,
                **(self.extra_context or {})
            })
            return context


class PasswordResetConfirmView(PasswordContextMixin, FormView):
    form_class = SetPasswordForm
    post_reset_login = True
    post_reset_login_backend = None
    success_url = reverse_lazy('password_reset_complete')
    template_name = 'registration/password_reset_confirm.html'
    title = ('Enter new password')
    token_generator = default_token_generator

    @method_decorator(sensitive_post_parameters())
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        assert 'uidb64' in kwargs and 'token' in kwargs

        self.validlink = False
        self.user = self.get_user(kwargs['uidb64'])

        if self.user is not None:
            token = kwargs['token']
            if token == INTERNAL_RESET_URL_TOKEN:
                session_token = self.request.session.get(INTERNAL_RESET_SESSION_TOKEN)
                if self.token_generator.check_token(self.user, session_token):
                    # If the token is valid, display the password reset form.
                    self.validlink = True
                    return super().dispatch(*args, **kwargs)
            else:
                if self.token_generator.check_token(self.user, token):
                    # Store the token in the session and redirect to the
                    # password reset form at a URL without the token. That
                    # avoids the possibility of leaking the token in the
                    # HTTP Referer header.
                    self.request.session[INTERNAL_RESET_SESSION_TOKEN] = token
                    redirect_url = self.request.path.replace(token, INTERNAL_RESET_URL_TOKEN)
                    return HttpResponseRedirect(redirect_url)

        # Display the "Password reset unsuccessful" page.
        return self.render_to_response(self.get_context_data())

    def get_user(self, uidb64):
        try:
            # urlsafe_base64_decode() decodes to bytestring
            uid = urlsafe_base64_decode(uidb64).decode()
            user = UserModel._default_manager.get(pk=uid)
        except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist, ValidationError):
            user = None
        return user

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.user
        return kwargs

    def form_valid(self, form):
        user = form.save()
        if form.is_valid():
            username = self.user
            password = form.cleaned_data['new_password1']
            u = User.objects.get(username=username)
            u.set_password(password)
            u.save()
        del self.request.session[INTERNAL_RESET_SESSION_TOKEN]
        if self.post_reset_login:
            auth_login(self.request, user, self.post_reset_login_backend)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.validlink:
            context['validlink'] = True
        else:
            context.update({
                'form': None,
                'title': 'Password reset unsuccessful',
                'validlink': False,
            })
        return context


def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('login')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'users_manager/password_change.html', {
        'form': form
    })

################################################################# ACCOUNTS

class SignUp(generic.CreateView):
    form_class = UserCreateForm
    success_url = reverse_lazy('login')
    template_name = 'users_manager/signup.html'

    def form_valid(self, form):
        user = form.save()
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            current_site = get_current_site(self.request)
            mail_subject = 'Activate the new user account.'
            message = render_to_string('users_manager/acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                'token': account_activation_token.make_token(user),
            })
            #to_email = form.cleaned_data.get('email')
            email = EmailMessage(
               mail_subject, message, to=['inao.latourrette@gmail.com'] #admin email
             )
            email.send()
            return render(self.request, 'users_manager/confirm_registration.html')

        else:
            form = UserCreateForm()
        return render(self.request, 'users_manager/signup.html', {'form': form})


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token): #Check if the token is correct
        user.is_active = True
        user.save()
        login(request, user)
        # return redirect('home')

        current_site = get_current_site(request)
        mail_subject = 'Account in MicroLearning Platform already activated'
        message = render_to_string('users_manager/user_link_confirmation.html', {
            'user': user,
            'domain': current_site.domain,
        })
        email = EmailMessage(
            mail_subject, message, to=[user.email]  # new user email
        )
        email.send()

        return HttpResponse('The selected account has been activated.')
    else:
        return HttpResponse('Activation link is invalid!')


class EditUserDataView(generic.TemplateView):
    template_name = "users_manager/edit_user_info.html"


    def get(self, request, *args, **kwargs):
        return render(request, template_name="users_manager/edit_user_info.html")


    def post(self, request, *args, **kwargs):
        connection = MongoClient(MONGODB_HOST, MONGODB_PORT)
        collection = connection[DB_NAME][COLLECTION_NAME]
        collection.update_one({"id": kwargs['id']}, {"$set": {"username": request.POST['userName'],
                                                    "first_name": request.POST['firstName'],
                                                    "last_name": request.POST['lastName'],
                                                    "email": request.POST['email']
                                                    }})
        return render(request, template_name="users_manager/user_data.html")



