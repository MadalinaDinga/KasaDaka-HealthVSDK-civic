from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _

from vsdk.service_development.models import CallSession, get_object_or_404

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
        verbose_name=_('Exposed'),
        help_text=_("Whether the person has been exposed to the virus."),
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
        verbose_name=_('Predicted result was confirmed by testing'),
        help_text=_('Whether the person tested positive for COVID-19.'),
        null=True, blank=True)

    class Meta:
        verbose_name_plural = _('Self-Check Results')

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
        if is_exposed is not None:
            result_item.is_exposed = is_exposed
        if infected_probability is not None:
            logger.debug("Set infection probability - {}".format(infected_probability))
            result_item.infected_probability = infected_probability
        if is_infected_prediction is not None:
            logger.debug("Set infection prediction - {}".format(is_infected_prediction))
            result_item.is_infected_prediction = is_infected_prediction
        if testing_recommended is not None:
            logger.debug("Set testing recommendation - {}".format(testing_recommended))
            result_item.testing_recommended = testing_recommended

        logger.debug("Saving result item - {}".format(result_item))
        result_item.save()
        return result_item

