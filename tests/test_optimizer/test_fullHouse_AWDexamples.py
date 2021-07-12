"""
Tests the full house model ingest from viz input
"""
import logging
import os
import unittest
from unittest import TestCase

from dm3k.slim_optimizer.full_house.full_house_input_viz import FullHouseInputViz

log = logging.getLogger(__name__)


class TestFullHouseVIZ(TestCase):
    def setUp(self):
        log.info("Testing: " + self.__class__.__name__ + " " + self._testMethodName + "----------")

    def tearDown(self):
        pass

    def test_awd_ingest(self):
        fh_input = FullHouseInputViz()

        path_to_file = os.path.abspath(os.path.dirname(__file__))  # path to local dm3k-viz.json

        log.debug("Looking for file at: " + path_to_file)

        fatal, val_err_list = fh_input.ingest_validate(path_to_file)

        log.debug("INGEST RESULTS")
        log.debug(fatal)
        log.debug(val_err_list)
        log.debug(fh_input._data)

        self.assertFalse(fatal)


if __name__ == "__main__":
    # FOR DEBUGGING USE...
    import sys

    log = logging.getLogger()
    log.level = logging.DEBUG
    stream_handler = logging.StreamHandler(sys.stdout)
    log.addHandler(stream_handler)

    unittest.main()
