from django.contrib import admin
from django import forms
from .models import *

class EmailConfigAdmin(admin.ModelAdmin):

    list_display = ('config_name', 'default', 'backend' )
    list_editable = ('default', )
    list_per_page = 10
    show_full_result_count = False


admin.site.register(EmailConfig,EmailConfigAdmin)
admin.site.register(ImageAttachment)
admin.site.register(ContextClass)
admin.site.register(ContextItem)
class HTMLTemplateAdmin(admin.ModelAdmin):
    filter_horizontal = ('images','requested_context_classes',)
admin.site.register(HTMLTemplate,HTMLTemplateAdmin)
class EmailAddressAdmin(admin.ModelAdmin):
    model = EmailAddress
    list_display = ['id', 'name', 'address']
admin.site.register(EmailAddress,EmailAddressAdmin)
class EmailQueueAdmin(admin.ModelAdmin):
    filter_horizontal = ('context_items', 'to', 'bcc')
    model = EmailQueue
    list_display = ['id', 'subject', 'html_template', 'status','created_by', 'created_on', 'sent_on', 'send_attempts']
    list_filter = ('status',)
admin.site.register(EmailQueue,EmailQueueAdmin)
class EmailPrototypeAdmin(admin.ModelAdmin):
    filter_horizontal = ('to', 'bcc')
    model = EmailPrototype
    list_display = ['id', 'name', 'subject', 'html_template']
admin.site.register(EmailPrototype,EmailPrototypeAdmin)


class EmailQueueLogAdmin(admin.ModelAdmin):
    model = EmailQueueLog
    list_display = ['id', 'timestamp', 'message', 'status', 'error_code', 'send_attempt', 'log_info']
    date_hierarchy = "timestamp"
    search_fields = ["message", "status", "error_code", "log_info"]
    list_filter = ["status", "error_code", "send_attempt"]

    readonly_fields = [
        "timestamp",
        "message",
        "status",
        "error_code",
        "send_attempt",
        "log_info",
    ]

    def has_add_permission(self, request):
        return False

admin.site.register(EmailQueueLog,EmailQueueLogAdmin)
