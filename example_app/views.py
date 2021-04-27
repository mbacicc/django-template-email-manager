from django.views.generic.base import TemplateView
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
import os
from template_email_manager.manager import TemplateEmailMessage

class IndexView(TemplateView):
    template_name = 'example_app/index.html'

def Example1View(request):

    context={
        'context_integer': 10,
        'context_string': 'Test User'
    }

    tem = TemplateEmailMessage(
        MessagePrototype='daily_number',
        MessageContext=context)

    tem.SendMessage()
    
    return HttpResponseRedirect(reverse('example_app:index'))





def DownloadFixtureView(request,fixture_id): 

    file_pos = os.path.join(
        os.path.dirname(__file__),
        'static',
        'example_app',
        'fixtures',
        'example' + str(fixture_id) + '.json')
    json_str = open(file_pos)   
    response = HttpResponse(json_str, content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename=fixture_example' + str(fixture_id) + '.json'
    return response
