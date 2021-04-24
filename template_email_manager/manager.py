
from datetime import datetime
from django.utils import timezone
from django.shortcuts import render
from django.template import Template, Context
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from smtplib import SMTPException
from email.mime.image import MIMEImage
import os
from django.utils.timezone import now
from django.utils import timezone
from datetime import timedelta

from django.core.mail import EmailMessage
from django.core.mail.backends.smtp import EmailBackend
from .models import *


def attempt_send_email(email):

    try:
        email_config = EmailConfig.objects.get(active=True)
    except:
        return None
    if email_config:
        backend = EmailBackend(host=email_config.host, port=email_config.port, username=email_config.username, 
                        password=email_config.password, use_tls=email_config.use_tls, fail_silently=email_config.fail_silently)

        try:
            email.status = EmailQueue.EmailQueueStatus.INPROGRESS
            email.last_operation = datetime.now(timezone.utc)
            email.save()
        except:
            pass

        emailSubject = email.subject
        emailOfSender = email.sender.address
        emailOfRecipient = []
        for to_address in email.to.all():
            emailOfRecipient.append(to_address.address)
        emailBcc = []
        for bcc_address in email.bcc.all():
            emailBcc.append(bcc_address.address)
        headers={
            "From": email.sender.name + " <" + email.sender.address + ">"
        }
        context = {}

        for item in email.context_items.all():
            cont_item = {
                item.context_class.name : item.value
            }
            context.update(cont_item)

        html_template_string = email.template_html.html_content
        html_template = Template(html_template_string)
        html_content = html_template.render(Context(context))

        txt_template_string = email.template_html.text_alternate
        txt_template = Template(txt_template_string)
        text_content = txt_template.render(Context(context))

        emailMessage = EmailMultiAlternatives(subject=emailSubject, body=text_content, from_email=emailOfSender,\
            to=emailOfRecipient, bcc=emailBcc, reply_to=[emailOfSender,], headers=headers, connection=backend)

        emailMessage.attach_alternative(html_content, "text/html")
        
        success = True
        try:
            for image in email.template_html.images.all():
                fp = open(os.path.join(settings.MEDIA_ROOT, image.image.name), 'rb')
                msg_img = MIMEImage(fp.read())
                fp.close()
                msg_img.add_header('Content-ID', '<{}>'.format(image.name))
                emailMessage.attach(msg_img)
        except:
            pass
        try:
            emailMessage.send(fail_silently=False)
            pass

        except SMTPException as e:
            # print('There was an error sending an email: ', e) 
            # error = {'message': ",".join(e.args) if len(e.args) > 0 else 'Unknown Error'}
            
            success = False
            try:
                if email.send_attempts < email_config.max_attempts : 
                    email.status = EmailQueue.EmailQueueStatus.FAILED
                    email.send_attempts += 1
                    email.retry_at = datetime.now(timezone.utc) + timedelta(seconds=email_config.default_attempts_wait + (email_config.default_attempts_wait_multiplier * email.send_attempts))
                    email.error_log += ';' + datetime.now().strftime("%d/%m/%Y %H:%M:%S")  + ', SMTP Error SMTPException ' + str(e.args)
                    email.save()
                else :
                    email.status = EmailQueue.EmailQueueStatus.MAXATTEMPTSCANCELED
                    email.send_attempts += 1
                    email.error_log += ';' + datetime.now().strftime("%d/%m/%Y %H:%M:%S") + ', SMTP Error SMTPException ' + str(e.args) + ' - canceling email send for max number of attempts'
                    email.save()
            except:
                pass
            return False
        except SMTPDataError as e:
            success = False
            try:
                if email.send_attempts < email_config.max_attempts : 
                    email.status = EmailQueue.EmailQueueStatus.FAILED
                    email.send_attempts += 1
                    email.retry_at = datetime.now(timezone.utc) + timedelta(seconds=email_config.default_attempts_wait + (email_config.default_attempts_wait_multiplier * email.send_attempts))
                    email.error_log += ';' + datetime.now().strftime("%d/%m/%Y %H:%M:%S")  + ', SMTP Error SMTPDataError ' + str(e.args)
                    email.save()
                else :
                    email.status = EmailQueue.EmailQueueStatus.MAXATTEMPTSCANCELED
                    email.send_attempts += 1
                    email.error_log += ';' + datetime.now().strftime("%d/%m/%Y %H:%M:%S") + ', SMTP Error SMTPDataError ' + str(e.args) + ' - canceling email send for max number of attempts'
                    email.save()
            except:
                pass
            return False
        except Exception as e:
            print('There was an error sending an email: ', e) 
            try:
                if email.send_attempts < email_config.max_attempts : 
                    email.status = EmailQueue.EmailQueueStatus.FAILED
                    email.send_attempts += 1
                    email.retry_at = datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M:%S")  + timedelta(seconds=email_config.default_attempts_wait + (email_config.default_attempts_wait_multiplier * email.send_attempts))
                    email.error_log += ';' + datetime.now() + ', Error ' + str(e.args)
                    email.last_operation = datetime.now(timezone.utc)
                    email.save()
                else :
                    email.status = EmailQueue.EmailQueueStatus.MAXATTEMPTSCANCELED
                    email.send_attempts += 1
                    email.error_log += ';' + datetime.now().strftime("%d/%m/%Y %H:%M:%S")  + ', SMTP Error ' + str(e.args) + ' - canceling email send for max number of attempts'
                    email.last_operation = datetime.now(timezone.utc)
                    email.save()
            except:
                pass
            success = False
            return False
        if success:
            try:
                email.status = EmailQueue.EmailQueueStatus.SENT
                email.send_attempts += 1
                email.sent_on = datetime.now(timezone.utc)
                email.last_operation = datetime.now(timezone.utc)
                email.save()
            except:
                pass
    return True
    

def fail_email(email, reason):
    email.status = EmailQueue.EmailQueueStatus.FAILED
    email.error_log += ';' + datetime.now().strftime("%d/%m/%Y %H:%M:%S")  + ', Failed: ' + reason
    email.last_operation = datetime.now(timezone.utc)
    email.save()