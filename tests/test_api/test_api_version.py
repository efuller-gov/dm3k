"""
Tests API to check for basic connectivity
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


import logging
import unittest
from unittest import TestCase

import requests

log = logging.getLogger(__name__)

# for this test we assume that api is in dev mode - see docker-compose-dev.yml for internal port
URL = "http://localhost:5000"


class TestBasicConnectionAPI(TestCase):
    def setUp(self):
        log.info("Testing: " + self.__class__.__name__ + " " + self._testMethodName + "----------")

    def tearDown(self):
        pass

    def test_version(self):
        version_url = URL + "/api/version"
        response = requests.get(version_url)

        log.debug("GET: " + str(version_url))
        log.debug("  response code: " + str(response.status_code))
        log.debug("  response headers: " + str(response.headers["content-type"]))
        log.debug("  response text: \n" + str(response.text))
        log.debug("  response json: \n" + str(response.json()))

        self.assertEqual(response.json(), {"api_version": "1.0"})


if __name__ == "__main__":
    # FOR DEBUGGING USE...
    import sys

    log = logging.getLogger()
    log.level = logging.DEBUG
    stream_handler = logging.StreamHandler(sys.stdout)
    log.addHandler(stream_handler)

    unittest.main()
