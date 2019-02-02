import json
import random
import requests
import string
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
                headers = {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}
                url = 'https://api.netatmo.com/oauth2/token'
                data = {
                    'grant_type': 'authorization_code',
                    'client_id': settings.NETATMO_CLIENT_ID,
                    'client_secret': settings.NETATMO_CLIENT_SECRET,
                    'code': get_dict.get('code'),
                    'redirect_uri': self.request.build_absolute_uri('?'),
                    'scope': 'read_thermostat'
                }
                response = requests.post(url, headers=headers, data=data)
                if response.status_code == 200:
                    json_response = response.json()
                    access_token = json_response['access_token']
                    api_url = "https://api.netatmo.com/api/getuser?access_token={}".format(access_token)
                    response = requests.get(api_url)
                    user_mail = response.json()['body']['mail']
                    context['logged'] = True
                    context['user_mail'] = user_mail
        else:
            state = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
            self.request.session['state'] = state
            context['client_id'] = settings.NETATMO_CLIENT_ID
            context['redirect_url'] = self.request.build_absolute_uri('?')
            context['state'] = state
        return context
