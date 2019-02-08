# Tiago Gomes habit_netatmo
Connect to NETATMO API using Python/Django

Example development project: http://34.199.52.187:8000/

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
- Run `make deploy` this command will:

    - check the environment set, 
    - build the project using docker-compose and docker-compose-override files,
    - restart docker, 
    - run all migrations, 
    - collect static files

If you want to start with some data in your database:
- Run `make loaddata` this will load the fixtures with the initial data

The project will starts at http://localhost:8000

## Endpoints

- get_temperature/<str:device_id>/?access_token=<str:acess_token>&module_id=<str:module_id> 

This endpoint gets the temperature from a Thermostat. Module_id is required 
in order to complet the measure View used to get thermostat temperature


    Params:
    - access_token required: User session access_token
    - device_id required: thermostat bridged module, got from client_netatmo.get_devices method
    - module_id required: thermostat module_id, get from client_netatmo.get_devices method
    - start_date optional: timestamp from start date
    - end_date optional: timestamp from end date
    
---------------------------------------------------------------------
- get_station/<str:device_id>/?access_token=<str:acess_token>

This endpoint gets the temperature from a Station. 

    Params:
    - access_token required: User session access_token
    - device_id required: station device_id, got from client_netatmo.get_devices method
    - type_measure required: coma separeted values of measures to get (temperature, co2, humidity, ...)
    - module_id optional: thermostat module_id, get from client_netatmo.get_devices method
    
---------------------------------------------------------------------
- get_camera_con_status/<str:device_id>/

This endpoint reads the Log from camera connection, if it exists, and returns the last status present in log file. 

    Params:
    - device_id required: camera device_id, got from client_netatmo.get_devices method
    
---------------------------------------------------------------------

## Webhook
The webhook address is configured in My app area on Netatmo user dashboard. For the purpouse of this 
example project, we are using a HTTP address, so it's only possible to receive data from the creator
account.

### Webhook address

- http://34.199.52.187:8000/webhook_client/

Gets the posted data received by Netatmo webhook and log the results according to the event_type.

There is no requested attr, but before proced with data treatment it's made a security check on backend
comparing the x-netatmo-secret, received on Header with the Hash256 of the content, using the Client 
Secret as Key:
- x-netatmo-secret == content_hashed256_using_API_Client_secret_as_key

### Webhook logs <url: /webhook_list/>

- Camera changing state: Stores Connection and Disconnection events from user's cameras each camera will create a 
different log file: 

    - Connection event will store an Info log level
    - Disconection event will store a Warning log level

- Camera monitoring state: Stores On ad Off events from user's cameras each camera will create a 
different log file:

    - On event will store an Info log level
    - Off event will store a Warning log level

- Camera SD card state: Stores SD event from user's cameras each camera will create a 
different log file. The log levels here are according to the sub_types:

    - Sub_type 1 will store a Warning log level
    - Sub_type 2, 3 or 4 will store an Info log level
    - Sub_type 5, 6 or 7 will store an Error log level