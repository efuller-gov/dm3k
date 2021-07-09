# AW UI
UI for the Eng Alg

## For Production
```
$ cd aw_ui
$ sudo docker compose --build -d 
```   

## For development
```
$ cd aw_ui
$ sudo docker-compose -f docker-compose-dev.yml up --build -d
``` 

### on API
Make change and then "Cntl-R" on browser and it should **hot reload**

IF NOT...
```
$ sudo docker restart api
```

### on UI
Make change and then it should **hot reload**



## Project was based on BELOW

Please find the tutorial at https://medium.com/@samy_raps/flask-vue-mysql-on-docker-part-i-setting-up-320d55a85971

### Important commands

Create a folder called `data` inside the `db` folder.

Build and run :: `docker-compose up --build`

Build and run in the background and view logs for all the instances ::
`docker-compose up --build -d && docker-compose logs --tail=all -f`

Stop instances :: docker-compose down

Stop and Delete all containers :: `docker container stop $(docker container ls -aq) && docker container rm $(docker container ls -aq)`

_Cheers!_


FOR API CONTAINER
sudo docker exec -ti dm3k_open_api bash


FOR UI CONTAINER
sudo docker exec -ti dm3k_open_ui /bin/sh
