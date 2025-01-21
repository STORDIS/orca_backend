<p align="center">
<a href="https://hub.docker.com/r/stordis/orca_backend/">
      <img alt="Docker Pulls" src="https://img.shields.io/docker/pulls/stordis/orca_backend?style=for-the-badge&logo=docker&logoColor=white&link=https%3A%2F%2Fhub.docker.com%2Fr%2Fstordis%2Forca_backend"/>
</a>
<a href="https://github.com/stordis/orca_backend/actions">
      <img alt="Tests Passing" src="https://img.shields.io/github/actions/workflow/status/stordis/orca_backend/docker-publish.yml?style=for-the-badge&logo=github&link=https%3A%2F%2Fgithub.com%2FSTORDIS%2Forca_backend%2Factions"/>
</a>
<a href="https://github.com/stordis/orca_backend/issues">
      <img alt="Issues" src="https://img.shields.io/github/issues/stordis/orca_backend?style=for-the-badge&logo=github&link=https%3A%2F%2Fgithub.com%2FSTORDIS%orca_backend%2Fissues"/>
</a>
<a href="https://github.com/stordis/orca_backend/graphs/contributors">
      <img alt="GitHub Contributors" src="https://img.shields.io/github/contributors/stordis/orca_backend?style=for-the-badge&logo=github&link=https%3A%2F%2Fgithub.com%2FSTORDIS%orca_backend%2Fgraphs%2Fcontributors" />
</a>
<a href="https://github.com/stordis/orca_backend/pulls?q=">
      <img alt="GitHub pull requests" src="https://img.shields.io/github/issues-pr/stordis/orca_backend?color=0088ff&style=for-the-badge&logo=github&link=https%3A%2F%2Fgithub.com%2FSTORDIS%orca_backend%2Fpulls" />
</a>
<a href="https://github.com/STORDIS/orca_backend?tab=Apache-2.0-1-ov-file#readme">
      <img alt="License" src="https://img.shields.io/github/license/stordis/orca_backend?style=for-the-badge"/>
</a>

</p>


# ORCA Backend

ORCA Backend is a REST API server written using Django framework to access orca_nw_lib functionalities. It is a backend service that can be used by applications to interact with SONiC Network and devices.

- [ORCA Backend](#orca-backend)
  - [Quick Start orca\_backend](#quick-start-orca_backend)
    - [Installing docker compose plugin](#installing-docker-compose-plugin)
    - [Quick Start ORCA Backend](#quick-start-orca-backend)
  - [APIs and ORCA UI](#apis-and-orca-ui)
    - [Steps to Use APIs](#steps-to-use-apis)
  - [To execute tests](#to-execute-tests)
  - [To Run GitHub Actions Locally](#to-run-github-actions-locally)


## Quick Start orca_backend

orca_backend can be quickly started using docker compose in 2 steps.

### Installing docker compose plugin

Install docker compose plugin using below steps

```sh 
DOCKER_CONFIG=${DOCKER_CONFIG:-$HOME/.docker}
mkdir -p $DOCKER_CONFIG/cli-plugins
curl -SL https://github.com/docker/compose/releases/download/v2.30.3/docker-compose-linux-x86_64 -o $DOCKER_CONFIG/cli-plugins/docker-compose
chmod +x $DOCKER_CONFIG/cli-plugins/docker-compose
```

To check that docker compose plugin successfully installed by running below command

```shell
docker compose version
```



### Quick Start ORCA Backend

ORCA Backend can be started easily by just running below command :

```sh
git clone https://github.com/STORDIS/orca_backend.git
cd orca_backend
docker compose up -d
```

To check that neo4j has successfully started, open https://<server_ip>:7474 with credentials neo4j/password to browse the database.

Container runs on 0.0.0.0:8000 by default. To verify that container has successfully started, try to access http://<server_ip>:8000/admin/ and log in with default user/password- admin/admin which is by default created.

Thats it, If thats enough, rest of the steps below can be skipped and directly proceed with quick start of [orca_ui](https://github.com/STORDIS/orca_ui), which again is as simple as running a docker container and there discover your topology. Else, refer below for more details about build and installation of ORCA backend.

> **_NOTE:_** Several settings have default values if not overriden by environment variables. For more details refer [Configuration](#configuration) section below.

> **_Note for release:_** While using a specific version of orca_backend, it is recommended to use the same version of orca_ui.


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

        export discover_networks="<Device(s) or Network(s) IP.>"
        python manage.py test network.test.test_interface

## To Run GitHub Actions Locally

- Install "act" as explained in [here](https://nektosact.com/installation/index.html?highlight=install#installation).
- Create a github_secret_file and add the secrets used by GitHub Actions file.
  
            STORDIS_DOCKER_HUB_USER="xyz"
            STORDIS_DOCKER_HUB_ACCESS_TOKEN="abc"
- Run GitHub actions locally as follows:

            cd orca_backend
            act --secret-file github_secret_file
