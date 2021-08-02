"""
API Endpoints for open-dm3k API
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
import sys

from flask import request, jsonify, make_response
from flask import current_app as app
from flask_restful import Resource

# ensure that optimizer directory is in path
app_directory = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')
if app_directory not in sys.path:
    sys.path.append(app_directory)

from optimizer.slim_optimizer_main import create_opt

class Version(Resource):
    """
    Simple Endpoint for checking aliveness and providing API version
    """
    def __init__(self):
        pass

    def get(self):
        """
        GET /api/version

        :return dict version: the version of the current API
        """
        return {'api_version': "1.0"}

class VizInput(Resource):
    """
    Endpoint for taking in data from the UI
    """
    def __init__(self):
        pass

    def post(self):
        """
        POST /api/vizdata

        :return dict response: results of optimization of post data
            (for full POST API details see /docs/api_devGuide.md)
        """
    
        app.logger.info("Viz Data POST")
        app.logger.debug(request.get_data())

        input_dict = request.json
        app.logger.debug(input_dict)

        config = {"optimizer": input_dict['algorithm']}

        opt, validation_errors = create_opt(input_dict, config)

        if len(validation_errors) > 0:
            app.logger.warning("VALIDATION ERRORS...")
            for e in validation_errors:
                app.logger.warning(e)
            
            # TODO - we should update this
            err_response = {
                "body": validation_errors,
                "reason": "Validation Errors in input data",
                "statusCode": 400
            }

            return jsonify(err_response)
        else:
            app.logger.debug("No Validation errors")

        opt.build()
        opt.solve()
        results = opt.get_output()

        all_results = results.to_dict()
        all_results["allocations"] = results.get_allocations()
        all_results["objective_value"] = results.get_objective_value()

        # TODO - we should update this 
        response = {
            "body": all_results,
            "reason": "OK",
            "statusCode": 200
        }

        return jsonify(response)


