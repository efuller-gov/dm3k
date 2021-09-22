"""
Tests the full house model from internal interface
"""

import logging
import sys
import unittest

from .test_optimizer_helper import TestOptimizer

log = logging.getLogger(__name__)


class TestFullHouse(TestOptimizer):
    def setUp(self):
        log.info("Testing: " + self.__class__.__name__ + " " + self._testMethodName + "----------")
        self._opt = None
        self._opt_name = "FullHouseViz"

    def tearDown(self):
        pass

    def test_awd_with_ship(self):
        input_dict, output = self._all_steps("AlienWorldDomination_wShip.json", self._opt_name)
        self._check_all(output, input_dict, 6)


if __name__ == "__main__":
    # FOR DEBUGGING USE...
    log = logging.getLogger()
    log.level = logging.DEBUG
    stream_handler = logging.StreamHandler(sys.stdout)
    log.addHandler(stream_handler)

    unittest.main()
