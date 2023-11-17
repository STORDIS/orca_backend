# ORCA Backend
ORCA Backend is a REST API server written using Django framework to access orca_nw_lib functionalities. It is a backend service that can be used by applications to interact with SONiC Netowrk and devices.
## Installing Dependencies
ORCA backend uses poetry for installing all required dependencies. Poetry can be installed using the following command :
        
        pip install poetry

To install dependencies use the following command :

        cd orca_backend
        poetry install

## To run the server :
        python manage.py runserver

## To execute tests :
        python manage.py test network.test.interface_test