from django.apps import AppConfig


class MemberConfig(AppConfig):
    name = 'member'

    def ready(self):
        # import signal handlers
        # (every models imported inside handlers will be instantiated as
        # soon as the registry is fully populated.)
        import member.signals.handlers  # noqa
