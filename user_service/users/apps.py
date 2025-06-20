from django.apps import AppConfig
from .consul_register import register_to_consul


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'

    def ready(self):
        register_to_consul()
