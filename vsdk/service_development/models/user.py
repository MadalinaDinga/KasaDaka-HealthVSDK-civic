from django.core.validators import MinLengthValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.hashers import make_password, check_password

from . import Language
from . import VoiceService


class KasaDakaUser(models.Model):
    """
    User that belongs to a Voice Service on this system
    """
    caller_id = models.CharField(_('Phone number'), max_length=100, unique=True)
    first_name = models.CharField(_('First name'), max_length=100, blank=True)
    last_name = models.CharField(_('Last name'), max_length=100, blank=True)
    creation_date = models.DateTimeField(_('Date created'), auto_now_add=True)
    modification_date = models.DateTimeField(_('Date last modified'), auto_now=True)
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True)
    service = models.ForeignKey(VoiceService, on_delete=models.CASCADE)
    username = models.CharField(_('Username'), max_length=100, blank=True, null=True)
    _password = models.CharField(_('Password'), max_length=100, blank=True, null=True, validators=[MinLengthValidator(6)])

    class Meta:
        verbose_name = _('KasaDaka User')

    def set_password(self, password):
        # Store hashed password
        self._password = make_password(password=password)

    def is_valid_credentials(self, username, password, service):
        """
        If user credentials (username and password) for current voice_service are valid, return true.
        If user credentials are not valid, return false.
        """
        is_pass_correct = check_password(password, self._password)
        print(f"{username}/{self.username}, {service}/{self.service}, {is_pass_correct}, {password}/{make_password(password)}/{self._password}")
        return username == self.username and password == self._password and service == self.service

    def __str__(self):
        if not (self.first_name or self.last_name):
            return "%s" % self.caller_id
        else:
            return "%s %s (%s)" % (self.first_name, self.last_name, self.caller_id)


def lookup_kasadaka_user_by_caller_id(caller_id, service):
    """
    If user with caller_id for current voice_service exists, returns User object.
    If user does not exist or caller_id is None, returns None.
    """
    if caller_id:
        try:
            return KasaDakaUser.objects.get(caller_id=caller_id,
                                            service=service)
        except KasaDakaUser.DoesNotExist:
            return None
    return None


def lookup_kasadaka_user_by_username(username, service):
    """
    If user with username for current voice_service exists, returns User object.
    If user does not exist or username is None, returns None.
    """
    if username:
        try:
            return KasaDakaUser.objects.get(username=username,
                                            service=service)
        except KasaDakaUser.DoesNotExist:
            return None
    return None
