import random
import string
import requests
from django.shortcuts import render
from django.views.generic import TemplateView
from django.conf import settings

# Create your views here.


class DashboardView(TemplateView):
    template_name = 'dashboard/dashboard.html'

    def get_context_data(self, **kwargs):
        get_dict = self.request.GET
        context = super().get_context_data(**kwargs)
        context['logged'] = False
        if get_dict.get('state', None) and get_dict.get('code'):
            if self.request.GET.get('state') == self.request.session.get('state'):
                context['logged'] = True
        else:
            state = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
            self.request.session['state'] = state
            context['client_id'] = settings.NETATMO_CLIENT_ID
            context['redirect_url'] = self.request.build_absolute_uri('?')
            context['state'] = state
        return context
