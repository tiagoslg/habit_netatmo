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


def read_thermostat():
    access_token = refresh_token()['access_token']
    headers = {"Authorization": "Bearer " + access_token}
    thermostats = get_thermostats()
    device_id = thermostats['body']['homes'][0]['modules'][0]['id'],
    module_id = thermostats['body']['homes'][0]['modules'][1]['id']

    params = {
        'access_token': access_token,
        'device_id': device_id,
        'module_id': module_id,
        'scale': 'max',
        'type': 'temperature,sp_temperature,boileron'
    }

    r = requests.get(NETATMO_GETMEASURE_URL, params=params)

    return r.json()
