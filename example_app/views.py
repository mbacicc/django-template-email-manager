from django.views.generic.base import TemplateView
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from template_email_manager.commands import add_email_to_queue

class IndexView(TemplateView):
    template_name = 'example_app/index.html'

def AddEmailView(request):
    # TODO add email to the manager
    print('Email Added to queue')
    return HttpResponseRedirect(reverse('example_app:index'))