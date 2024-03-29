from django.contrib import messages
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from vsdk import settings
from .models import *

admin.site.site_header = "CIVIC Medical Desktop"
admin.site.site_title = "CIVIC Medical Desktop"
admin.site.index_title = "Welcome to CIVIC"


def format_validation_result(obj):
    """
        Creates a HTML list from all errors found in validation
        """
    return '<br/>'.join(obj.validator())


class VoiceServiceAdmin(admin.ModelAdmin):
    fieldsets = [(_('General'), {
        'fields': ['name', 'description', 'vxml_url', 'active', 'is_valid', 'validation_details',
                   'supported_languages']}),
                 (_('Registration process'),
                  {'fields': ['registration', 'is_pass_based_auth', 'registration_language']}),
                 (_('Call flow'), {'fields': ['_start_element']})]
    list_display = ('name', 'active')
    readonly_fields = ('vxml_url', 'is_valid', 'validation_details')

    def save_model(self, request, obj, form, change):
        if obj.active and 'active' in form.changed_data and settings.KASADAKA:
            # set all other voice services to inactive
            other_vs = VoiceService.objects.exclude(pk=obj.id)
            for vs in other_vs:
                vs.active = False
                vs.save()
            # change asterisk config here
            from pathlib import Path
            my_file = Path(settings.ASTERISK_EXTENSIONS_FILE)
            if my_file.is_file():
                extensions = ''
                with open(settings.ASTERISK_EXTENSIONS_FILE) as infile:
                    import re
                    extensions = infile.read()
                    regex = r"(Vxml\()(.+)(\?callerid\=\$\{CALLERID\(num\)\}\))"
                    subst = "\\1" + settings.VXML_HOST_ADDRESS + str(obj.get_vxml_url()) + "\\3"
                    extensions = re.sub(regex, subst, extensions, 0)
                with open(settings.ASTERISK_EXTENSIONS_FILE, 'w') as outfile:
                    outfile.write(extensions)
                # Reload asterisk
                import subprocess
                subprocess.getoutput("sudo /etc/init.d/asterisk reload")
                messages.add_message(request, messages.WARNING, _(
                    'Voice service activated. Other voice services have been deactivated, the Asterisk configuration has been changed to point to this service, and this new configuration has been loaded.'))
            else:
                messages.add_message(request, messages.ERROR, _(
                    'Voice service activated. Other voice services have been deactivated. THE ASTERISK CONFIGURATION COULD NOT BE FOUND!'))
        super(VoiceServiceAdmin, self).save_model(request, obj, form, change)

    def get_readonly_fields(self, request, obj=None):
        """
        Only allow activation of voice service if it is valid
        """
        if obj is not None:
            if not obj.is_valid():
                return self.readonly_fields + ('active',)
        return self.readonly_fields

    def validation_details(self, obj=None):
        return mark_safe(format_validation_result(obj))

    validation_details.short_description = _('Validation errors')


class VoiceServiceElementAdmin(admin.ModelAdmin):
    fieldsets = [
        (_('General'), {'fields': ['name', 'description', 'service', 'is_valid', 'validation_details', 'voice_label']})]
    list_filter = ['service']
    list_display = ('name', 'service', 'is_valid')
    readonly_fields = ('is_valid', 'validation_details')

    def validation_details(self, obj=None):
        return mark_safe(format_validation_result(obj))

    validation_details.short_description = _('Validation errors')


class ChoiceOptionsInline(admin.TabularInline):
    model = ChoiceOption
    insert_after = 'skip_reading_choice_options'
    extra = 2
    fk_name = 'parent'
    view_on_site = False
    verbose_name = _('Possible choice')
    verbose_name_plural = _('Possible choices')


class ChoiceAdmin(VoiceServiceElementAdmin):
    fieldsets = VoiceServiceElementAdmin.fieldsets + [
        (_('Configure Choice Element'),
         {'fields': ['skip_reading_choice_options', 'is_persistent_choice', 'symptom', 'risk']})]

    inlines = [ChoiceOptionsInline]

    change_form_template = 'admin/custom/change_form.html'

    class Media:
        css = {
            'all': (
                'css/admin.css',
            )
        }


