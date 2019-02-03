import time
import requests
from django.conf import settings


NETATMO_BASE_URL = 'https://api.netatmo.com/api'
NETATMO_HOMESDATA_URL = NETATMO_BASE_URL + '/homesdata'
NETATMO_STATIONSDATA_URL = NETATMO_BASE_URL + '/getstationsdata'
NETATMO_HOMESTATUS_URL = NETATMO_BASE_URL + '/homestatus'
NETATMO_OAUTH_URL = 'https://api.netatmo.com/oauth2/token'
NETATMO_GETMEASURE_URL = NETATMO_BASE_URL + '/getmeasure'


def refresh_token():
    headers = {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}
    payload = {
        'grant_type': 'refresh_token',
        'refresh_token': settings.REFRESH_TOKEN,
        'client_id': settings.NETATMO_CLIENT_ID,
        'client_secret': settings.NETATMO_CLIENT_SECRET
    }
    response = requests.post(NETATMO_OAUTH_URL, data=payload, headers=headers)
    return response.json()


def get_devices():
    access_token = refresh_token()['access_token']
    headers = {"Authorization": "Bearer " + access_token}
    r = requests.get(NETATMO_STATIONSDATA_URL, headers=headers)
    data = r.json()
    device_list = {
        'stations_devices': [],
        'homes_modules': []
    }
    for device in data['body']['devices']:
        device_list['stations_devices'].append({
            'id': device['_id'],
            'type': device['type'],
            'name': device['module_name'],
            'last_status_store': device['last_status_store'],
            'data_type': device['data_type']
        })
    r = requests.get(NETATMO_HOMESDATA_URL, headers=headers)
    data = r.json()
    for home in data['body']['homes']:
        for module in home['modules']:
            device_list['homes_modules'].append({
                'id': module['id'],
                'type': module['type'],
                'name': module['name'],
                'bridge': module.get('bridge', '')
            })
    return device_list


def get_thermostats():
    access_token = refresh_token()['access_token']
    headers = {"Authorization": "Bearer " + access_token}
    r = requests.get(NETATMO_HOMESDATA_URL, headers=headers)
    data = r.json()
    return data


def read_temperature(device_id, module_id='', start_date=None, end_date=None, access_token=None,
                     timestamp=int(time.time())):
    if not device_id:
        return {'error', 'You must provide a device id'}
    if not access_token:
        access_token = refresh_token()['access_token']
    if not start_date or end_date:
        end_date = timestamp
        start_date = end_date - 3600

    params = {
        'access_token': access_token,
        'device_id': device_id,
        'module_id': module_id,
        'scale': 'max',
        'type': 'temperature',
        'date_begin': start_date,
        'date_end': end_date
    }

    r = requests.get(NETATMO_GETMEASURE_URL, params=params)

    return r.status_code, r.json()


def read_station_data(device_id, module_id='', start_date=None, end_date=None, access_token=None,
                      type_measure='', timestamp=int(time.time())):
    if not device_id:
        return {'error', 'You must provide a device id'}
    if not access_token:
        access_token = refresh_token()['access_token']
    if not start_date or end_date:
        end_date = timestamp
        start_date = end_date - 24*3600
    if not type_measure:
        type_measure = 'temperature'
    params = {
        'access_token': access_token,
        'device_id': device_id,
        'module_id': module_id,
        'scale': '1hour',
        'type': type_measure.lower(),
        'date_begin': start_date,
        'date_end': end_date
    }

    r = requests.get(NETATMO_GETMEASURE_URL, params=params)

    return r.status_code, r.json()

