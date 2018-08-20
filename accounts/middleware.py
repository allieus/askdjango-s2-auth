from importlib import import_module
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import logout as auth_logout
from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin
from .models import UserSession

SessionStore = import_module(settings.SESSION_ENGINE).SessionStore


class KickMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        is_user_logged_in = getattr(request.user, 'is_user_logged_in', False)

        if is_user_logged_in:
            for user_session in UserSession.objects.filter(user=request.user):
                session_key = user_session.session_key
                session = SessionStore(session_key)
                # session.delete()
                session['kicked'] = True
                session.save()
                user_session.delete()

            session_key = request.session.session_key  # 로그인 전 세션
            UserSession.objects.create(user=request.user, session_key=session_key)

        return response


class KickedMiddleware(MiddlewareMixin):
    def process_request(self, request):
        kicked = request.session.pop('kicked', None)
        if kicked:
            messages.info(request, '동일 아이디로 다른 브라우저 웹사이트에서 로그인이 감지되어, 강제 로그아웃되었습니다.')
            auth_logout(request)
            return redirect(settings.LOGIN_URL)

