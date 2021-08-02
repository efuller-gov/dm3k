#!/bin/bash

# Run this script you must be within the api docker container
# to run you must..
#  1) start the docker container in dev mode
#      (see dev_env.md in /docs folder)
#  2) exec into the docker container
#       $ sudo docker exec -ti dm3k_open_api bash
#  2) cd into tests directory (within the docker container)
#       $ cd ../tests    # need to be the in /app/tests
#  3) run this file
#       $ source ./run_all_tests.sh
#
# NOTE - Tests must start with test  (eg test*.py)

python -m unittest discover -v -s /app/tests