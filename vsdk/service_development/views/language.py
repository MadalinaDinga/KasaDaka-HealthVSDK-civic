from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views.generic import TemplateView
from django.http.response import HttpResponseRedirect

from ..models import CallSession, Language

import logging

logger = logging.getLogger("mada")


class LanguageSelection(TemplateView):

    def render_language_selection_form(self, request, session, redirect_url):
        languages = session.service.supported_languages.all()

        # This is the redirect URL to POST the language selected
        redirect_url_POST = reverse('service-development:language-selection', args=[session.id])

        # This is the redirect URL for *AFTER* the language selection process
        pass_on_variables = {'redirect_url': redirect_url}

        context = {'languages': languages,
                   'redirect_url': redirect_url_POST,
                   'pass_on_variables': pass_on_variables
                   }
        logger.error("CONTEXT render")
        logger.error(context)
        return render(request, 'language_selection.xml', context, content_type='text/xml')

    def get(self, request, session_id):
        """
        Asks the user to select one of the supported languages.
        """

        logger.debug("REQUEST {}".format(request))
        logger.debug("Session ID {}".format(session_id))
        try:
            session = get_object_or_404(CallSession, pk=session_id)
            if 'redirect_url' in request.GET:
                redirect_url = request.GET['redirect_url']
            return self.render_language_selection_form(request, session, redirect_url)
        except Exception as ex:
            logger.error(ex)
            return None

    def post(self, request, session_id):
        try:
            """
            Saves the chosen language to the session
            """
            if 'redirect_url' in request.POST:
                redirect_url = request.POST['redirect_url']
            else:
                logger.error("Incorrect request, redirect_url not set")
                raise ValueError('Incorrect request, redirect_url not set')
            if 'language_id' not in request.POST:
                logger.error("Incorrect request, language ID not set")
                raise ValueError('Incorrect request, language ID not set')

            session = get_object_or_404(CallSession, pk=session_id)
            voice_service = session.service
            language = get_object_or_404(Language, pk=request.POST['language_id'])

            session._language = language
            session.save()

            session.record_step(None, "Language selected, %s" % language.name)

            return HttpResponseRedirect(redirect_url)
        except Exception as ex:
            logger.error("POST")
            logger.error(ex)
            return None
