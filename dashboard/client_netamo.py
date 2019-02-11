import logging
import time
import requests
from netatmo.views import NETATMO_HOMESDATA_URL, NETATMO_STATIONSDATA_URL, NETATMO_HOMESTATUS_URL, \
    NETATMO_OAUTH_URL, NETATMO_AUTHORIZE_URL, NETATMO_GETMEASURE_URL
from .logger import Logger, LogTypes


def refresh_token(refresh_token, client_id, client_secret):
    """
    Method used to refresh the social_app token, after it has expired
    :param refresh_token: User refresh token got when authorized the app
    :param client_id: App client_id got when authorized the app
    :param client_secret: App client_secret got when authorized the app
    :return: json with the raw content from Netatmo, if the return status == 200, the new value to access_token will be
    at ['access_token']
    """
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
    """
    Use the access_token to retrive a list of devices for the logged user
    :param access_token: User access token got from refresh_token
    :return: Json with the treated return of two netatmo urls:
        - /getstationsdata
        - /homesdata
    """
    headers = {"Authorization": "Bearer " + access_token}
    resp = requests.get(NETATMO_STATIONSDATA_URL, headers=headers)
    data = resp.json()
    device_list = {
        'stations_devices': [],
        'homes_modules': []
    }
    for device in data['body'].get('devices', []):
        device_list['stations_devices'].append({
            'id': device['_id'],
            'type': device['type'],
            'name': device['module_name'],
            'last_status_store': device['last_status_store'],
            'data_type': device['data_type']
        })
    resp = requests.get(NETATMO_HOMESDATA_URL, headers=headers)
    data = resp.json()
    for home in data['body'].get('homes', []):
        for module in home.get('modules', []):
            device_list['homes_modules'].append({
                'id': module['id'],
                'type': module['type'],
                'name': module['name'],
                'bridge': module.get('bridge', '')
            })
    return device_list


def read_temperature(access_token, device_id, module_id='', start_date=None, end_date=None,
                     timestamp=int(time.time())):
    """
    Read a temperature from a thermostat
    :param access_token: User access token got from refresh_token
    :param device_id: Thermostat bridge ID
    :param module_id: Thermostat module ID
    :param start_date: int timestamp from start date
    :param end_date: int timestamp from end date
    :param timestamp: int current timestamp
    :return: status_code and json from requests method
    """
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

    resp = requests.get(NETATMO_GETMEASURE_URL, params=params)

    return resp.status_code, resp.json()


def read_station_data(access_token, device_id=''):
    """
    Get the information from unique or every user stations
    :param access_token: User access token got from refresh_token
    :param device_id: Station device_id
    :return: status_code and json from requests method
    """
    params = {
        'access_token': access_token,
        'device_id': device_id
    }

    resp = requests.get(NETATMO_STATIONSDATA_URL, params=params)

    return resp.status_code, resp.json()


def log_camera_connection(data):
    """
    Receive data from webhook and log it to a file
    :param data: json parsed from webhook view
    :return:
    """
    camera_id = data.get('camera_id')
    user_id = data.get('user_id')
    level = logging.INFO
    if data.get('event_type') == 'disconnection':
        level = logging.WARNING
    logger = Logger(level, user_id, camera_id,
                    type_log=LogTypes.CAMERA_CON_STATUS.__str__()).my_logger()
    if data.get('event_type') == 'disconnection':
        logger.warning(data)
    else:
        logger.info(data)


def log_camera_monitoring(data):
    """
    Receive data from webhook and log it to a file
    :param data: json parsed from webhook view
    :return:
    """
    camera_id = data.get('camera_id')
    user_id = data.get('user_id')
    level = logging.INFO
    if data.get('event_type') == 'off':
        level = logging.WARNING
    logger = Logger(level, user_id, camera_id,
                    type_log=LogTypes.CAMERA_MON_STATUS.__str__()).my_logger()
    if data.get('event_type') == 'off':
        logger.warning(data)
    else:
        logger.info(data)


def log_camera_sd_card(data):
    """
    Receive data from webhook and log it to a file
    :param data: json parsed from webhook view
    :return:
    """
    level_by_sub_type = {
        1: logging.WARNING,
        2: logging.INFO,
        3: logging.INFO,
        4: logging.INFO,
        5: logging.ERROR,
        6: logging.ERROR,
        7: logging.ERROR,
    }
    camera_id = data.get('camera_id')
    user_id = data.get('user_id')
    event_type = data.get('event_type').lower()
    if event_type == 'sd':
        sub_type = int(data.get('sub_type', 0))
        level = level_by_sub_type.get(sub_type, None)
        if level:
            logger = Logger(level, user_id, camera_id,
                            type_log=LogTypes.CAMERA_SD_CARD.__str__()).my_logger()
            if level == logging.WARNING:
                logger.warning(data)
            elif level == logging.ERROR:
                logger.error(data)
            else:
                logger.info(data)


def general_log(data):
    level = logging.INFO
    camera_id = data.get('camera_id')
    user_id = data.get('user_id')
    logger = Logger(level, user_id, camera_id,
                    type_log=LogTypes.GENERAL.__str__()).my_logger()
    logger.info(data)
