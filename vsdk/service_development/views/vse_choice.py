from django.shortcuts import render, get_object_or_404, get_list_or_404, redirect
from django.views.generic import TemplateView

from ..models import *

import logging

logger = logging.getLogger("mada")


class ChoiceSelection(TemplateView):

    def choice_options_resolve_redirect_urls(self, choice_options, session):
        """
        Returns all possible redirect URLs for *AFTER* the choice option selection process
        """
        choice_options_redirection_urls = []
        for choice_option in choice_options:
            logger.debug("Choice option {}".format(choice_option))
            redirect_url = choice_option.redirect.get_absolute_url(session)
            choice_options_redirection_urls.append(redirect_url)
        return choice_options_redirection_urls

    def choice_options_resolve_voice_labels(self, choice_options, language):
        """
        Returns a list of voice labels belonging to the provided list of choice_options.
        """
        choice_options_voice_labels = []
        for choice_option in choice_options:
            choice_options_voice_labels.append(choice_option.get_voice_fragment_url(language))
        return choice_options_voice_labels

    def choice_generate_context(self, choice_element, session):
        """
        Returns a dict that can be used to generate the choice VXML template
        choice = this Choice element object
        choice_voice_label = the resolved Voice Label URL for this Choice element
        choice_options = iterable of ChoiceOption object belonging to this Choice element
        choice_options_voice_labels = list of resolved Voice Label URL's referencing to the choice_options in the same position
        choice_options_redirect_urls = list of resolved redirection URL's referencing to the choice_options in the same position
            """
        choice_options = choice_element.choice_options.all()
        language = session.language
        choice_element_config = {'skip_reading_choice_options': choice_element.skip_reading_choice_options}
        # This is the redirect URL to POST the selected choice option
        redirect_url_POST = reverse('service-development:choice', args=[choice_element.id, session.id])

        context = {'choice': choice_element,
                   'choice_voice_label': choice_element.get_voice_fragment_url(language),
                   'choice_options': choice_options,
                   'config': choice_element_config,
                   'choice_options_voice_labels': self.choice_options_resolve_voice_labels(choice_options, language),
                   'choice_options_redirect_urls': self.choice_options_resolve_redirect_urls(choice_options, session),
                   'language': language,
                   'redirect_url': redirect_url_POST
                   }
        return context

    def get(self, request, element_id, session_id):
        """
           Asks the user to select one of the choice options.
        """
        logger.debug("REQUEST {}".format(request))
        logger.debug("Session ID {}".format(session_id))

        choice_element = get_object_or_404(Choice, pk=element_id)
        session = get_object_or_404(CallSession, pk=session_id)
        session.record_step(choice_element)
        context = self.choice_generate_context(choice_element, session)

        logger.debug("Context {} - Session {}".format(context, session))
        logger.debug("Render choice.xml")
        return render(request, 'choice.xml', context, content_type='text/xml')

    def post(self, request, element_id, session_id):
        try:
            """
            Saves the chosen option to a new session self-check item
            """
            logger.debug("POST request {} - body {}".format(request, request.POST))
            logger.debug("Element ID {} - Session ID {}".format(element_id, session_id))

            if 'choice_option' not in request.POST:
                logger.error("Incorrect request, choice option ID not set")
                raise ValueError('Incorrect request, choice option ID not set')

            if 'option_redirect' not in request.POST:
                logger.error("Incorrect request, redirect URL not set")
                raise ValueError('Incorrect request, redirect URL not set')

            logger.debug("Choice option {} - redirect URL {}".format(request.POST['choice_option'], request.POST['option_redirect']))

            choice_element = get_object_or_404(Choice, pk=element_id)
            if choice_element.is_persistent_choice:
                # Save choice option for persistent elements in a self-check item
                is_confirmed = request.POST['choice_option'] == '1'
                logger.debug("Is confirmed {}".format(is_confirmed))
                session = get_object_or_404(CallSession, pk=session_id)
                logger.debug("Linked session {}".format(session))
                check_item = lookup_or_create_self_check_item(None, session, choice_element, is_confirmed)
                logger.debug("Saved self-check item {}".format(check_item))

            return HttpResponseRedirect(request.POST['option_redirect'])

        except Exception as ex:
            logger.error("Saving the choice option failed with error message - {}".format(ex))
            return None
