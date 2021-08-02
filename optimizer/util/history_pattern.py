"""
This provides a common framework to track the history of steps within an optimizer,
 including the time and memory required to load, solve, etc.

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
from datetime import datetime

from optimizer.util.util import time_mem_stamp

log = logging.getLogger(__name__)


class HistoryManager:
    def __init__(self):
        log.debug("Initializing the History Manager")
        self._metrics_history = []
        self._tag_dict = {}

    def start_tag(self, tag_string):
        """
        Creates a start tag entry in tag_dict.

        :param str tag_string: The key for the new entry
        :return: None
        """
        time, memory = time_mem_stamp()
        # log.debug("start_tag: %s with time %s and memory %s", tag_string, time, memory)
        self._tag_dict[tag_string] = {"time": time, "memory": memory}

    def end_tag(self, tag_string):
        """
        Creates a end tag entry in tag_dict

        :param str tag_string: The key for the new entry
        :return: None
        """
        prev_time = self._tag_dict[tag_string]["time"]
        prev_memory = self._tag_dict[tag_string]["memory"]
        curr_time, curr_memory = time_mem_stamp()
        diff_time = curr_time - prev_time
        diff_memory = curr_memory - prev_memory
        # log.debug("end_tag: %s with time %s and memory %s", tag_string, curr_time, curr_memory)
        metric_dict = {
            "datetime": datetime.now(),
            "operation": tag_string,
            "time_to_run_sec": diff_time.total_seconds(),
            "memory_gain_MB": diff_memory,
            "end_memory_MB": curr_memory,
        }
        self._metrics_history.append(metric_dict)
        # log.debug("Removing %s entry from self._tag_dict", tag_string)
        del self._tag_dict[tag_string]

    def get_history(self):
        """

        :return: A list of dict entries
        """
        log.debug("Returning self._metrics_history")
        return self._metrics_history
