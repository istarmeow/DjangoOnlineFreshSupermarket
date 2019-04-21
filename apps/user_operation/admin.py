from django.contrib import admin
from django.apps import apps

all_models = apps.get_app_config('user_operation').get_models()
for model in all_models:
    try:
        admin.site.register(model)
    except:
        pass
