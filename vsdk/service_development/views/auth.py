import logging
from django.http.response import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import TemplateView
from ..models.user import lookup_kasadaka_user_by_username, KasaDakaUser

from ..models import CallSession, Language

logger = logging.getLogger("mada")


class UserAuthentication(TemplateView):

    def render_auth_form(self, request, session):
        try:
            # This is the redirect URL to POST the username and password selected
            redirect_url_POST = reverse('service-development:kasadaka-user-auth', args=[session.id])

            # This is the redirect URL for *AFTER* the username and password input process
            pass_on_variables = {'redirect_url': reverse('service-development:voice-service', args=[session.service.id, session.id])}
            language = session.language

            context = {
                       'redirect_url': redirect_url_POST,
                       'pass_on_variables': pass_on_variables,
                       'language': language,
                       }
            logger.debug("Context {} - Request {} - Session {}".format(context, request, session))
            logger.debug("auth.xml")
            return render(request, 'auth.xml', context, content_type='text/xml')

        except Exception as ex:
            logger.error("EXCEPYIasd")
            logger.error(ex)

    def get(self, request, session_id):
        """
        Asks the user to type his username and password (digits only).
        """
        session = get_object_or_404(CallSession, pk=session_id)
        return self.render_auth_form(request, session)

    def post(self, request, session_id):
        """
        Checks the user by username and password
        Saves the username to the current session, if authentication is valid
        Otherwise, retrieves authentication error
        """
        if 'redirect_url' in request.POST:
            redirect_url = request.POST['redirect_url']
        else:
            raise ValueError('Incorrect request, redirect_url not set')
        if 'username' not in request.POST:
            raise ValueError('Incorrect request, username not set')
        if 'pass' not in request.POST:
            raise ValueError('Incorrect request, password not set')

        session = get_object_or_404(CallSession, pk=session_id)
        voice_service = session.service

        in_username = request.POST['username']
        in_password = request.POST['pass']

        user = lookup_kasadaka_user_by_username(in_username, voice_service)

        if user is None:
            session.record_step(None, "Authentication failed - No user associated to this service, %s" % in_username)
            raise ValueError('No user associated to this service')

        if not user.is_valid_credentials(in_username, in_password, voice_service):
            session.record_step(None, "Authentication failed - Invalid credentials, %s" % in_username)
            raise ValueError('Invalid credentials')

        session.user = user.username
        session.save()

        session.record_step(None, "Authentication successful, %s" % in_username)

        # Return to the start of voice service
        return redirect('service-development:voice-service', voice_service_id=session.service.id, session_id=session_id)