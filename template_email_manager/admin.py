from django.contrib import admin

from .models import *

class EmailConfigAdmin(admin.ModelAdmin):

    list_display = ('config_name', 'active', )
    list_editable = ('active', )
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
    list_display = ['id', 'subject', 'template_html', 'status','created_by', 'created_on', 'sent_on', 'send_attempts']
    list_filter = ('status',)
admin.site.register(EmailQueue,EmailQueueAdmin)
class EmailPrototypeAdmin(admin.ModelAdmin):
    filter_horizontal = ('to', 'bcc')
    model = EmailPrototype
    list_display = ['id', 'name', 'subject', 'template_html']
admin.site.register(EmailPrototype,EmailPrototypeAdmin)


