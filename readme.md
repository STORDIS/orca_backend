# ORCA Backend
ORCA Backend is a REST API server written using Django framework to access orca_nw_lib functionalities. It is a backend service that can be used by applications to interact with SONiC Netowrk and devices.
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
Configuration for network app are available under orca_backend/network/config/ directory.
Which has 2 files for configuration :
- orca.yml - Device and Neo4j access information. Also the device or newtwork information which needs to be discovered.
- logging.yml - A standard python logging configuration for orca_nw_lib.

## Run ORCA Backend:
orca_backend runs like normal django server as follows\

        python manage.py runserver

## APIs
Under orca_backend/network there are python modules for configuration.
API can be directly used from browser with django rest framework's web interface. URLs are available under network/urls.py.\
e.g. \
- http://localhost:8000/interfaces?mgt_ip=10.10.130.210
- http://localhost:8000/devices


## To execute tests :
        python manage.py test network.test.interface_test