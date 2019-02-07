import time
import requests
from netatmo.views import NETATMO_HOMESDATA_URL, NETATMO_STATIONSDATA_URL, NETATMO_HOMESTATUS_URL, \
    NETATMO_OAUTH_URL, NETATMO_AUTHORIZE_URL, NETATMO_GETMEASURE_URL


def refresh_token(refresh_token, client_id, client_secret):
    headers = {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}
    payload = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': client_id,
        'client_secret': client_secret
    }
    response = requests.post(NETATMO_OAUTH_URL, data=payload, headers=headers)
    return response.json()


def get_devices(access_token):
    headers = {"Authorization": "Bearer " + access_token}
    resp = requests.get(NETATMO_STATIONSDATA_URL, headers=headers)
    data = resp.json()
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
    resp = requests.get(NETATMO_HOMESDATA_URL, headers=headers)
    data = resp.json()
    for home in data['body']['homes']:
        for module in home['modules']:
            device_list['homes_modules'].append({
                'id': module['id'],
                'type': module['type'],
                'name': module['name'],
                'bridge': module.get('bridge', '')
            })
    return device_list


def get_thermostats(access_token):
    headers = {"Authorization": "Bearer " + access_token}
    r = requests.get(NETATMO_HOMESDATA_URL, headers=headers)
    data = r.json()
    return data


def read_temperature(access_token, device_id, module_id='', start_date=None, end_date=None,
                     timestamp=int(time.time())):
    if not device_id:
        return {'error', 'You must provide a device id'}
    if not end_date:
        end_date = timestamp
    if not start_date:
        start_date = end_date - 3600

    params = {
        'access_token': access_token,
        'device_id': device_id,
        'module_id': module_id,
        'scale': 'max',
        'type': 'temperature',
        'date_begin': int(start_date),
        'date_end': int(end_date)
    }

    r = requests.get(NETATMO_GETMEASURE_URL, params=params)

    return r.status_code, r.json()


def read_station_data(access_token, device_id=''):
    params = {
        'access_token': access_token,
        'device_id': device_id
    }

    resp = requests.get(NETATMO_STATIONSDATA_URL, params=params)

    return resp.status_code, resp.json()

