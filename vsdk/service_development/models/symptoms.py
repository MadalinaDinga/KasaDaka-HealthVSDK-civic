from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _, ugettext


class Symptom(models.Model):
    """
    User that belongs to a Voice Service on this system
    """
    name = models.CharField(_('Name'), max_length=100)
    description = models.CharField(_('Description'), max_length=1000, blank=True)
    _percentage_severe = models.FloatField(
        _('Percentage severe'),
        null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text=_(
            "The percentage of people with severe COVID-19 reporting the symptom."))
    _percentage_nonsevere = models.FloatField(
        _('Percentage non-severe'),
        null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text=_(
            "The percentage of people with non-severe COVID-19 reporting the symptom."))
    is_severe = models.BooleanField(
        verbose_name=_('Is severe'),
        help_text=_('Whether the symptom is considered severe.'),
        default=False)

    @property
    def symptom_occurrence_percent(self):
        """
        Returns the average of percentage severe and percentage nonsevere.
        """
        return (self._percentage_severe + self._percentage_nonsevere) / 2

    class Meta:
        verbose_name_plural = _('Symptoms')

    def __str__(self):
        return _('Symptom: %s') % self.name

    def is_valid(self):
        return len(self.validator()) == 0

    is_valid.boolean = True
    is_valid.short_description = _('Is valid')

    def validator(self):
        errors = []
        if not self.name:
            errors.append(ugettext('No symptom name'))
        if not self._percentage_severe:
            errors.append(ugettext('No percentage for severe cases'))
        if not self._percentage_nonsevere:
            errors.append(ugettext('No percentage for non-severe cases'))

        # deduplicate errors
        errors = list(set(errors))
        return errors
