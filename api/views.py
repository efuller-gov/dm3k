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
    def __init__(self):
        pass

    def get(self):
        return {'api_version': "1.0"}

class VizInput(Resource):
    def __init__(self):
        pass

    def post(self):
    
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
            err_response = make_response(jsonify(validation_errors), 400)
            err_response.headers["Content-Type"] = "application/json"
            return err_response
        else:
            app.logger.debug("No Validation errors")

        opt.build()
        opt.solve()
        results = opt.get_output()

        all_results = results.to_dict()
        all_results["allocations"] = results.get_allocations()
        all_results["objective_value"] = results.get_objective_value()

        return jsonify(all_results)


