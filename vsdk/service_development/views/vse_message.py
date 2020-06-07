from django.shortcuts import render, get_object_or_404, get_list_or_404, redirect

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


def message_presentation_generate_result_context(message_presentation_element, session, result_id):
    language = session.language
    message_voice_fragment_url = message_presentation_element.get_voice_fragment_url(language)
    redirect_url = message_presentation_get_redirect_url(message_presentation_element, session)
    context = {'message_voice_fragment_url': message_voice_fragment_url,
               'redirect_url': redirect_url,
               'result': result_id}
    return context


def message_presentation(request, element_id, session_id):
    message_presentation_element = get_object_or_404(MessagePresentation, pk=element_id)
    session = get_object_or_404(CallSession, pk=session_id)
    session.record_step(message_presentation_element)
    context = message_presentation_generate_context(message_presentation_element, session)

    if message_presentation_element.redirects_to_result:
        logger.debug("Started result computation")

        # TODO: move logic to DiagnosisConfigParameters
        # Get all self-check items (symptoms/risks) for session
        session_self_check_items_set = SelfCheckItem.objects.filter(session=session)
        logger.debug("Self-check items for session {}".format(session_self_check_items_set))

        symptoms_count = 0  # session_self_check_symptoms_set.count()
        risks_count = 0  # session_self_check_risks_set.count()

        # Compute the weighted average of the confirmed symptoms
        symptoms__wavg = 0
        symptoms__wavg_denominator = 0
        for check in session_self_check_items_set:
            choice = check.choice_element
            logger.debug("Choice item {}".format(choice))
            if choice.symptom and not choice.risk:  # process symptom
                symptoms_count += 1
                sympt_id = choice.symptom.id
                logger.debug("Symptom details - name {} ID {}".format(choice.symptom.name, sympt_id))

                sympt_occurrence = get_object_or_404(Symptom, pk=sympt_id).symptom_occurrence_percent
                symptoms__wavg_denominator += sympt_occurrence
                logger.debug("Has symptom {}".format(check.has_symptom))
                symptoms__wavg += int(check.has_symptom) * sympt_occurrence

            if not check.choice_element.symptom and check.choice_element.risk:  # process risk
                risks_count += 1

        if symptoms_count > 0:
            symptoms__wavg /= symptoms__wavg_denominator
        logger.debug("WAVG - estimated probability {}".format(symptoms__wavg))
        logger.debug("User reported symptoms count {}".format(symptoms_count))
        logger.debug("User reported risks count {}".format(risks_count))

        # compare wavg and sympt no with configuration benchmarks
        diagnostic_params = DiagnosisConfigParameters.objects.all().first()
        logger.debug("Retrieved configuration - {}".format(diagnostic_params))

        is_symptom_count_above_benchmark = symptoms_count > diagnostic_params.symptom_no_benchmark
        is_wavg_above_benchmark = symptoms__wavg > diagnostic_params.infected_probability_benchmark
        logger.debug("Symptom_count {} - benchmark {}".format(is_symptom_count_above_benchmark, DiagnosisConfigParameters.symptom_no_benchmark))
        logger.debug("WAVG {} - benchmark {}".format(is_wavg_above_benchmark, DiagnosisConfigParameters.infected_probability_benchmark))

        is_suspect = is_symptom_count_above_benchmark or is_wavg_above_benchmark
        logger.debug("Is suspect {}".format(is_suspect))

        # create new result item
        result_item = update_or_create_result_item_for_session(session, symptoms_count, risks_count, False, symptoms__wavg, is_suspect, is_suspect)
        logger.debug("Saved result {}".format(result_item))

        # TODO: play corresponding audios
        return render(request, 'retrieve_result.xml', context, content_type='text/xml')

    return render(request, 'message_presentation.xml', context, content_type='text/xml')
