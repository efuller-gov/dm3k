
from flask import request
from flask_restful import Resource
from sqlalchemy import text as sql_text


class Quote(Resource):
    """ The quotes View """

    def __init__(self):
        pass

    def get(self):
        """ Returns a list of quotes """
        return {
            'quotes': ['george', 'me']
        }

    def post(self):
        return True

