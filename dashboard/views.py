import random
import requests
import string
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views.generic import TemplateView, View
from django.conf import settings
from .client_netamo import get_devices, read_temperature, read_station_data
from .utils import refresh_session_access_token

# Create your views here.


class AccessTokenBaseView(LoginRequiredMixin, TemplateView):
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        refresh_session_access_token(self.request)

        return context


class SigninView(TemplateView):
    template_name = 'dashboard/signin.html'

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
                    'scope': get_dict.get('scope')
                }
                response = requests.post(url, headers=headers, data=data)
                if response.status_code == 200:
                    json_response = response.json()
                    access_token = json_response['access_token']
                    context['access_token'] = access_token
                    context['refresh_token'] = json_response['refresh_token']
                    context['scope'] = json_response['scope']
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


class DashboardView(AccessTokenBaseView):
    template_name = 'dashboard/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        access_token = self.request.session.get('access_token')
        if access_token:
            context['devices'] = get_devices(access_token)
        return context


class RefreshAccessToken(View):

    def post(self, request, *args, **kwargs):
        refresh_session_access_token(request)
        ret = {
            'access_token': request.session['access_token'],
            'token_expires': request.session['token_expires']
        }
        return JsonResponse(ret, status=200)


class GetThermostatTemperature(View):

    def get(self, request, device_id, *args, **kwargs):
        module_id = request.GET.get('module_id', None)
        if not module_id:
            status = 500
            return JsonResponse({'error': 'You must send a module_id to read a temperature from a Thermostat'},
                                status=status)
        start_date = request.GET.get('start_date', None)
        end_date = request.GET.get('end_date', None)
        access_token = request.session.get('access_token', None)
        status, result = read_temperature(access_token, device_id, module_id=module_id, start_date=start_date,
                                          end_date=end_date)
        num_mesures = result['body'].__len__()
        if num_mesures == 0:
            data = {
                'found': False,
            }
        else:
            data = {
                'found': True,
                'results': [['Temperature', result['body'][num_mesures - 1]['value'][0]]],
                'beg_time': result['body'][num_mesures - 1]['beg_time']
            }
        return JsonResponse({'status': status,
                             'device_id': device_id,
                             'module_id': module_id,
                             'data': data,
                             'time_server': result['time_server']}, status=status)


class GetStationData(View):

    def get(self, request, device_id, *args, **kwargs):
        module_id = request.GET.get('module_id', None)
        type_measure = request.GET.get('type_measure', None)
        access_token = request.GET.get('access_token', None)
        status, result = read_station_data(access_token, device_id)
        if result['body'].__len__() == 0:
            data = {
                'found': False,
                'time_server': result['time_server']
            }
        else:
            type_measure_list = type_measure.split(',')
            result_dict = result['body']['devices'][0]['dashboard_data']
            result_list = []
            for i in range(0, len(type_measure_list)):
                result_list.append([type_measure_list[i].title(), result_dict.get(type_measure_list[i])])
            beg_time = result['body']['devices'][0]['last_status_store']
            data = {
                'found': True,
                'results': result_list,
                'beg_time': beg_time
            }
        return JsonResponse({'status': status,
                             'device_id': device_id,
                             'module_id': module_id,
                             'data': data,
                             'time_server': result['time_server']}, status=status)
