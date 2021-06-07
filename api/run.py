from flask import Flask
from flask_cors import CORS
from flask_restful import Api
from views import Quote

import argparse

app = Flask(__name__)
CORS(app)
api = Api(app)


api.add_resource(Quote, '/')

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()
    if args.debug:
        print("Running Debug mode!")
        app.run(debug=True, host="0.0.0.0", port=5000)
    else:
        app.run()
