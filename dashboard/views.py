import time
import datetime
import json
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponse
from django.views.generic import TemplateView, View
from .client_netamo import get_devices, read_temperature, read_station_data, log_camera_connection
from .utils import refresh_session_access_token
from .logger import get_log_file_name
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

# Create your views here.


class AccessTokenBaseView(LoginRequiredMixin, TemplateView):
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        refresh_session_access_token(self.request)

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
        access_token = request.GET.get('access_token', None)
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


class GetCameraConnectionStatus(View):

    def get(self, request, device_id, *args, **kwargs):
        status = 200
        if not device_id:
            status = 500
            return JsonResponse({'error': 'You must send a module_id to read a temperature from a Thermostat'},
                                status=status)
        time_event = '--'
        level_event = '--'
        message = '--'
        social_acc = request.user.socialaccount_set.first()
        if social_acc and device_id:
            user_id = social_acc.uid
            f_read = open(get_log_file_name(user_id, device_id), "r")
            f_lines = f_read.readlines()
            f_read.close()
            if f_lines:
                last_line = f_lines[-1]
                last_line = last_line.replace('\n', '')
                line_list = last_line.split(' - ')
                try:
                    time_event = int(time.mktime(datetime.datetime.strptime(line_list[0],
                                                                            "%Y-%m-%d %H:%M:%S").timetuple()))
                    level_event = line_list[2]
                    data = json.loads(line_list[3].replace("\'", '\"'))
                    message = data.get('message')
                except Exception as e:
                    status = 500
                    return JsonResponse({'error': 'Error on read logfile: {}'.format(e.__str__())},
                                        status=status)
        return JsonResponse(data={
            'status': status,
            'time_event': time_event,
            'level_event': level_event,
            'message': message,
            'time_server': int(time.time())
        }, status=status)


@csrf_exempt
@require_POST
def webhook(request):
    """docstring for WebHookView"""
    jsondata = request.body
    data = json.loads(jsondata)
    user_id = data.get('user_id', None)
    if user_id:
        if data.get('event_type') in ['connection', 'disconnection'] and data.get('camera_id'):
            log_camera_connection(data)

    return HttpResponse(status=200)
