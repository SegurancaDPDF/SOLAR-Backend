from django.apps import AppConfig

# registra o aplicativo e suas configurações no projeto Django


class ApiV2Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api.api_v2'
