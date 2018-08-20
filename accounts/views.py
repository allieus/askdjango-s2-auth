from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView, PasswordChangeView
from django.http import Http404
from django.urls import reverse_lazy
from django.utils.http import urlsafe_base64_decode
from django.shortcuts import redirect, render, resolve_url
from django.views.generic import CreateView, UpdateView
from .forms import SignupForm, ProfileForm
from .models import Profile


'''
def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)  # 로그인 처리
            next_url = request.GET.get('next') or 'profile'
            return redirect(next_url)
    else:
        form = SignupForm()
    return render(request, 'accounts/signup.html', {
        'form': form,
    })
'''

class SignupView(CreateView):
    model = User
    form_class = SignupForm
    template_name = 'accounts/signup.html'

    def get_success_url(self):
        next_url = self.request.GET.get('next') or 'profile'
        return resolve_url(next_url)

    def form_valid(self, form):
        user = form.save()
        auth_login(self.request, user)
        return redirect(self.get_success_url())

signup = SignupView.as_view()


@login_required
def profile(request):
    return render(request, 'accounts/profile.html')


class ProfileUpdateView(UpdateView, LoginRequiredMixin):
    model = Profile
    form_class = ProfileForm
    success_url = reverse_lazy('profile')

    def get_object(self):
        return self.request.user.profile

profile_edit = ProfileUpdateView.as_view()


class RequestLoginViaUrlView(PasswordResetView):
    template_name = 'accounts/request_login_via_url_form.html'
    title = '이메일을 통한 로그인'
    email_template_name = 'accounts/login_via_url.html'
    success_url = settings.LOGIN_URL


def login_via_url(request, uidb64, token):
    User = get_user_model()
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        current_user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist, ValidationError):
        raise Http404

    if default_token_generator.check_token(current_user, token):
        auth_login(request, current_user)
        messages.info(request, '로그인이 승인되었습니다.')
        return redirect('root')

    messages.error(request, '로그인이 거부되었습니다.')
    return redirect('root')


class MyPasswordChangeView(PasswordChangeView):
    success_url = reverse_lazy('profile')
    template_name = 'accounts/password_change_form.html'

    def form_valid(self, form):
        messages.info(self.request, '암호 변경을 완료했습니다.')
        return super().form_valid(form)


class MyPasswordResetView(PasswordResetView):
    success_url = reverse_lazy('login')
    template_name = 'accounts/password_reset_form.html'
    # email_template_name = ...
    # html_email_template_name = ...

    def form_valid(self, form):
        messages.info(self.request, '암호 변경 메일을 발송했습니다.')
        return super().form_valid(form)


class MyPasswordResetConfirmView(PasswordResetConfirmView):
    success_url = reverse_lazy('login')
    template_name = 'accounts/password_reset_confirm.html'

    def form_valid(self, form):
        messages.info(self.request, '암호 리셋을 완료했습니다.')
        return super().form_valid(form)

