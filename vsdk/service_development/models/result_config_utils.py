from django.shortcuts import get_object_or_404
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _
from vsdk.service_development.models import Symptom, SelfCheckItem, update_or_create_result_item_for_session

import logging

logger = logging.getLogger("mada")


class ResultConfig(models.Model):
    """
       An entity containing the diagnosis configurable parameters and infection prediction helpers.
    """
    infected_probability_benchmark = models.FloatField(null=True, blank=True,
                                                       validators=[MinValueValidator(0), MaxValueValidator(100)],
                                                       help_text=_(
                                                           "Point of reference against which the infection probability is compared and conclusions may be drawn whether the person is infected or not."))
    symptom_no_benchmark = models.PositiveIntegerField(null=True, blank=True,
                                                       help_text=_(
                                                           "Point of reference against which the number of reported symptoms per session is computed and conclusions may be drawn whether the person is infected or not."))
    result_negative_voice_label = models.ForeignKey('VoiceLabel',
                                                    on_delete=models.PROTECT,
                                                    verbose_name=_('User is not suspect voice label'),
                                                    related_name='result_negative_voice_label',
                                                    help_text=_("A Voice Label for negative diagnosis result"))
    result_positive_voice_label = models.ForeignKey('VoiceLabel',
                                                    on_delete=models.PROTECT,
                                                    verbose_name=_('User is suspect voice label'),
                                                    related_name='result_positive_voice_label',
                                                    help_text=_("A Voice Label for positive diagnosis result"))
    no_testing_voice_label = models.ForeignKey('VoiceLabel',
                                               on_delete=models.PROTECT,
                                               verbose_name=_('Testing not necessary voice label'),
                                               related_name='no_testing_voice_label',
                                               help_text=_("A Voice Label for no testing necessary"))
    yes_testing_voice_label = models.ForeignKey('VoiceLabel',
                                                on_delete=models.PROTECT,
                                                verbose_name=_('Testing recommended voice label'),
                                                related_name='yes_testing_voice_label',
                                                help_text=_("A Voice Label for testing needed"))
    yes_risks_voice_label = models.ForeignKey('VoiceLabel',
                                              on_delete=models.PROTECT,
                                              verbose_name=_('Risks warning voice label'),
                                              related_name='yes_risks_voice_label',
                                              help_text=_("A Voice Label for risks warning"))
    yes_contact_voice_label = models.ForeignKey('VoiceLabel',
                                                on_delete=models.PROTECT,
                                                verbose_name=_('Exposure warning voice label'),
                                                related_name='yes_contact_voice_label',
                                                help_text=_("A Voice Label for exposure or contact warning"),
                                                blank=True, null=True)

    class Meta:
        verbose_name_plural = _('Result Configuration')

    def __str__(self):
        return _('Infected probability benchmark: %s - symptoms count benchmark: %s') % (
            self.infected_probability_benchmark, self.symptom_no_benchmark)

    @property
    def get_result_interface_voice_label_url_dict(self):
        """
        Returns a dictionary containing all URLs of Voice
        Fragments of the hardcoded result interface audio fragments.
        """
        result_interface_voice_labels = {
            'result_positive_voice_label': self.result_positive_voice_label,
            'result_negative_voice_label': self.result_negative_voice_label,
            'no_testing_voice_label': self.no_testing_voice_label,
            'yes_testing_voice_label': self.yes_testing_voice_label,
            'yes_risks_voice_label': self.yes_risks_voice_label,
            'exposure or contact': self.yes_contact_voice_label
        }
        for k, v in result_interface_voice_labels.items():
            result_interface_voice_labels[k] = v.get_voice_fragment_url(self)

        return result_interface_voice_labels


# Utils - methods for diagnosis computation
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
    diagnostic_params = ResultConfig.objects.all().first()
    logger.debug("Retrieved configuration - {}".format(diagnostic_params))

    is_symptom_count_above_benchmark = symptoms_count > diagnostic_params.symptom_no_benchmark
    is_wavg_above_benchmark = symptoms_wavg > diagnostic_params.infected_probability_benchmark
    logger.debug("Symptom_count {} - benchmark {}".format(is_symptom_count_above_benchmark,
                                                          ResultConfig.symptom_no_benchmark))
    logger.debug("WAVG {} - benchmark {}".format(is_wavg_above_benchmark,
                                                 ResultConfig.infected_probability_benchmark))

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
