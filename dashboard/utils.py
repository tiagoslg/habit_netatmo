import requests
from django.conf import settings


NETATMO_BASE_URL = 'https://api.netatmo.com/api'
NETATMO_HOMESDATA_URL = NETATMO_BASE_URL + '/homesdata'
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


def get_thermostats():
    access_token = refresh_token()['access_token']
    headers = {"Authorization":"Bearer " + access_token}
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
