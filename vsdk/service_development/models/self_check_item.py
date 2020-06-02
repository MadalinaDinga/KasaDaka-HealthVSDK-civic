from django.db import models
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _, ugettext

from vsdk.service_development.models import CallSession, Symptom, Risk, Choice


class SelfCheckItem(models.Model):
    """
    User that belongs to a Voice Service on this system
    """
    session = models.ForeignKey(CallSession, on_delete=models.CASCADE, related_name="check_item_session")
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


def lookup_or_create_self_check_item(self_check_item_id=None, session_id=None, choice_element_id=None, has_symptom=None):
    if self_check_item_id:
        self_check_item = get_object_or_404(SelfCheckItem, pk=self_check_item_id)
    else:
        if not session_id:
            raise ValueError('Session ID missing for self-check item')
        if not choice_element_id:
            raise ValueError('No choice element associated with the self-check item')
        if not has_symptom:
            raise ValueError('No answer associated to the self-check item')

        self_check_item = SelfCheckItem.objects.create(
            session=session_id,
            choice_element=choice_element_id,
            has_symptom=has_symptom
        )
        self_check_item.save()
    return self_check_item
