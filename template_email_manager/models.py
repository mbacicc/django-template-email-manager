from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from django.utils.timezone import now
import django
from django.db.models.signals import post_delete, post_save, pre_save
if django.VERSION < (2, 0):
    from django.utils.encoding import force_text as force_str
    from django.utils.translation import ugettext_lazy as _
else:
    from django.utils.encoding import force_str
    from django.utils.translation import gettext_lazy as _

class EmailConfig(models.Model):
    class EmailConfigBackendChoices(models.TextChoices):
        SMTP = 'SMTP', _('SMTP Backend')
        CONSOLE = 'CONS', _('Console Backend')

    @staticmethod
    def post_save_handler(instance, **kwargs):
        if instance.default:
            EmailConfig.objects.exclude(pk=instance.pk).update(default=False)
        EmailConfig.get_default_config()

    @staticmethod
    def get_default_config():
        objs_manager = EmailConfig.objects
        objs_default_qs = objs_manager.filter(default=True)
        objs_default_ls = list(objs_default_qs)
        objs_default_count = len(objs_default_ls)

        if objs_default_count == 0:
            obj = objs_manager.all().first()
            if obj:
                obj.set_default()
            else:
                obj = objs_manager.create()

        elif objs_default_count == 1:
            obj = objs_default_ls[0]

        elif objs_default_count > 1:
            obj = objs_default_ls[-1]
            obj.set_default()

        return obj

    config_name = models.CharField(
        default='Default',
        max_length=255,
        unique=True,
        verbose_name=_('Config Name'),
        help_text="Configuration Name, must be unique")
    default = models.BooleanField(
        default=True,
        verbose_name=_('default'),
        help_text="If checked this is the default account when new messages have no selected account")
    backend = models.CharField(
        max_length=5,
        choices=EmailConfigBackendChoices.choices,
        default=EmailConfigBackendChoices.SMTP,
        help_text="When SMTP is chosen, all other fields are mandatory, otherwise when Console is chosen, Host, Port, TLS, Username and Password are not needed")
    host = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Only needed when SMTP backend is used, SMTP server host name")
    port = models.IntegerField(
        default=587,
        blank=True,
        null=True,
        help_text="Only needed when SMTP backend is used, SMTP server host port")
    use_tls = models.BooleanField(
        default=True,
        blank=True,
        null=True,
        help_text="Only needed when SMTP backend is used, SMTP server Use TLS. Mutually exclusive with SSL")
    use_ssl = models.BooleanField(
        default=True,
        blank=True,
        null=True,
        help_text="Only needed when SMTP backend is used, SMTP server Use SSL. Mutually exclusive with TLS")
    timeout = models.IntegerField(
        default=30,
        blank=True,
        null=True,
        help_text="Only needed when SMTP backend is used, SMTP server timeout time in seconds")
    username = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Only needed when SMTP backend is used, SMTP server authentication user name")
    password = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Only needed when SMTP backend is used, SMTP server authentication password")
    address = models.EmailField(
        blank=True,
        null=True,
        help_text="Only needed when SMTP backend is used")
    fail_silently = models.BooleanField(default=False)
    max_attempts = models.IntegerField(default=20)
    default_attempts_wait = models.IntegerField(default=60)
    default_attempts_wait_multiplier = models.IntegerField(default=10)
    def set_active(self):
        self.active = True
        self.save()

    class Meta:

        verbose_name = _('Email Config')
        verbose_name_plural = _('Email Configs')

    def __str__(self):
        return str(self.id) + ' - ' + force_str(self.config_name)

post_save.connect(EmailConfig.post_save_handler, sender=EmailConfig)

class ImageAttachment(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='uploads/email-images/')
    def __str__(self):
        return str(self.id) + ' - ' + self.name
    class Meta:
        verbose_name = 'Image Attachment'
        verbose_name_plural = 'Image Attachments'

class ContextClass(models.Model):
    class ContextClassTypeChoices(models.TextChoices):
        INTEGER = 'INT', _('Integer Number')
        FLOAT = 'FLO', _('Float')
        STRING = 'STR', _('String')
        DATE = 'DAT', _('Date')
        TIME = 'TIM', _('Time')
        DATETIME = 'DTI', _('DateTime')

    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Name of the Context Class, must be Unique")
    value_type = models.CharField(
        max_length=5,
        choices=ContextClassTypeChoices.choices,
        default=ContextClassTypeChoices.INTEGER,
        help_text="Used to format the content in a more readable way")
    class Meta:
        verbose_name = 'Context Class'
        verbose_name_plural = 'Context Classes'
    def __str__(self):
        return str(self.id) + ' - ' + self.name


