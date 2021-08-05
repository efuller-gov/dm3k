# OPEN-DM3K DEVELOPMENT ENVIRONMENT

This README file explains how to set up and work with the docker system in the development mode for OPEN-DM3K

Table of Contents:

[[_TOC_]]


## Installation

### Prerequisites

Installation assumes you have...

- docker (v19.03+)  see https://docs.docker.com/get-docker/
- docker-compose (v1.27+)  see https://docs.docker.com/compose/install/

### Installation Procedure

from the main directory of the repo run...

```bash
$ sudo docker-compose -f docker-compose-dev.yml up --build -d
```

To confirm the installation, run...

```bash
$ sudo docker ps
```

Output of this command should show 3 docker containers: dm3k_open_api, dm3k_open_ui, dm3k_open_nginx.  With status as not restarting.

To stop OPEN-DM3K, run...

```bash
$ sudo docker-compose -f docker-compose-dev.yml down
```

## Usage

Connect to the UI by pointing your web browser to:  http://{hostname}/ui 

where hostname is the name or ip address of the machine that is running docker.

For details on how to use the UI to create/solve resource allocation problems see ./docs/user_guide.md

To confirm the API is working you can point your browser to: http://{hostname}/api/version

This should return `{"api_version":"1.0"}`

## UI Container Development

Within development mode, the system will hot reload any changes within the following directories:

- ./ui/public
- ./ui/src

If hot reload does not occur, try the following...

1. Ctrl-R in the browser.  This should force a hard reload.
2. If #1 doesnt work, try restarting the ui container by running...

    ```bash
    $ sudo docker restart dm3k_open_ui
    ```

if you need to add new node_modules, you will need to make the change in 'package.json' and then re build the container, by running...

```bash
$ sudo docker-compose -f docker-compose-dev.yml down
$ sudo docker-compose -f docker-compose-dev.yml up
```

> **IMPORTANT**:  If you do add new node_modules, make sure you grab the new yarn.lock file from inside the docker container so that it can be saved to the repo.  Grab the new yarn.lock file by running...
>   ```bash
>   $ cd ui    # get into the ui directory of the repo  
>   $ sudo docker cp dm3k_open_ui:/app/yarn.lock .
>   ```

If you need to get inside of the ui container, run...

```bash
$ sudo docker exec -ti dm3k_open_ui /bin/sh
```

To exit the container, run...

```bash
/app$ exit
```

To stop the container, run...

```bash
$ sudo docker-compose -f docker-compose-dev.yml down
```

## API Container Development

Within development mode, the system will hot reload any changes within the following directories:

- ./api
- ./examples
- ./optimizer
- ./tests

If hot reload does not occur, try restarting the api container by running...

```bash
$ sudo docker restart dm3k_open_api
```

if you need to add new python packages, you will need to change either the api requirements.txt or the optimizer requirements.txt (depending on what you want) and then re build the container, by running...

```bash
$ sudo docker-compose -f docker-compose-dev.yml down
$ sudo docker-compose -f docker-compose-dev.yml up
```

If you need to get inside of the api container, run...

```bash
$ sudo docker exec -ti dm3k_open_api bash
```

Once inside the container you can run any test, by running...

```bash
/app/api$ cd ../tests           # get to the test directory at top of repo
/app/api$ cd {test_directory}   # whatever tests you want to run
/app/api$ python {test_file}.py 
```

Logs from the test will appear on the screen.

To exit the container, run...

```bash
/app$ exit
```

To stop the container, run...

```bash
$ sudo docker-compose -f docker-compose-dev.yml down
```
