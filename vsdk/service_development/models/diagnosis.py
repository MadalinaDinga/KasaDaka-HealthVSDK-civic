from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.http import Http404
from django.utils.translation import ugettext_lazy as _
from requests import HTTPError

from vsdk.service_development.models import CallSession, get_object_or_404, SelfCheckItem, Symptom

import logging

logger = logging.getLogger("mada")


class ResultItem(models.Model):
    """
    A result is a message element, associated to a self-check session
    """
    session = models.ForeignKey(CallSession, on_delete=models.PROTECT, related_name="session_result",
                                verbose_name=_('Call session'), null=True, blank=True)
    symptom_no = models.PositiveIntegerField(null=True, blank=True,
                                             verbose_name=_('Number of confirmed symptoms'),
                                             help_text=_("The number of reported symptoms."))
    risk_no = models.PositiveIntegerField(null=True, blank=True,
                                          verbose_name=_('Number of confirmed risk factors'),
                                          help_text=_("The number of reported risks."))
    is_exposed = models.BooleanField(
        verbose_name=_('User was exposed'),
        help_text=_("Whether the person has been exposed."),
        null=True, blank=True)
    infected_probability = models.FloatField(null=True, blank=True,
                                             validators=[MinValueValidator(0), MaxValueValidator(100)],
                                             verbose_name=_('Infection estimated probability'),
                                             help_text=_(
                                                 'The probability that the person has been infected, based on the configured parameters.'))
    is_infected_prediction = models.BooleanField(
        verbose_name=_('Self-check result'),
        help_text=_('Whether the person is believed to be infected after the self-check.'),
        null=True, blank=True)
    testing_recommended = models.BooleanField(
        verbose_name=_('Is testing recommended'),
        help_text=_('Whether testing is recommended.'),
        null=True, blank=True)
    testing_confirmation = models.BooleanField(
        verbose_name=_('Testing result'),
        help_text=_('Whether the person tested positive for COVID-19.'),
        null=True, blank=True)

    class Meta:
        verbose_name = _('Result Item')

    def __str__(self):
        return _(
            'Result: %s, exposure: %s, symptoms: %s, risks: %s, infected prediction: %s, confirmed: %s, testing result: %s') % (
                   self.session,
                   self.is_exposed,
                   self.symptom_no,
                   self.risk_no,
                   self.is_infected_prediction,
                   self.testing_confirmation is not None,
                   self.testing_confirmation,

               )


def update_is_exposed_for_session(session=None, is_exposed=None):
    result_item = None
    try:
        result_item = get_object_or_404(ResultItem, session=session)
        logger.debug("Retrieved result item - {}".format(result_item))
    except Exception as e:
        print("Could not retrieve result for session - {}".format(e))
        result_item = ResultItem.objects.create()  # create result item for session
        result_item.session = session
        logger.debug("Created new result item - {}".format(result_item))
    finally:
        if not result_item.is_exposed:  # can be updated only if False
            result_item.is_exposed = is_exposed
            logger.debug("Is exposed is - {}".format(is_exposed))
        result_item.save()
        return result_item


def update_or_create_result_item_for_session(session=None, symptom_no=None, risk_no=None, is_exposed=None,
                                             infected_probability=None, is_infected_prediction=None,
                                             testing_recommended=None):
    result_item = None
    try:
        result_item = get_object_or_404(ResultItem, session=session)
        logger.debug("Retrieved result item - {}".format(result_item))
    except Exception as e:
        print("Could not retrieve result for session - {}".format(e))
        result_item = ResultItem.objects.create()  # create result item for session
        result_item.session = session
        logger.debug("Created new result item - {}".format(result_item))
    finally:
        # set result fields
        if symptom_no:
            result_item.symptom_no = symptom_no
        if risk_no:
            result_item.risk_no = risk_no
        if is_exposed:
            result_item.is_exposed = is_exposed
        if infected_probability:
            result_item.infected_probability = infected_probability
        if is_infected_prediction:
            result_item.is_infected_prediction = is_infected_prediction
        if testing_recommended:
            result_item.testing_recommended = testing_recommended

        logger.debug("Saving result item - {}".format(result_item))
        result_item.save()
        return result_item


class DiagnosisConfigParameters(models.Model):
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

    class Meta:
        verbose_name_plural = _('Diagnosis Configurable Parameters')

    def __str__(self):
        return _('Infected probability benchmark: %s - symptoms count benchmark: %s') % (
            self.infected_probability_benchmark, self.symptom_no_benchmark)


def compute_result(session):
    logger.debug("Started result computation")

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
        if choice.symptom and not choice.risk and not choice.symptom.is_severe:  # process non-severe symptom
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
    logger.debug("Symptom_count {} - benchmark {}".format(is_symptom_count_above_benchmark,
                                                          DiagnosisConfigParameters.symptom_no_benchmark))
    logger.debug("WAVG {} - benchmark {}".format(is_wavg_above_benchmark,
                                                 DiagnosisConfigParameters.infected_probability_benchmark))

    is_suspect = is_symptom_count_above_benchmark or is_wavg_above_benchmark
    logger.debug("Is suspect {}".format(is_suspect))

    # create new result item
    result_item = update_or_create_result_item_for_session(session, symptoms_count, risks_count, False, symptoms__wavg,
                                                           is_suspect, is_suspect)
    return result_item