class ContextItem(models.Model):
    context_class = models.ForeignKey(ContextClass,on_delete=models.PROTECT)
    value = models.TextField(default=None, blank=True, null=True)
    def __str__(self):
        return str(self.id) + ' - ' + self.context_class.name
    class Meta:
        verbose_name = 'Context Item'
        verbose_name_plural = 'Context Items'

class HTMLTemplate(models.Model):
    shortname = models.CharField(max_length=45, unique=True, default='new_template')
    fullname = models.CharField(max_length=255,null=True, blank=True)
    html_content = models.TextField(null=True, blank=True)
    images = models.ManyToManyField(ImageAttachment, blank=True)
    text_alternate = models.TextField(null=True, blank=True)
    requested_context_classes = models.ManyToManyField(ContextClass)
    class Meta:
        verbose_name = 'HTML Template'
        verbose_name_plural = 'HTML Templates'
    def __str__(self):
        return str(self.id) + ' - ' + self.shortname

class EmailAddress(models.Model):
    name = models.CharField(max_length=255)
    address = models.EmailField()
    class Meta:
        verbose_name = 'E-mail Address'
        verbose_name_plural = 'E-mail Addresses'
    def __str__(self):
        return str(self.id) + ' - ' + self.address

class EmailQueue(models.Model):
    class EmailQueueStatus(models.TextChoices):
        CREATING = 'CRE', _('Creating')
        READY = 'REA', _('Ready')
        INPROGRESS = 'INP', _('In Progress')
        SENT = 'SEN', _('Sent')
        FAILED = 'FAI', _('Send Failed')
        USERCANCEL = 'USC', _('User Canceled')
        MAXATTEMPTSCANCELED = 'MAC', _('Canceled for Maximum number of sending attempts')

    subject = models.CharField(max_length=255)
    sender = models.ForeignKey(EmailAddress,
        on_delete=models.PROTECT,
        related_name='related_queue_sender')
    account = models.ForeignKey(
        EmailConfig,
        on_delete=models.PROTECT
    )
    to = models.ManyToManyField(EmailAddress,
        related_name='related_queue_to')
    bcc = models.ManyToManyField(EmailAddress,
        related_name='related_queue_bcc',
        blank=True)
    html_template = models.ForeignKey(HTMLTemplate,
        on_delete=models.PROTECT)
    context_items = models.ManyToManyField(
        ContextItem,
        blank=True)
    status = models.CharField(max_length=255,
        choices=EmailQueueStatus.choices,
        default=EmailQueueStatus.CREATING)
    created_by = models.ForeignKey(User,
        on_delete=models.PROTECT,
        blank=True,
        null=True)
    created_on = models.DateTimeField(default=now)
    sent_on = models.DateTimeField(blank=True,
        null=True)
    send_attempts = models.IntegerField(default=0)
    retry_at = models.DateTimeField(default=None,
        blank=True,
        null=True)
    last_operation = models.DateTimeField(default=now)
    class Meta:
        verbose_name = 'E-mail Queue'
        verbose_name_plural = 'E-mail Queues'
    def __str__(self):
        return str(self.id) + ' - ' + self.subject

class EmailPrototype(models.Model):
    name = models.CharField(max_length=255,
        unique=True)
    subject = models.CharField(
        max_length=255)
    sender = models.ForeignKey(
        EmailAddress,
        on_delete=models.PROTECT,
        related_name='related_prototype_sender')
    to = models.ManyToManyField(
        EmailAddress,
        related_name='related_prototype_to')
    bcc = models.ManyToManyField(
        EmailAddress,
        related_name='related_prototype_bcc',
        blank=True)
    html_template = models.ForeignKey(
        HTMLTemplate,
        on_delete=models.PROTECT)
    class Meta:
        verbose_name = 'E-mail Prototype'
        verbose_name_plural = 'E-mail Prototypes'
    def __str__(self):
        return str(self.id) + ' - ' + self.name

class EmailQueueLog(models.Model):
    message = models.ForeignKey(
        EmailQueue,
        on_delete=models.PROTECT)
    status = models.CharField(
        max_length=5,
        choices=EmailQueue.EmailQueueStatus.choices)
    send_attempt = models.IntegerField()
    timestamp = models.DateTimeField(default=now)
    error_code = models.IntegerField(
        blank=True,
        null=True)
    log_info = models.TextField()
    class Meta:
        abstract = True
        ordering = ["-timestamp"]
    class Meta:
        verbose_name = 'E-mail Queue Log'
        verbose_name_plural = 'E-mail Queue Logs'
