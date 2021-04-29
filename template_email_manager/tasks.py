from background_task import background
from django.contrib.auth.models import User
from .models import *
import logging
from django.db.models import Q
from .manager import *
from django.utils.timezone import now
from datetime import datetime
from django.utils import timezone
from datetime import timedelta

from django.shortcuts import render
from django.template import Template, Context
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from smtplib import SMTPException
from email.mime.image import MIMEImage
import os

logger = logging.getLogger('django.email_manager.background_tasks')

timeout_in_progress_expiration_seconds = 600



@background(schedule=10)
# @background()
def background_process_emails():

    # Attempt Sending newly created emails and failed emails that are not expired
    emails = EmailQueue.objects.filter(Q(status=EmailQueue.EmailQueueStatus.READY) | Q(status=EmailQueue.EmailQueueStatus.FAILED,retry_at__lte=now()))
    for email in emails:
        attempt_send_email(email)

    # Send to failed in progress email that are there for long time
    time_threshold = datetime.now(timezone.utc) - timedelta(seconds=timeout_in_progress_expiration_seconds)
    emails = EmailQueue.objects.filter(status=EmailQueue.EmailQueueStatus.INPROGRESS, last_operation__lte=time_threshold) 
    for email in emails:
        fail_email(email, 'expired, in progress for more than ' + str(timeout_in_progress_expiration_seconds) + ' seconds')

    return True
    



def attempt_send_email(email):

    eql = EmailQueueLog(
        message = email,
        status = EmailQueue.EmailQueueStatus.INPROGRESS,
        send_attempt = 0,
        error_code = 0,
        log_info = 'Starting composing e-mail message'
    )
    eql.save()

    email_config = email.account

    if email_config:
        if email_config.backend == EmailConfig.EmailConfigBackendChoices.SMTP:
            email_backend = SMTPEmailBackend(host=email_config.host, port=email_config.port, username=email_config.username, 
                            password=email_config.password, use_tls=email_config.use_tls, fail_silently=email_config.fail_silently)
        else:
            email_backend = ConsoleEmailBackend(fail_silently=email_config.fail_silently)



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
            emailOfRecipient.append(to_address.name + " <" + to_address.address + ">")
        emailBcc = []
        for bcc_address in email.bcc.all():
            emailBcc.append(bcc_address.name + " <" + bcc_address.address + ">")
        headers={
            "From": email.sender.name + " <" + email.sender.address + ">"
        }
        context = {}

        for item in email.context_items.all():
            cont_item = {
                item.context_class.name : item.value
            }
            context.update(cont_item)

        html_template_string = email.html_template.html_content
        html_template = Template(html_template_string)
        html_content = html_template.render(Context(context))

        txt_template_string = email.html_template.text_alternate
        txt_template = Template(txt_template_string)
        text_content = txt_template.render(Context(context))

        emailMessage = EmailMultiAlternatives(subject=emailSubject, body=text_content, from_email=emailOfSender,\
            to=emailOfRecipient, bcc=emailBcc, reply_to=[emailOfSender,], headers=headers, connection=email_backend)

        emailMessage.attach_alternative(html_content, "text/html")
        
        success = True
        try:
            for image in email.html_template.images.all():
                fp = open(os.path.join(settings.MEDIA_ROOT, image.image.name), 'rb')
                msg_img = MIMEImage(fp.read())
                fp.close()
                msg_img.add_header('Content-ID', '<{}>'.format(image.name))
                emailMessage.attach(msg_img)
        except:
            pass
        try:
            eql = EmailQueueLog(
                message = email,
                status = EmailQueue.EmailQueueStatus.INPROGRESS,
                send_attempt = 0,
                error_code = 0,
                log_info = 'Attempting e-mail send'
            )
            eql.save()
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
                    email.save()
                    eql = EmailQueueLog(
                        message = email,
                        status = EmailQueue.EmailQueueStatus.FAILED,
                        send_attempt = 0,
                        error_code = int(e.args),
                        log_info = 'SMTP Error SMTPException ' + str(e.args)
                    )
                    eql.save()
                else :
                    email.status = EmailQueue.EmailQueueStatus.MAXATTEMPTSCANCELED
                    email.send_attempts += 1
                    email.save()
                    eql = EmailQueueLog(
                        message = email,
                        status = EmailQueue.EmailQueueStatus.MAXATTEMPTSCANCELED,
                        send_attempt = 0,
                        error_code = int(e.args),
                        log_info = 'SMTP Error SMTPException ' + str(e.args) + ' - canceling email send for max number of attempts'
                    )
                    eql.save()
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
                    email.save()
                    eql = EmailQueueLog(
                        message = email,
                        status = EmailQueue.EmailQueueStatus.FAILED,
                        send_attempt = 0,
                        error_code = int(e.args),
                        log_info = 'SMTP Error SMTPDataError ' + str(e.args)
                    )
                    eql.save()
                else :
                    email.status = EmailQueue.EmailQueueStatus.MAXATTEMPTSCANCELED
                    email.send_attempts += 1
                    email.save()
                    eql = EmailQueueLog(
                        message = email,
                        status = EmailQueue.EmailQueueStatus.MAXATTEMPTSCANCELED,
                        send_attempt = 0,
                        error_code = int(e.args),
                        log_info = 'SMTP Error SMTPDataError ' + str(e.args) + ' - canceling email send for max number of attempts'
                    )
                    eql.save()
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
                    email.last_operation = datetime.now(timezone.utc)
                    email.save()
                    eql = EmailQueueLog(
                        message = email,
                        status = EmailQueue.EmailQueueStatus.FAILED,
                        send_attempt = 0,
                        error_code = int(e.args),
                        log_info = 'Error ' + str(e.args)
                    )
                    eql.save()
                else :
                    email.status = EmailQueue.EmailQueueStatus.MAXATTEMPTSCANCELED
                    email.send_attempts += 1
                    email.last_operation = datetime.now(timezone.utc)
                    email.save()
                    eql = EmailQueueLog(
                        message = email,
                        status = EmailQueue.EmailQueueStatus.MAXATTEMPTSCANCELED,
                        send_attempt = 0,
                        error_code = int(e.args),
                        log_info = 'Error ' + str(e.args) + ' - canceling email send for max number of attempts'
                    )
                    eql.save()
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
                eql = EmailQueueLog(
                    message = email,
                    status = EmailQueue.EmailQueueStatus.SENT,
                    send_attempt = 0,
                    error_code = 0,
                    log_info = 'Message sent'
                )
                eql.save()
            except:
                pass
    return True
    

def fail_email(email, reason):
    email.status = EmailQueue.EmailQueueStatus.FAILED
    email.last_operation = datetime.now(timezone.utc)
    email.save()
    eql = EmailQueueLog(
        message = email,
        status = EmailQueue.EmailQueueStatus.FAILED,
        send_attempt = 0,
        error_code = 0,
        log_info = 'Failed: ' + reason
    )
    eql.save()