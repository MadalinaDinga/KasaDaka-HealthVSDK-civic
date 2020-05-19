import logging
from django.http.response import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import TemplateView
from ..models.user import lookup_kasadaka_user_by_username, KasaDakaUser

from ..models import CallSession, Language

logger = logging.getLogger("mada")


class UserAuthentication(TemplateView):

    def render_auth_form(self, request, session, redirect_url):
        # This is the redirect URL to POST the username and password selected
        redirect_url_POST = reverse('service-development:kasadaka-user-auth', args=[session.id])
        redirect_url_POST = reverse('service-development:language-selection', args=[session.id])
        # This is the redirect URL for *AFTER* the username and password input process
        pass_on_variables = {'redirect_url': redirect_url}
        language = session.language

        context = {'language': language,
                   'redirect_url': redirect_url_POST,
                   'pass_on_variables': pass_on_variables
                   }
        logger.debug("Context {} - Request {} - Session {}".format(context, request, session))
        logger.debug("Render auth.xml")
        return render(request, 'auth.xml', context, content_type='text/xml')

    def get(self, request, session_id):
        """
        Asks the user to type his username and password (digits only).
        """
        logger.debug("Request {} - Session id {}".format(request, session_id))
        logger.debug("Asking for credentials")

        session = get_object_or_404(CallSession, pk=session_id)
        if 'redirect_url' in request.GET:
            redirect_url = request.GET['redirect_url']
        return self.render_auth_form(request, session, redirect_url)

    def post(self, request, session_id):
        """
        Checks the user by username and password
        Saves the username to the current session, if authentication is valid
        Otherwise, retrieves authentication error
        """
        logger.debug("Request {} - Session id {}".format(request, session_id))
        logger.debug("Checking credentials")

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

        logger.debug("Redirecting to {}".format(redirect_url))
        # Return to the start of voice service
        return HttpResponseRedirect(redirect_url)
