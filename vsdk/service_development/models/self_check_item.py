from django.db import models
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _

from vsdk.service_development.models import CallSession, Choice

import logging

logger = logging.getLogger("mada")


class SelfCheckItem(models.Model):
    """
    A self-check item is a self-reported item, either a symptom, or a risk factor.
    """
    session = models.ForeignKey(CallSession, on_delete=models.CASCADE, related_name="check_item_session")
    choice_element = models.ForeignKey(Choice, on_delete=models.PROTECT, related_name="choice_element",
                                       verbose_name=_('ChoiceElement'))
    has_symptom = models.BooleanField(null=True)

    class Meta:
        verbose_name_plural = _('Self-Reported Items')

    def __str__(self):
        return _('SelfCheckItem: session %s, choice element %s has_symptom %s') \
               % (str(self.session),
                  self.choice_element,
                  self.has_symptom)


def lookup_or_create_self_check_item(self_check_item_id=None, session=None, choice_element=None,
                                     has_symptom=None):
    if self_check_item_id:
        self_check_item = get_object_or_404(SelfCheckItem, pk=self_check_item_id)
    else:
        if session is None:
            raise ValueError('Session ID missing for self-check item')
        if choice_element is None:
            raise ValueError('No choice element associated with the self-check item')
        if has_symptom is None:
            raise ValueError('No answer/option associated to the self-check item')

        self_check_item = SelfCheckItem.objects.create(
            session=session,
            choice_element=choice_element,
            has_symptom=has_symptom
        )
        logger.debug("Saving self-check item - {}".format(self_check_item))
        self_check_item.save()
    return self_check_item
