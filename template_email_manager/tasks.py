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

logger = logging.getLogger('django.email_manager.background_tasks')

timeout_in_progress_expiration_seconds = 600

from .commands import *

@background(schedule=60)
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

    return 1
