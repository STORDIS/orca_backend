<p align="center">
<a href="https://hub.docker.com/r/stordis/orca_backend/">
      <img alt="Docker Pulls" src="https://img.shields.io/docker/pulls/stordis/orca_backend?style=for-the-badge&logo=docker&logoColor=white&link=https%3A%2F%2Fhub.docker.com%2Fr%2Fstordis%2Forca_backend" />
    </a>
<a href="https://github.com/stordis/orca_backend/actions">
      <img alt="Tests Passing" src="https://img.shields.io/github/actions/workflow/status/stordis/orca_backend/docker-publish.yml?style=for-the-badge&logo=github&link=https%3A%2F%2Fgithub.com%2FSTORDIS%2Forca_backend%2Factions
      " />
</a>
<a href="https://github.com/stordis/orca_backend/issues">
      <img alt="Issues" src="https://img.shields.io/github/issues/stordis/orca_backend?style=for-the-badge&logo=github&link=https%3A%2F%2Fgithub.com%2FSTORDIS%orca_backend%2Fissues
      " />
</a>
<a href="https://github.com/stordis/orca_backend/graphs/contributors">
      <img alt="GitHub Contributors" src="https://img.shields.io/github/contributors/stordis/orca_backend?style=for-the-badge&logo=github&link=https%3A%2F%2Fgithub.com%2FSTORDIS%orca_backend%2Fgraphs%2Fcontributors" />
</a>
<a href="https://github.com/stordis/orca_backend/pulls?q=">
      <img alt="GitHub pull requests" src="https://img.shields.io/github/issues-pr/stordis/orca_backend?color=0088ff&style=for-the-badge&logo=github&link=https%3A%2F%2Fgithub.com%2FSTORDIS%orca_backend%2Fpulls" />
</a>
</p>

# ORCA Backend
ORCA Backend is a REST API server written using Django framework to access orca_nw_lib functionalities. It is a backend service that can be used by applications to interact with SONiC Network and devices.



