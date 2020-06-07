from django.shortcuts import render

from ..models import *


def message_presentation_get_redirect_url(message_presentation_element, session):
    if not message_presentation_element.final_element:
        return message_presentation_element.redirect.get_absolute_url(session)
    else:
        return None


def message_presentation_generate_context(message_presentation_element, session):
    language = session.language
    message_voice_fragment_url = message_presentation_element.get_voice_fragment_url(language)
    redirect_url = message_presentation_get_redirect_url(message_presentation_element, session)
    context = {'message_voice_fragment_url': message_voice_fragment_url,
               'redirect_url': redirect_url}
    return context


def message_presentation_generate_result_context(message_presentation_element, is_infected_prediction,
                                                 is_testing_recommended, has_risk, session):
    language = session.language
    redirect_url = message_presentation_get_redirect_url(message_presentation_element, session)
    context = {
        'language': language,
        'is_infected_prediction': is_infected_prediction,
        'is_testing_recommended': is_testing_recommended,
        'has_risk': has_risk,
        'redirect_url': redirect_url
    }
    return context


def message_presentation(request, element_id, session_id):
    message_presentation_element = get_object_or_404(MessagePresentation, pk=element_id)
    session = get_object_or_404(CallSession, pk=session_id)
    session.record_step(message_presentation_element)
    context = message_presentation_generate_context(message_presentation_element, session)

    if message_presentation_element.redirects_to_result:
        result_item = compute_result(session)
        logger.debug("Saved result {}".format(result_item))

        context = message_presentation_generate_result_context(message_presentation_element,
                                                               result_item.is_infected_prediction,
                                                               result_item.testing_recommended, result_item.risk_no > 0,
                                                               session)
        return render(request, 'retrieve_result.xml', context, content_type='text/xml')

    return render(request, 'message_presentation.xml', context, content_type='text/xml')
