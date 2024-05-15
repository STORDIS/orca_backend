# ORCA Backend
ORCA Backend is a REST API server written using Django framework to access orca_nw_lib functionalities. It is a backend service that can be used by applications to interact with SONiC Netowrk and devices.


- [ORCA Backend](#orca-backend)
  - [Installing Dependencies](#installing-dependencies)
    - [Install Neo4j](#install-neo4j)
    - [Install ORCA Backend dependencies](#install-orca-backend-dependencies)
  - [Configuration](#configuration)
  - [Run ORCA Backend:](#run-orca-backend)
  - [Run ORCA Backend in docker container](#run-orca-backend-in-docker-container)
    - [Create docker image](#create-docker-image)
  - [APIs](#apis)
  - [To execute tests](#to-execute-tests)



## Installing Dependencies
### Install Neo4j
One of the dependencies for ORCA backend orca_nw_lib uses neo4j to store the network topology. To install neo4j easiest is to run Neo4j Docker image in container with the following command :
        
    docker run \
        --name testneo4j \
        -p7474:7474 -p7687:7687 \
        -d \
        -v $HOME/neo4j/data:/data \
        -v $HOME/neo4j/logs:/logs \
        -v $HOME/neo4j/import:/var/lib/neo4j/import \
        -v $HOME/neo4j/plugins:/plugins \
        --env NEO4J_AUTH=neo4j/password \
        neo4j:latest
Then open https://localhost:7474 with credentials neo4j/password to browse the database.\
### Install ORCA Backend dependencies
ORCA backend uses poetry for installing all required dependencies. Poetry can be installed using the following command :
        
        pip install poetry

To install all dependencies of ORCA backend use the following command :
        
        git clone https://github.com/STORDIS/orca_backend.git
        cd orca_backend
        poetry install

> **_Troubleshoot:_**   if _"poetry install"_ stucks for long, perform cleanup as follows:
>       `poetry env remove --all`\
>       `poetry cache clear --all .`\
>       `rm -rf $(poetry config cache-dir)/artifacts`\
> 
> If issue not resolved, check poetry output in verbose mode as follows :\
>       `poetry -vvv install` \
> In the output if install process is stuck at _"[keyring.backend] Loading macOS"_ try setting :\
>       `export PYTHON_KEYRING_BACKEND=keyring.backends.null.Keyring`

## Configuration
The major configuration required here is for orca_nw_lib. orca_nw_lib is defined as a dependency in [pyproject.toml](./pyproject.toml). Once all the dependencies of orca_backend are installed, orca_nw_lib is available under:             
`<python_venv_path>/lib/python_<version>/site-packages/orca_nw_lib`
In the above directory, following files have update options.
- orca_nw_lib.yml - Device and Neo4j access information. Also the device or network information which needs to be discovered.
- orca_nw_lib_logging.yml - A standard python logging configuration for orca_nw_lib.

## Run ORCA Backend:
orca_backend runs like normal django server as follows:

        python manage.py runserver

## Run ORCA Backend in docker container
Docker image of orca_backend can be created and container cane started as follows:
### Create docker image
First create the docker image as follows:

        cd orca_backend
        docker build -t orca_backend .

If docker image is to be transferred to other machine to run there, first save the image, transfer to desired machine and load there as follows:

        docker save -o orca_backend.tar.gz orca_backend:latest
        scp orca_backend.tar.gz <user_name>@host:<path to copy the image>
        ssh <user_name>@host
        cd <path to copy the image>
        docker load -i orca_backend.tar.gz

Docker container can be started as follows:

        docker run --net="host" orca_backend


## APIs
When not using [orca_ui](https://github.com/STORDIS/orca_ui), APIs from orca_backend can also be used. Under orca_backend/network there are python modules for configuration.
API can be directly used from browser with django rest framework's web interface. URLs are available under network/urls.py.\
e.g. \
- http://localhost:8000/interfaces?mgt_ip=10.10.130.210
- http://localhost:8000/devices


## To execute tests
        python manage.py test network.test.interface_test