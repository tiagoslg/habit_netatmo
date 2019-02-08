# Tiago Gomes habit_netatmo
Connect to NETATMO API using Python/Django

## Requirements
This project requires Docker and Docker compose. Both **must be installed** on local machine

Link with instructions to install Docker on Ubuntu:
    https://docs.docker.com/engine/installation/linux/ubuntu/

Link with instructions to install Docker compose:
    https://docs.docker.com/compose/install/#install-compose

Pay attention to linux post install instructions:
    https://docs.docker.com/install/linux/linux-postinstall/

## Running this project:

- Install Docker and Docker compose
- Clone this project in your locall machine
- Access the folder
- Run `make set_env_development` to setup the development environment 
(this project is not ready to run production env)
- Run `make deploy` this command will check the environment, build the project
using docker-compose and docker-compose-override files, restart docker, run all 
the migrations, collect static files

If you want to start with some data in your database:
- Run `make loaddata` this will load the fixtures with the initial data

The project will start at http://localhost:8000

## Endpoints

- get_temperature/<str:device_id>/?access_token=<str:acess_token>&module_id=<str:module_id> 

This endpoint get the temperature from a Thermostat. Module_id is required 
in order to complet the measure View used to get thermostat temperature


    Params:
    - access_token required: User session access_token
    - device_id required: thermostat bridged module, got from client_netatmo.get_devices method
    - module_id required: thermostat module_id, get from client_netatmo.get_devices method
    - start_date optional: timestamp from start date
    - end_date optional: timestamp from end date
    
---------------------------------------------------------------------
- get_station/<str:device_id>/?access_token=<str:acess_token>

This endpoint get the temperature from a Station. 

    Params:
    - access_token required: User session access_token
    - device_id required: station device_id, got from client_netatmo.get_devices method
    - type_measure required: coma separeted values of measures to get (temperature, co2, humidity, ...)
    - module_id optional: thermostat module_id, get from client_netatmo.get_devices method
    
---------------------------------------------------------------------
- get_camera_con_status/<str:device_id>/

This endpoint read the Log from camera connection and return the last status in log file. 

    Params:
    - device_id required: camera device_id, got from client_netatmo.get_devices method
    
---------------------------------------------------------------------
