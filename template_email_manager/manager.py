
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
# Discard config read from settings, load all the backends and choose the appropriate one depending on the email config
from django.core.mail.backends.smtp import EmailBackend as SMTPEmailBackend
from django.core.mail.backends.console import EmailBackend as ConsoleEmailBackend
from .models import *

import re


class TemplateEmailMessage():
    
    MessageId=None
    MessageSubject=None
    MessagePrototype=None
    MessageContext=None
    SendAccountId=None
    SendAccountName=None
    ToAddresses=None
    BccAddresses=None
    MessageCreatedBy=None
    MessageCreatedByName=None
    Error = False
    ErrorMessage = ''

    Message=None

    def __init__(
        self,
        MessageId=None,             # Optional, If accessing with MessageId, we are trying to retrieve an already created message to follow its status, otherwise we create a new message
        MessageSubject=None,        # If passing MessageSubject, we override the default subject in the Email Prototype
        MessagePrototype=None,      # Name of the Email Prototype as stored in the DB
        MessageContext=None,        # Dict of variable to replace in the HTML and TXT template
        SendAccountId=None,         # If passing SendAccountId, we override the default send account configured in EmailConfig, SendAccountId is the ID of the EmailConfig instance
        SendAccountName=None,       # If passing SendAccountName, we override the default send account configured in EmailConfig, SendAccountName is the config_name field of the EmailConfig instance
        ToAddresses=None,           # list of email addresses as strings, overrides the default Email Prototype list of addresses
        BccAddresses=None,          # list of email addresses as strings, overrides the default Email Prototype list of addresses
        MessageCreatedById=None,    # If passing MessageCreatedById, we override the default user adding the email to the queue (user with ID 1)
        MessageCreatedByName=None,  # If passing MessageCreatedByName, we override the default user adding the email to the queue (user with ID 1)
        ):
        """__init__() functions as the class constructor, retrieves the parameters from the user call
        and configures the TemplateEmailMessage class"""
        if MessageSubject:
            self.MessageSubject = MessageSubject
        if SendAccountId and not SendAccountName:
            self.SendAccountId = SendAccountId
        else:
            Error = True
            ErrorMessage = 'Unable to set SendAccountId, since both SendAccountId and SendAccountName are specified, please specify only one'
            raise ValueError(
                "Unable to set SendAccountId, since both SendAccountId and"
                "SendAccountName are specified, please specify only one.")
        if SendAccountName and not SendAccountId:
            self.SendAccountName = SendAccountName
        else:
            Error = True
            ErrorMessage = 'Unable to set SendAccountId, since both SendAccountId and SendAccountName are specified, please specify only one'
            raise ValueError(
                "Unable to set SendAccountId, since both SendAccountId and"
                "SendAccountName are specified, please specify only one.")
        if ToAddresses:
            self.ToAddresses = ToAddresses
        if BccAddresses:
            self.BccAddresses = BccAddresses
        if MessagePrototype:
            self.MessagePrototype = MessagePrototype
        else:
            raise ValueError(
                "No e-mail prototype specified")
        if MessageContext:
            self.MessageContext = MessageContext
        if MessageCreatedBy and not MessageCreatedByName:
            self.MessageCreatedBy = MessageCreatedBy
        else:
            Error = True
            ErrorMessage = 'Unable to set MessageCreatedBy, since both MessageCreatedBy are MessageCreatedByName are specified, please specify only one'
            raise ValueError(
                "Unable to set MessageCreatedBy, since both MessageCreatedBy and"
                "MessageCreatedByName are specified, please specify only one.")
        if MessageCreatedByName and not MessageCreatedBy:
            self.MessageCreatedByName = MessageCreatedByName
        else:
            Error = True
            ErrorMessage = 'Unable to set MessageCreatedBy, since both MessageCreatedBy and MessageCreatedByName are specified, please specify only one'
            raise ValueError(
                "Unable to set MessageCreatedBy, since both MessageCreatedBy and"
                "MessageCreatedByName are specified, please specify only one.")
            
        if MessageId:
            self.RetrieveMessage(MessageId)
        else:
            self.CreateMessage()

    def CreateMessage(self):
        if not self.Error:
            proto = None
            try:
                proto = EmailPrototype.objects.get(name=self.MessagePrototype)
            except:
                pass
            if proto:
                if self.MessageSubject:
                    subject = self.MessageSubject
                else:
                    subject = proto.subject
                    result = re.search(r"\{{ ([A-Za-z0-9_]+)\ }}", subject)
                    if result:
                        try:
                            word = result.group(1)
                            item_value = context[word]
                        except:
                            pass
                        if item_value:
                            subject=subject.replace('{{ ' + word + ' }}', item_value)
                send_user = None
                if self.MessageCreatedBy:
                    send_user = User.objects.get(pk=self.MessageCreatedBy)
                else:
                    send_user = User.objects.get(pk=1)
                self.Message = EmailQueue(subject=subject,
                    sender=proto.sender,
                    html_template=proto.html_template,
                    created_by=send_user,
                    status=EmailQueue.EmailQueueStatus.CREATING)
                self.Message.save()
                self.Message.to.set(proto.to.all())
                self.Message.bcc.set(proto.bcc.all())
                self.Message.save()
                email_context_items = []
                for def_cont in proto.html_template.requested_context_classes.all():
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
                        self.Message.context_items.add(ci)
                self.Message.status=EmailQueue.EmailQueueStatus.READY
                self.Message.save()
            print (context)
            response = {
                'answer': True,
                'explain': 'Message queued Successfully',
                'MessageId': self.MessageId
            }
            return response
        else:
            response = {
                'answer': False,
                'explain': self.ErrorMessage,
                'MessageId': None
            }
            return response


    
    def RetrieveMessage(self,MessageId):

        response = {
            'answer': True,
            'explain': 'Command Executed Successfully',
            'MessageId': self.MessageId
        }
        return response

    def SendMessage(self):
        
        response = {
            'answer': True,
            'explain': 'Command Executed Successfully',
            'MessageId': self.MessageId
        }
        return response

    def GetMessageStatus(self):

        response = {
            'answer': True,
            'explain': 'Command Executed Successfully',
            'MessageId': self.MessageId,
            'status': 'sent'
        }
        return response

