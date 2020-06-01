from django.db import models
from django.utils.translation import ugettext_lazy as _, ugettext

from vsdk.service_development.models import CallSession, Symptom, Risk, Choice


class SelfCheckItem(models.Model):
    """
    User that belongs to a Voice Service on this system
    """
    session = models.ForeignKey(CallSession, on_delete=models.CASCADE, related_name="check_item_session")
    symptom = models.ForeignKey(Symptom, on_delete=models.PROTECT, related_name="symptom",
                                verbose_name=_('Symptom'), null=True)
    risk = models.ForeignKey(Risk, on_delete=models.PROTECT, related_name="risk",
                             verbose_name=_('Risk'), null=True)
    choice_element = models.ForeignKey(Choice, on_delete=models.PROTECT, related_name="choice_element",
                                       verbose_name=_('ChoiceElement'))
    has_symptom = models.BooleanField(null=True)

    class Meta:
        verbose_name = _('Self-Check')

    def __str__(self):
        if self.risk:
            return _('SelfCheckItem: %s, risk %s, has_symptom %s') % self.session, self.risk.name, self.has_symptom
        else:
            return _(
                'SelfCheckItem: %s, symptom %s, has_symptom %s') % self.session, self.symptom.name, self.has_symptom
