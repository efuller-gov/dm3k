"""
Tests API vizinput interface to run the optimizer
"""

import json
import logging
import os
import unittest
from unittest import TestCase

import requests

log = logging.getLogger(__name__)

# make sure we can get access to examples
app_directory = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..")

# for this test we assume that api is in dev mode - see docker-compose-dev.yml for internal port
URL = "http://localhost:5000"


class TestVizInput(TestCase):
    def setUp(self):
        log.info("Testing: " + self.__class__.__name__ + " " + self._testMethodName + "----------")

    def tearDown(self):
        pass

    # ---------------------------------------------
    #  UTILITY FUNCTIONS
    # ---------------------------------------------

    def _load(self, data_filename):
        path_to_file = os.path.join(app_directory, "examples", data_filename)
        with open(path_to_file, "r") as f:
            input_dict = json.load(f)

        # for now, add algorithm = KnapsackViz
        input_dict["algorithm"] = "KnapsackViz"

        return input_dict

    # ---------------------------------------------
    #  TESTS AGAINST INPUT FILES
    # ---------------------------------------------

    def test_viz_input_simple_knapsack(self):
        vizinput_url = URL + "/api/vizdata"

        input_dict = self._load("simpleKnapsack.json")
        log.debug(input_dict)

        response = requests.post(vizinput_url, json=input_dict)

        log.debug("POST: " + str(vizinput_url))
        log.debug("request data:\n" + json.dumps(input_dict, indent=4))
        log.debug("  response code: " + str(response.status_code))
        log.debug("  response headers: " + str(response.headers["content-type"]))
        log.debug("  response text: \n" + str(response.text))
        log.debug("  response json: \n" + str(response.json()))


if __name__ == "__main__":
    # FOR DEBUGGING USE...
    import sys

    log = logging.getLogger()
    log.level = logging.DEBUG
    stream_handler = logging.StreamHandler(sys.stdout)
    log.addHandler(stream_handler)

    unittest.main()
