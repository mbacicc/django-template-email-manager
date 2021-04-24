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

    @staticmethod
    def post_save_handler(instance, **kwargs):
        if instance.active:
            EmailConfig.objects.exclude(pk=instance.pk).update(active=False)
        EmailConfig.get_active_theme()

    @staticmethod
    def get_active_theme():
        objs_manager = EmailConfig.objects
        objs_active_qs = objs_manager.filter(active=True)
        objs_active_ls = list(objs_active_qs)
        objs_active_count = len(objs_active_ls)

        if objs_active_count == 0:
            obj = objs_manager.all().first()
            if obj:
                obj.set_active()
            else:
                obj = objs_manager.create()

        elif objs_active_count == 1:
            obj = objs_active_ls[0]

        elif objs_active_count > 1:
            obj = objs_active_ls[-1]
            obj.set_active()

        return obj

    config_name = models.CharField(
        default='Default',
        max_length=255,
        unique=True,
        verbose_name=_('Config Name'))
    active = models.BooleanField(
        default=True,
        verbose_name=_('active'))
    host = models.CharField(max_length=255)
    port = models.IntegerField(default=587)
    use_tls = models.BooleanField(default=True)
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
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
    name = models.CharField(max_length=100)
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
    images = models.ManyToManyField(ImageAttachment)
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
    to = models.ManyToManyField(EmailAddress,
        related_name='related_queue_to')
    bcc = models.ManyToManyField(EmailAddress,
        related_name='related_queue_bcc',
        blank=True)
    template_html = models.ForeignKey(HTMLTemplate,
        on_delete=models.PROTECT)
    context_items = models.ManyToManyField(ContextItem)
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
    error_log = models.TextField(
        blank=True)
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
    subject = models.CharField(max_length=255)
    sender = models.ForeignKey(EmailAddress,
        on_delete=models.PROTECT,
        related_name='related_prototype_sender')
    to = models.ManyToManyField(EmailAddress,
        related_name='related_prototype_to')
    bcc = models.ManyToManyField(EmailAddress,
        related_name='related_prototype_bcc',
        blank=True)
    template_html = models.ForeignKey(HTMLTemplate,
        on_delete=models.PROTECT)
    class Meta:
        verbose_name = 'E-mail Prototype'
        verbose_name_plural = 'E-mail Prototypes'
    def __str__(self):
        return str(self.id) + ' - ' + self.name