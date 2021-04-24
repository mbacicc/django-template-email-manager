from .models import *
import re

def add_email_to_queue(prototype, context):
    proto = None
    try:
        proto = EmailPrototype.objects.get(name=prototype)
    except:
        pass
    if proto:
        subject = proto.subject
        result = re.search(r"\<([A-Za-z0-9_]+)\>", subject)
        if result:
            try:
                word = result.group(1)
                item_value = context[word]
            except:
                pass
            if item_value:
                subject=subject.replace('<' + word + '>', item_value)
        eq = EmailQueue(subject=subject,
            sender=proto.sender,
            template_html=proto.template_html,
            created_by=User.objects.get(pk=1),
            status=EmailQueue.EmailQueueStatus.CREATING)
        eq.save()
        eq.to.set(proto.to.all())
        eq.bcc.set(proto.bcc.all())
        eq.save()
        email_context_items = []
        for def_cont in proto.template_html.requested_context_classes.all():
            print (def_cont)
            item_value = None
            try:
                item_value = context[def_cont.name]
                item_name = def_cont.name
            except:
                pass
            if item_value != None:
                ci = ContextItem(context_class=ContextClass.objects.get(pk=def_cont.pk))
                ci.value = item_value
                ci.save()
                eq.context_items.add(ci)
        eq.status=EmailQueue.EmailQueueStatus.READY
        eq.save()
    print (context)