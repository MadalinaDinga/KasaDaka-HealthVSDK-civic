from vsdk.service_development.models import get_object_or_404, SelfCheckItem, Symptom, \
    DiagnosisConfigParameters, update_or_create_result_item_for_session

import logging

logger = logging.getLogger("mada")


def process_symptoms_risks(session_self_check_items):
    """
     Analyse user responses (reported symptoms and risks).
     Returns the non-severe symptoms count, risks count and the weighted average of symptom occurrence.
    """
    nonsevere_symptoms_count = 0  # session_self_check_symptoms_set.count()
    risks_count = 0  # session_self_check_risks_set.count()
    symptoms_wavg = 0
    symptoms__wavg_denominator = 0

    for check in session_self_check_items:
        choice = check.choice_element
        logger.debug("Choice item {}".format(choice))
        if choice.symptom and not choice.risk and not choice.symptom.is_severe:  # process non-severe symptom
            nonsevere_symptoms_count += 1
            sympt_id = choice.symptom.id
            logger.debug("Symptom details - name {} ID {}".format(choice.symptom.name, sympt_id))

            sympt_occurrence = get_object_or_404(Symptom, pk=sympt_id).symptom_occurrence_percent
            symptoms__wavg_denominator += sympt_occurrence
            logger.debug("Has symptom {}".format(check.has_symptom))
            symptoms_wavg += int(check.has_symptom) * sympt_occurrence

        if not check.choice_element.symptom and check.choice_element.risk:  # process risk
            risks_count += 1

    if nonsevere_symptoms_count > 0:
        symptoms_wavg /= symptoms__wavg_denominator
    logger.debug("WAVG - estimated probability {}".format(symptoms_wavg))
    logger.debug("User reported {} non-severe symptoms.".format(nonsevere_symptoms_count))
    logger.debug("User reported {} risks.".format(risks_count))

    return nonsevere_symptoms_count, risks_count, symptoms_wavg


def compute_self_check_result(symptoms_count, symptoms_wavg):
    """
     Compute the self-check result - if the user might be infected.
    """
    # Compare wavg and sympt no with configuration benchmarks
    diagnostic_params = DiagnosisConfigParameters.objects.all().first()
    logger.debug("Retrieved configuration - {}".format(diagnostic_params))

    is_symptom_count_above_benchmark = symptoms_count > diagnostic_params.symptom_no_benchmark
    is_wavg_above_benchmark = symptoms_wavg > diagnostic_params.infected_probability_benchmark
    logger.debug("Symptom_count {} - benchmark {}".format(is_symptom_count_above_benchmark,
                                                          DiagnosisConfigParameters.symptom_no_benchmark))
    logger.debug("WAVG {} - benchmark {}".format(is_wavg_above_benchmark,
                                                 DiagnosisConfigParameters.infected_probability_benchmark))

    return is_symptom_count_above_benchmark or is_wavg_above_benchmark


def compute_result(session):
    logger.debug("Started result computation")

    # Get all self-check items (symptoms/risks) for session
    session_self_check_items_set = SelfCheckItem.objects.filter(session=session)
    logger.debug("Self-check items for session {}".format(session_self_check_items_set))

    # Compute the weighted average of the confirmed symptoms
    symptoms_count, risks_count, symptoms_wavg = process_symptoms_risks(session_self_check_items_set)

    # Compute self-check result
    is_suspect = compute_self_check_result(symptoms_count, symptoms_wavg)
    logger.debug("Is suspect {}".format(is_suspect))

    is_testing_recommended = is_suspect  # Recommend testing if there is a fair suspicion of having contacted the virus

    # save result information
    result_item = update_or_create_result_item_for_session(session, symptoms_count, risks_count, False,
                                                           symptoms_wavg,
                                                           is_suspect, is_testing_recommended)
    return result_item