class VoiceLabelInline(admin.TabularInline):
    model = VoiceFragment
    extra = 2
    fk_name = 'parent'
    fieldsets = [(_('General'), {'fields': ['language', 'is_valid', 'audio', 'audio_file_player']})]
    readonly_fields = ('audio_file_player', 'is_valid')


class VoiceLabelByVoiceServicesFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _('Voice Service')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'voice-service'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        voice_services = VoiceService.objects.all()
        result = []
        for service in voice_services:
            result.append((service.id, service.name))
        return result

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        return VoiceLabel.objects.filter(voiceservicesubelement__service__id=self.value()).distinct()


class VoiceLabelAdmin(admin.ModelAdmin):
    list_display = ['name']
    list_filter = [VoiceLabelByVoiceServicesFilter]
    inlines = [VoiceLabelInline]

    def save_model(self, request, obj, form, change):
        if not settings.KASADAKA:
            messages.add_message(request, messages.WARNING, _(
                'Automatic .wav file conversion only works when running on real KasaDaka system. MANUALLY ensure your files are in the correct format! Wave (.wav) : Sample rate 8KHz, 16 bit, mono, Codec: PCM 16 LE (s16l)'))
        super(VoiceLabelAdmin, self).save_model(request, obj, form, change)


class CallSessionInline(admin.TabularInline):
    model = CallSessionStep
    extra = 0
    fk_name = 'session'
    can_delete = False
    fieldsets = [(_('General'), {'fields': ['visited_element', 'time', 'description']})]
    readonly_fields = ('time', 'session', 'visited_element', 'description')
    max_num = 0


class CallSessionAdmin(admin.ModelAdmin):
    list_display = ('start', 'user', 'service', 'caller_id', 'language')
    list_filter = ('service', 'user', 'caller_id')
    fieldsets = [(_('General'), {'fields': ['service', 'user', 'caller_id', 'start', 'end', 'language']})]
    readonly_fields = ('service', 'user', 'caller_id', 'start', 'end', 'language')
    inlines = [CallSessionInline]
    can_delete = True

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return True

    # def get_actions(self, request):
    #    actions = super(CallSessionAdmin, self).get_actions(request)
    #    if 'delete_selected' in actions:
    #        del actions['delete_selected']
    #    return actions


class MessagePresentationAdmin(VoiceServiceElementAdmin):
    fieldsets = VoiceServiceElementAdmin.fieldsets + [
        (_('Message Presentation'), {'fields': ['_redirect', 'redirects_to_result', 'final_element']})]


class KasaDakaUserAdmin(admin.ModelAdmin):
    list_filter = ['service', 'language', 'caller_id']
    list_display = ('__str__', 'caller_id', 'service', 'language')


class SpokenUserInputAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'category', 'description', 'audio_file_player')
    list_filter = ('category',)
    fieldsets = [(_('General'), {'fields': ['audio', 'audio_file_player', 'session', 'category', 'description']})]
    readonly_fields = ('audio', 'session', 'category', 'audio_file_player')
    can_delete = True

    def has_add_permission(self, request):
        return False


class SelfCheckItemAdmin(admin.ModelAdmin):
    list_display = ('get_user', 'get_session_start_date', 'get_self_check_item_name', 'get_answer')
    readonly_fields = ('session', 'get_self_check_item_name', 'has_symptom', 'choice_element')
    list_filter = ['session__user', 'session__start', 'choice_element__symptom', 'choice_element__risk']
    can_delete = False

    def has_add_permission(self, request):
        return False

    def get_user(self, obj):
        if obj.session.user:
            return "%s" % (str(obj.session.user))
        else:
            return "%s" % (str(obj.session.caller_id))

    get_user.short_description = 'User'
    get_user.admin_order_field = 'session'

    def get_session_start_date(self, obj):
        return obj.session.formatted_time

    get_session_start_date.short_description = 'Date'
    get_session_start_date.admin_order_field = 'session'

    def get_self_check_item_name(self, obj):
        if obj.choice_element.symptom:
            return obj.choice_element.symptom
        if obj.choice_element.risk:
            return obj.choice_element.risk

    get_self_check_item_name.short_description = 'Name'  # Rename column head
    get_self_check_item_name.admin_order_field = 'choice_element'  # Allows column order sorting

    def get_answer(self, obj):
        return obj.has_symptom

    get_answer.short_description = 'Reported'
    get_answer.boolean = True


