"""
API Endpoints for open-dm3k API
"""

import os
import sys

from flask import Blueprint
from flask import current_app as app
from flask import jsonify, request

# ensure that optimizer directory is in path
app_directory = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..")
if app_directory not in sys.path:
    sys.path.append(app_directory)

from optimizer.slim_optimizer_main import create_opt  # noqa: E402
from optimizer.slim_optimizer_main import algorithm_dict  # noqa: E402

api = Blueprint("api", __name__)


@api.route("/api/version", methods=["GET"])
def get_version():
    """
    GET /api/version

    :return dict version: the version of the current API
    """
    return {"api_version": "1.0"}


@api.route("/api/optimizers", methods=["GET"])
def get_optimizers():
    """
    GET /api/optimizers

    :return list of optimizers
    """
    opt_list = list(algorithm_dict.keys())
    if "default" in opt_list:
        opt_list.remove("default")

    return jsonify(opt_list)


@api.route("/api/vizdata", methods=["POST"])
def post_vizdata():
    """
    POST /api/vizdata

    :return dict response: results of optimization of post data
        (for full POST API details see /docs/api_devGuide.md)
    """

    app.logger.info("Viz Data POST")
    
    input_dict = request.json
    app.logger.debug(input_dict)

    config = {"optimizer": input_dict["algorithm"]}

    opt, validation_errors = create_opt(input_dict, config)

    if len(validation_errors) > 0:
        app.logger.warning("VALIDATION ERRORS...")
        for e in validation_errors:
            app.logger.warning(e)

        # TODO - we should update this
        err_response = {"body": validation_errors, "reason": "Validation Errors in input data", "statusCode": 400}

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
    response = {"body": all_results, "reason": "OK", "statusCode": 200}

    return jsonify(response)
