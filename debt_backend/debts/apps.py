from django.apps import AppConfig


class DebtsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'debts'

    def ready(self):
        from debts import signals  # noqa
