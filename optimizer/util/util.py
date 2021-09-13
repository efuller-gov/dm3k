"""
Contains utility functions used by all of optimizer
"""

import logging
import os
import time
from datetime import datetime

import psutil

log = logging.getLogger(__name__)

convertToMB = float(2 ** 20)
process = psutil.Process()

FULL_HOUSE_FULL_TRACE_KEYS = [
    "allocated",
    "activity",
    "budget_used",
    "picked",
    "resource",
    "selected",
    "value",
]

FULL_HOUSE_FULL_TRACE_KEYS_ORIG = [
    "container_name",
    "child_budget_used",
    "child_resource",
    "child_activity",
    "parent_budget_used",
    "parent_resource",
    "parent_activity",
    "selected",
    "value",
]

FULL_HOUSE_INPUT_DICT_KEYS = [
    "req_child_amt",
    "req_parent_amt",
    "avail_child_amt",
    "avail_parent_amt",
    "activity_children",
    "child_possible_allocations",
    "parent_possible_allocations",
    "child_score",
    "resource_families",
]

FULL_HOUSE_INPUT_LIST_KEYS = ["child_resources", "parent_resources", "child_activities", "parent_activities", "force_list", "forbid_list"]

FULL_HOUSE_INPUT_KEYS = FULL_HOUSE_INPUT_DICT_KEYS + FULL_HOUSE_INPUT_LIST_KEYS + ["parent_budget_name"] + ["child_budget_name"]


def remove_old_temp_files(dir_name, days=0, hours=0, minutes=0, seconds=0):
    """
    Remove old temp files. Defaults to keeping only temp files created in last hour
    """
    now = time.time()
    hours = (days * 24) + hours
    minutes = (hours * 60) + minutes
    seconds = (minutes * 60) + seconds
    if seconds == 0:
        seconds = 3600
    old = now - seconds
    for f in os.listdir(dir_name):
        try:
            path = os.path.join(dir_name, f)
            if os.stat(path).st_ctime < old:
                os.remove(path)
        except FileNotFoundError as e:
            # Fail silently if this exception occurs
            log.warning(e)


def time_mem_stamp():
    """
    return the current time and memory usage

    :return time_stamp: the current time in as datetime object.
    :return mem_stamp: the current memory amount as
    """
    return datetime.now(), process.memory_info()[0] / convertToMB


def fh_append(append_dict, key, value, type_resources=None):
    """
    Helper method that will set the given default value (typically list or dict) if the key does not exist in the append_dict yet

    :param append_dict:
    :param key:
    :param value:
    :param str type_resources: Set to "child_resources" or "parent_resources" if modifying the resource_families dict
    :return: None
    """
    default_type = []
    if type_resources is not None:
        default_type = {"parent_resources": [], "child_resources": []}

    append_dict.setdefault(key, default_type)
    if type_resources is None:
        if value not in append_dict[key]:
            append_dict[key].append(value)
    else:
        if value not in append_dict[key][type_resources]:
            append_dict[key][type_resources].append(value)


#
def fh_extend(extend_dict, key, values, type_resources=None):
    """
     Helper method that will set the given default value (typically list or dict) if the key does not exist in the extend_dict yet

    :param extend_dict:
    :param key:
    :param values:
    :param str type_resources: Set to "child_resources" or "parent_resources" if modifying the resource_families dict
    :return: None
    """
    default_type = []
    if type_resources is not None:
        default_type = {"parent_resources": [], "child_resources": []}

    extend_dict.setdefault(key, default_type)
    if type_resources is None:
        if set(values).intersection(set(extend_dict[key])):
            log.warning("Adding repeated values to list at key %s", key)
        extend_dict[key].extend(values)
    else:
        if set(values).intersection(set(extend_dict[key][type_resources])):
            log.warning("Adding repeated values to list at key %s", key)
        extend_dict[key][type_resources].extend(values)
