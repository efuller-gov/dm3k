"""
Main file for open-dm3k API
"""
# -------------------------------------------------------------------------
# @license JHUAPL
# Copyright (C) 2021 Johns Hopkins University Applied Physics Laboratory
#
# All Rights Reserved.
# This material may only be used, modified, or reproduced by or for the
# U.S. government pursuant to the license rights granted under FAR
# clause 52.227-14 or DFARS clauses 252.227-7013/7014.
# For any other permission, please contact the Legal Office at JHU/APL.
# --------------------------------------------------------------------------


import os
import logging

from flask import Flask
from flask_cors import CORS
from views import api

import argparse

app = Flask(__name__)
CORS(app)
app.register_blueprint(api)

# logging
# set up logging
app_directory = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')
LOG_DIR = os.path.join(app_directory, 'logs')
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)
log_file = os.path.join(LOG_DIR, 'basic.log')

# clear the file on start up
f = open(log_file, 'w').close()

logging.basicConfig(filename=log_file, 
                    level=logging.DEBUG, 
                    format='%(asctime)s %(levelname)s :: <%(name)s %(threadName)s> {%(module)s:%(lineno)d} - %(message)s')

log = logging.getLogger()
log.debug("Debug Logging ON")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()
    if args.debug:
        print("Running Debug mode!")
        app.run(debug=True, host="0.0.0.0", port=5000)
    else:
        app.run()
