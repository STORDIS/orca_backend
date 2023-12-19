# ORCA Backend
ORCA Backend is a REST API server written using Django framework to access orca_nw_lib functionalities. It is a backend service that can be used by applications to interact with SONiC Netowrk and devices.
## Installing Dependencies
ORCA backend uses poetry for installing all required dependencies. Poetry can be installed using the following command :
        
        pip install poetry

To install dependencies use the following command :

        cd orca_backend
        poetry install

## Configuration
Configuration for network app are available under orca_backend/network/config/ directory.
Which has 2 files for configuration :\
- orca.yml - Device and Neo4j access information. Also the device or newtwork information which needs to be discovered.
- logging.yml - A standard python logging configuration for orca_nw_lib.

## APIs
Under orca_backend/network there are python modules for configuration.
API can be directly used from browser with django rest framework's web interface. URLs are available under network/urls.py.\
e.g. \
http://localhost:8000/interfaces?mgt_ip=10.10.130.210\
http://localhost:8000/devices

## To run the server :
orca_backend runs like normal django server as follows\

        python manage.py runserver

## To execute tests :
        python manage.py test network.test.interface_test