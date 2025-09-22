from django.apps import AppConfig


class DbAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'db_app'
    verbose_name = 'База данных прайсов'