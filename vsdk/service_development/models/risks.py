from django.db import models
from django.utils.translation import ugettext_lazy as _, ugettext


class Risk(models.Model):
    """
    User that belongs to a Voice Service on this system
    """
    name = models.CharField(_('Name'), max_length=100)
    description = models.CharField(max_length=1000, blank=True)

    class Meta:
        verbose_name = _('Risk')

    def __str__(self):
        return _('Risk: %s') % self.name

    def is_valid(self):
        return len(self.validator()) == 0

    is_valid.boolean = True
    is_valid.short_description = _('Is valid')

    def validator(self):
        errors = []
        if not self.name:
            errors.append(ugettext('No symptom name'))

        # deduplicate errors
        errors = list(set(errors))
        return errors
