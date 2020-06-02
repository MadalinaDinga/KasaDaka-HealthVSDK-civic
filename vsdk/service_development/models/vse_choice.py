from django.db import models
from django.utils.translation import ugettext
from django.utils.translation import ugettext_lazy as _

from .risks import Risk
from .symptoms import Symptom
from .vs_element import VoiceServiceElement, VoiceServiceSubElement


class Choice(VoiceServiceElement):
    _urls_name = 'service-development:choice'
    skip_reading_choice_options = models.BooleanField(default=False,
                                                      verbose_name=_('Skip Mentioning Choice Options'),
                                                      help_text=_(
                                                          'Whether the choice options should be mentioned to the user for the choice element'))
    is_persistent_choice = models.BooleanField(default=False,
                                               verbose_name=_('Save Choice Option'),
                                               help_text=_(
                                                   'Whether the chosen option should be saved in the database'))
    symptom = models.ForeignKey(Symptom, on_delete=models.PROTECT, related_name="symptom",
                                verbose_name=_('Associated symptom'), null=True, blank=True,
                                help_text=_('Select the corresponding symptom, if this choice element represents one'))
    risk = models.ForeignKey(Risk, on_delete=models.PROTECT, related_name="risk",
                             verbose_name=_('Associated risk'), null=True, blank=True,
                             help_text=_('Select the corresponding risk, if this choice element represents one'))

    class Meta:
        verbose_name = _('Choice Element')

    def __str__(self):
        return self.name

    def is_valid(self):
        return len(self.validator()) == 0

    is_valid.boolean = True
    is_valid.short_description = _('Is valid')

    def validator(self):
        errors = []
        errors.extend(super(Choice, self).validator())
        choice_options = self.choice_options.all()
        for choice_option in choice_options:
            errors.extend(choice_option.validator())

        # deduplicate errors
        errors = list(set(errors))
        return errors


class ChoiceOption(VoiceServiceSubElement):
    parent = models.ForeignKey(
        Choice,
        on_delete=models.CASCADE,
        related_name='choice_options')
    _redirect = models.ForeignKey(
        VoiceServiceElement,
        on_delete=models.SET_NULL,
        verbose_name=_('Redirect element'),
        help_text=_("The element to redirect to when this choice is made by the user."),
        related_name='%(app_label)s_%(class)s_redirect_related',
        blank=True,
        null=True)

    class Meta:
        verbose_name = _('Voice Service')

    @property
    def redirect(self):
        """
        Returns the actual subclassed object that is redirected to,
        instead of the VoiceServiceElement superclass object (which does
        not have specific fields and methods).
        """
        return VoiceServiceSubElement.objects.get_subclass(id=self._redirect.id)

    def __str__(self):
        return "(%s): %s" % (self.parent.name, self.name)

    def is_valid(self):
        return len(self.validator()) == 0

    is_valid.boolean = True
    is_valid.short_description = _('Is valid')

    def validator(self):
        errors = []
        errors.extend(super(ChoiceOption, self).validator())
        # check if redirect is present
        if not self._redirect:
            errors.append(ugettext('No redirect in choice option: "%s"') % str(self))
        else:
            if self.service.id != self.parent.service.id:
                errors.append(ugettext(
                    'Choice option "%(name_of_element)s" not in correct (same) Voice Service as Choice element! ("%(name_service_of_element)s", should be "%(name_service_of_parent_of_element)s")') % {
                                  'name_of_element': str(self), 'name_service_of_element': str(self.service),
                                  'name_service_of_parent_of_element': str(self.parent.service)})
            if self.redirect.service.id != self.parent.service.id:
                errors.append(ugettext(
                    'Redirect element of choice option "%(name_of_element)s" not in correct (same) Voice Service! ("%(name_service_of_element)s", should be "%(name_service_of_parent_of_element)s")') % {
                                  'name_of_element': str(self), 'name_service_of_element': str(self.redirect.service),
                                  'name_service_of_parent_of_element': str(self.service)})

        return errors
