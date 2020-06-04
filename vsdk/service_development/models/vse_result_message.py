from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _, ugettext

from vsdk.service_development.models import CallSession


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
    is_infected_confirmation = models.BooleanField(
        verbose_name=_('Testing result'),
        help_text=_('Whether the person tested positive for COVID-19.'),
        null=True, blank=True)

    class Meta:
        verbose_name = _('Result Item')

    def __str__(self):
        return _('Result: %s, infected prediction: %s, confirmed: %s, testing result: %s') % (
            self.session, self.has_infection_predicted,
            self.has_infection_confirmed is not None,
            self.has_infection_confirmed)


class Diagnosis(models.Model):
    """
       An entity containing the outcome computation configurable parameters and a diagnostic prediction utility.
    """
    infected_probability_benchmark = models.FloatField(null=True, blank=True,
                                                       validators=[MinValueValidator(0), MaxValueValidator(100)],
                                                       help_text=_(
                                                           "Point of reference against which the infection probability is compared and conclusions may be drawn whether the person is infected or not."))
    symptom_no_benchmark = models.PositiveIntegerField(null=True, blank=True,
                                                       help_text=_(
                                                           "Point of reference against which the number of reported symptoms per session is computed and conclusions may be drawn whether the person is infected or not."))

    class Meta:
        verbose_name_plural = _('Outcome Configuration')