class ResultItemAdmin(admin.ModelAdmin):
    list_display = (
        'get_user', 'get_session_start_date', 'get_is_infected_prediction', 'get_testing_confirmation', 'get_infected_probability', 'get_testing_recommended',
        'is_exposed', 'get_symptom_no', 'get_risk_no')
    readonly_fields = (
        'session', 'is_exposed', 'symptom_no', 'risk_no', 'infected_probability', 'is_infected_prediction',
        'testing_recommended')
    can_delete = False

    def has_add_permission(self, request):
        return False

    def get_user(self, obj):
        if obj.session.user:
            return "%s" % (str(obj.session.user))
        else:
            return "%s" % (str(obj.session.caller_id))
    get_user.short_description = 'User'
    get_user.admin_order_field = 'session'

    def get_session_start_date(self, obj):
        return obj.session.formatted_time
    get_session_start_date.short_description = 'Date'
    get_session_start_date.admin_order_field = 'session'

    def get_testing_confirmation(self, obj):
        return obj.testing_confirmation
    get_testing_confirmation.short_description = mark_safe('Diagnostic <br/> Confirmation')
    get_testing_confirmation.admin_order_field = 'testing_confirmation'
    get_testing_confirmation.boolean = True

    def get_testing_recommended(self, obj):
        return obj.testing_recommended
    get_testing_recommended.short_description = mark_safe('Testing <br/> Recommended')
    get_testing_recommended.admin_order_field = 'testing_recommended'
    get_testing_recommended.boolean = True

    def get_is_infected_prediction(self, obj):
        if obj.is_infected_prediction:
            return "Positive"
        else:
            return "Negative"
        #return obj.is_infected_prediction
    get_is_infected_prediction.short_description = mark_safe('Predicted <br/> diagnostic')
    get_is_infected_prediction.admin_order_field = 'is_infected_prediction'
    # get_is_infected_prediction.boolean = True

    def get_infected_probability(self, obj):
        if obj.infected_probability:
            return str(round(obj.infected_probability, 2))
    get_infected_probability.short_description = mark_safe('Infection estimated <br/> probability')
    get_infected_probability.admin_order_field = 'infected_probability'

    def get_symptom_no(self, obj):
        return obj.symptom_no
    get_symptom_no.short_description = mark_safe('Number of reported <br/> symptoms')
    get_symptom_no.admin_order_field = 'symptom_no'

    def get_risk_no(self, obj):
        return obj.risk_no
    get_risk_no.short_description = mark_safe('Number of reported <br/> risk factors')
    get_risk_no.admin_order_field = 'risk_no'


class ResultConfigAdmin(admin.ModelAdmin):
    list_display = ('infected_probability_benchmark', 'symptom_no_benchmark')
    can_delete = False

    def has_add_permission(self, request):
        return False


# Register your models here

admin.site.register(VoiceService, VoiceServiceAdmin)
admin.site.register(MessagePresentation, MessagePresentationAdmin)
admin.site.register(Choice, ChoiceAdmin)
admin.site.register(CallSession, CallSessionAdmin)
admin.site.register(KasaDakaUser, KasaDakaUserAdmin)
admin.site.register(Language)
admin.site.register(VoiceLabel, VoiceLabelAdmin)
admin.site.register(SpokenUserInput, SpokenUserInputAdmin)
admin.site.register(UserInputCategory)
admin.site.register(Record)
admin.site.register(Symptom)
admin.site.register(Risk)
admin.site.register(SelfCheckItem, SelfCheckItemAdmin)
admin.site.register(ResultItem, ResultItemAdmin)
admin.site.register(ResultConfig, ResultConfigAdmin)
