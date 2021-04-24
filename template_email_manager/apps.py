from django.apps import AppConfig


class TemplateEmailManagerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'template_email_manager'
    from . import __version__ as version_info
    verbose_name = 'Template Email Manager ({})'.format(version_info)

