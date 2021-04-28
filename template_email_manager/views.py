from django.shortcuts import render

from django.http import HttpResponse, HttpResponseRedirect
from .tasks import *

def process_emails(request):
    background_process_emails(schedule=0, repeat=30)
    return HttpResponse('ok')
    
def add_test_email(request):
    result = task_add_test_email()
    return HttpResponse(result)