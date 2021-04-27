
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
    OverrideDefaultAccount=False
    ToAddresses=None
    BccAddresses=None
    MessageCreatedById=None
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
            OverrideDefaultAccount = True
        if SendAccountName and not SendAccountId:
            self.SendAccountName = SendAccountName
            OverrideDefaultAccount = True
        if SendAccountName and SendAccountId:
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
        if MessageCreatedById and not MessageCreatedByName:
            self.MessageCreatedById = MessageCreatedById 
        if MessageCreatedByName and not MessageCreatedById:
            self.MessageCreatedByName = MessageCreatedByName
        if MessageCreatedByName and MessageCreatedById:
            Error = True
            ErrorMessage = 'Unable to set MessageCreatedById or MessageCreatedByName, since both MessageCreatedBy and MessageCreatedByName are specified, please specify only one'
            raise ValueError(
                "Unable to set MessageCreatedBy or MessageCreatedByName, since both MessageCreatedBy and"
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
                raise ValueError("Unable to find Email Prototype"
                                            " with name \"" + str(self.MessagePrototype) + "\", are you sure you added it to the DB?")
            if proto:
                if self.MessageSubject:
                    subject = self.MessageSubject
                else:
                    subject = proto.subject
                    result = re.search(r"\{{ ([A-Za-z0-9_]+)\ }}", subject)
                    if result:
                        try:
                            word = result.group(1)
                            item_value = self.MessageContext[word]
                        except:
                            raise ValueError("Unable to find Context Item with class named \""
                                            + str(word) + "\", are you sure you added it to the DB?")
                        if item_value:
                            subject=subject.replace('{{ ' + word + ' }}', item_value)
                send_user = None
                if self.MessageCreatedById:
                    send_user = User.objects.get(pk=self.MessageCreatedById)
                else:
                    send_user = User.objects.get(pk=1)
                send_account = None
                if self.OverrideDefaultAccount:
                    if self.SendAccountId:
                        send_account = self.SendAccountId
                    else:
                        try:
                            send_account = EmailConfig.objects.get(config_name=self.SendAccountName).id
                        except:
                            raise ValueError("Unable to find Email Configuration"
                                            " with name " + str(self.SendAccountName))
                else:
                    try:
                        send_account = EmailConfig.objects.get(default=True).id
                    except:
                        raise ValueError("No Valid Email Configuration Existing")
                if send_account:
                    self.Message = EmailQueue(subject=subject,
                        sender=proto.sender,
                        html_template=proto.html_template,
                        created_by=send_user,
                        status=EmailQueue.EmailQueueStatus.CREATING,
                        account_id=send_account)
                    self.Message.save()
                    self.Message.to.set(proto.to.all())
                    self.Message.bcc.set(proto.bcc.all())
                    self.Message.save()
                    email_context_items = []
                    for def_cont in proto.html_template.requested_context_classes.all():
                        item_value = None
                        try:
                            item_value = self.MessageContext[def_cont.name]
                            item_name = def_cont.name
                        except:
                            if self.Message:
                                self.Message.delete()
                            raise ValueError("Unable to find Context Item with class named \""
                                            + str(def_cont.name) + "\", are you sure you declared it in the context while calling TemplateEmailMessage class?")
                            pass
                        if item_value != None:
                            ci = ContextItem(context_class=ContextClass.objects.get(pk=def_cont.pk))
                            ci.value = item_value
                            ci.save()
                            self.Message.context_items.add(ci)
                        else:
                            if self.Message:
                                self.Message.delete()
                            raise ValueError("Unable to find Context Item with class named \""
                                            + str(def_cont.name) + "\", are you sure you declared it in the context while calling TemplateEmailMessage class?")
                    
                    self.Message.save()
                print (self.MessageContext)
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
        if self.Message:
            self.Message.status=EmailQueue.EmailQueueStatus.READY
            self.Message.save()
            response = {
                'answer': True,
                'explain': 'Command Executed Successfully',
                'MessageId': self.MessageId
            }
            return response
        else:
            raise ValueError("Unable to send Message, Message undefined")

    def GetMessageStatus(self):

        response = {
            'answer': True,
            'explain': 'Command Executed Successfully',
            'MessageId': self.MessageId,
            'status': 'sent'
        }
        return response

