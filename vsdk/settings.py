from os import environ

# Override production variables if DJANGO_DEVELOPMENT env variable is set
if environ.get('HEROKU'):
    from vsdk.settings_prod import *
else:
    from vsdk.settings_dev import *