- [ORCA Backend](#orca-backend)
  - [orca\_backend Quick Start in 2 simple steps](#orca_backend-quick-start-in-2-simple-steps)
    - [Run Neo4j docker container](#run-neo4j-docker-container)
    - [Run orca\_backend docker container](#run-orca_backend-docker-container)
  - [Running orca\_backend from source](#running-orca_backend-from-source)
    - [Install ORCA Backend dependencies](#install-orca-backend-dependencies)
    - [Configuration](#configuration)
    - [Make Migrations](#make-migrations)
    - [Create Django User](#create-django-user)
    - [Finally, Run ORCA Backend:](#finally-run-orca-backend)
    - [Next...](#next)
  - [Build and install orca\_backend docker image from source](#build-and-install-orca_backend-docker-image-from-source)
    - [Create docker image](#create-docker-image)
  - [APIs and ORCA UI](#apis-and-orca-ui)
    - [Steps to Use APIs](#steps-to-use-apis)
  - [To execute tests](#to-execute-tests)


## orca_backend Quick Start in 2 simple steps
ORCA Backend can be started easily by just running 2 docker containers, as follows :

### Run Neo4j docker container
One of the dependencies for ORCA backend orca_nw_lib uses neo4j to store the network topology. To install neo4j easiest is to run Neo4j Docker image in container with the following command :
        
    docker run \
        --name orca_neo4j \
        -p7474:7474 -p7687:7687 \
        -d \
        -v $HOME/neo4j/data:/data \
        -v $HOME/neo4j/logs:/logs \
        -v $HOME/neo4j/import:/var/lib/neo4j/import \
        -v $HOME/neo4j/plugins:/plugins \
        --env NEO4J_AUTH=neo4j/password \
        neo4j:latest
To check that neo4j has successfully started, open https://localhost:7474 with credentials neo4j/password to browse the database.  

### Run orca_backend docker container
Use following command to run orca_backend

        docker run --net="host" -d stordis/orca_backend:latest

To verify that container has successfully started, try to access http://<server_ip>:8000/admin/ and log in with default user/password- admin/admin which is by default created. 

Thats it, If thats enough, rest of the steps below can be skipped and directly proceed with quick start of [orca_ui](https://github.com/STORDIS/orca_ui), which again is as simple as running a docker container and there discover your topology. Else, refer below for more details about build and installation of ORCA backend.


## Running orca_backend from source 
### Install ORCA Backend dependencies
ORCA backend uses poetry for installing all required dependencies. Poetry can be installed using the following command :
        
        pip install poetry

To install all dependencies of ORCA backend use the following command :
        
        git clone https://github.com/STORDIS/orca_backend.git
        cd orca_backend
        poetry install

> **_Troubleshoot:_**   if _"poetry install"_ stuck for long, perform cleanup as follows:
      `poetry env remove --all` \
      `poetry cache clear --all .`      
      `rm -rf $(poetry config cache-dir)/artifacts`     
If issue not resolved, check poetry output in verbose mode as follows :\
      `poetry -vvv install` \
In the output if install process is stuck at _"[keyring.backend] Loading macOS"_ try setting :\
       `export PYTHON_KEYRING_BACKEND=keyring.backends.null.Keyring`

### Configuration
For a quick start with ORCA, defining "discover_networks" environment variable like: `export discover_networks="<comma separated device or network IPs>"` is enough. 

Optionally, there are more params which can be configured (can be set as environment variables). Details of additional params can be found in config section of (ORCA Network Library)[https://github.com/STORDIS/orca_nw_lib]

### Make Migrations
Needed for log_manager do following :

        python manage.py makemigrations log_manager
        python manage.py migrate

### Create Django User
Create Django user as follows :

        cd orca_backend
        python manage.py createsuperuser

The user created here can be used to login to server via orca_ui, or making rest calls using postman etc.

### Finally, Run ORCA Backend:
orca_backend runs like normal django server as follows:

        python manage.py runserver

To verify that django server has successfully started, try accessing (replace localhost with your server address) - <http://localhost:8000/> , Here all the Rest endpoint should be listed. Or to perform admin tasks access- <http://localhost:8000/admin/>. 

### Next...
[Install ORCA UI](https://github.com/STORDIS/orca_ui)
 

## Build and install orca_backend docker image from source
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

>**_Note_** - Above command will also create a default django super user with username/password - admin/admin consider changing password afterwards at <http://localhost:8000/admin/> (replace localhost with orca_backend server address)

## APIs and ORCA UI
Users can always use [orca_ui](https://github.com/STORDIS/orca_ui) which already implements the orca_backend APIs and straight forward when it comes to use ORCA as a whole client server application, User can still use orca_backend REST APIs with out using [orca_ui](https://github.com/STORDIS/orca_ui) to develop custom apps for example.
For a quick start, APIs can be directly used from browser with django rest framework's web interface or from Postman like tools. URLs are available under network/urls.py. Before using APIs a user authentication is required as well. Following is the procedure to use orca_backend APIs using simple curl - 

### Steps to Use APIs

1. Create superuser in Django orca_backend using the command below:
   ```bash
        cd orca_backend
        python manage.py migrate
        python manage.py createsuperuser
   ```
   user_name and password is sufficient to start with.
2. After creating the superuser, use the following login API to generate a token for the user created above:
   ```bash
        curl --location 'http://localhost:8000/auth/login' \
        --header 'Content-Type: application/json' \
        --data-raw '{
                "username": "<username>",
                "password": "<password>"
        }'
   ```

    Example Response:
    ```json
    {
        "token": "f2cb8adc5c0fadc0b38b9505c93378515f96dc98"
    }
    ```

3. Use the generated token above in subsequent API requests by including it in the request header with the key named "Authorization":

    ```bash
    curl --location 'http://localhost:8000/interfaces?mgt_ip=10.10.130.210' \
    --header 'Authorization: Token f2cb8adc5c0fadc0b38b9505c93378515f96dc98'
    ```

## To execute tests
        python manage.py test network.test.interface_test