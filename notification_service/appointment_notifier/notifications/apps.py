from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'appointment_notifier.notifications'

    def ready(self):
        # Import và register Consul khi app ready
        try:
            from consul_register import register_to_consul
            register_to_consul()
        except Exception as e:
            print(f"Failed to register to Consul: {e}")