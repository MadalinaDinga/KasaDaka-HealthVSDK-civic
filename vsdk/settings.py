from os import environ

# Override production variables if DJANGO_DEVELOPMENT env variable is set
if environ.get('HEROKU'):
    from vsdk.settings_prod import *
else:
    from vsdk.settings_dev import *


ADMIN_REORDER = (
    # Keep original label and models
    'sites',

    # Rename app
    {'app': 'auth',
     'label': 'CIVIC AUTHENTICATION AND AUTHORIZATION',
     'models': (
         {'model': 'auth.User', 'label': 'CIVIC Users'},
         {'model': 'auth.Group', 'label': 'Manage Desktops'},
         {'model': 'service_development.KasaDakaUser', 'label': 'Voice Service Users'},
         {'model': 'service_development.CallSession', 'label': 'Call Sessions'},
     )},

    {'app': 'service_development',
     'label': 'Voice Service Configuration',
     'models': (
         'service_development.VoiceService',
         'service_development.MessagePresentation',
         'service_development.Choice',
         # 'service_development.SpokenUserInput',
         # 'service_development.UserInputCategory',
         # 'service_development.SpokenUserInput',
     )},

    {'app': 'service_development',
     'label': 'Language Configuration',
     'models': (
         {'model': 'service_development.Language', 'label': 'Languages'},
         {'model': 'service_development.VoiceLabel', 'label': 'Voice Labels'},
     )},

    {'app': 'service_development',
     'label': 'Medical Configuration',
     'models': (
         'service_development.Symptom',
         'service_development.Risk',
         'service_development.ResultConfig',
     )},

    {'app': 'service_development',
     'label': 'Self-Reported Items',
     'models': (
         {'model': 'service_development.SelfCheckItem', 'label': 'User-Reported Items'},
         {'model': 'service_development.ResultItem', 'label': 'Diagnostic Results'},
     )},
)