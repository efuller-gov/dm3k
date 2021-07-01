"""
This ingests the legacy json format of constraints for full house problems.
"""
import datetime
import json
import logging
import os
from typing import Any, AnyStr, Dict, List, Union

from dm3k import LOG_DIR
from dm3k.slim_optimizer.full_house.full_house_input import FullHouseInput

log = logging.getLogger(__name__)

VALIDATE_ERROR_CODE = {
    0: "fatal constraint format error",  # fatal
    1: "fixable constraint format error",  # add in the necessary format with blank content
    2: "DU in values but not in costs",  # remove the du in values
    3: "DU in resourceSetDuMap not in values",  # remove the du in resourceSetDuMap
    4: "DU in resourceSetDuMap not in costs",  # remove the du in resourceSetDuMap
    5: "resourceGroup not in groupResourceMap and groupCapItemMap",  # remove the resourceGroup
    6: "resource in resourceSetDuMap not in groupResourceMap",  # remove the resource
    7: "DU in costs but not resourceSetDuMap",  # remove the du in costs
    8: "DU in costs but not in values",  # remove the du in costs
}


class FullHouseInputJson(FullHouseInput):
    """
    The json input format (formerly called common2) is a single file called 'constraints.json' that looks like...

    .. note:
        {
            "resourceGroups": ["Ship0", "Ship1"],
            "groupCapItemMap": {
                "Ship0": [{"type": "missile0", "capacity": 4}],
                "Ship1": [{"type": "missile0", "capacity": 3}]},
            "groupResourceMap": {
                "Ship0": ["launcher0"],
                "Ship1": ["launcher1"]},
            "costs": {
                "VIP0": [{"type": "missile0", "cost": 1}],
                "VIP1": [{"type": "missile0", "cost": 1}],
                ...

                "VIP16": [{"type": "missile0", "cost": 1}]},
            "resourceSetDuMap": {
                "launcher0": {
                    "launcher0target0": ["VIP5",... "VIP11"],
                    "launcher0target1": ["VIP0", ... "VIP11"]},
                "launcher1": {
                    "launcher1target0": ["VIP5", ...  "VIP11"],
                    "launcher1target1": ["VIP0", ...  "VIP11"]}},
            "bundles": {},
            "bundleScores": {},
            "forbidList": [],
            "forceList": []
        }

    """

    def __init__(self):
        super().__init__()
        self._needs_rebuild = True

    def ingest_validate(self, constraints_path, activity_scores_names=None):
        """
        Validate the constraints and activity scores to determine if following Errors are found

        .. note:
            ERROR_CODE      DESCRIPTION
                1           the necessary constraints files do not exist
                2           the formats of the constraints files are incorrect
                3           the data within the constraints files are not consistent with each other
                4           the data within the constraints files and the activity names are not consistent

            And then Load the files in the constraints path into this input (capturing them in the self._data attribute)

            :param str constraints_path: string path to the folder which contains the constraints files
            :param list activity_scores_names:
            :return bool fatal: True=a fatal error has been found, the optimizer should not continue
            :return list validation_errors: a list of errors where each error is a dict with the following attributes...
                        "err_code" : <a int where int is key in ERROR_CODE above>,
                        "err_txt" : <human readable text that describes the error>,
                        "offender" : <string or list of name(s) (of DU, resource, or resource group) that is causing error>,
                        "fix": <string or list of name(s) of process performed to fix the error  or None>,
                        "is_fatal_error": <boolean; True = error is fatal, False = error is fixable>
        """
        # --- VALIDATE ---
        # determine if correct files exist
        filepath = constraints_path + "/constraints.json"
        if os.path.exists(filepath):
            with open(filepath) as openfile:
                constraints_text = openfile.read()
        else:
            return (
                True,
                [
                    {
                        "err_code": 1,
                        "err_txt": "constraints.json file could not be found in {}".format(constraints_path),
                        "offender": "**YOU**",
                        "fix": "Cant fix this!",
                        "is_fatal_error": True,
                    }
                ],
            )

        # get constraints as a dict
        constraints = json.loads(constraints_text)

        # --- INGEST ---
        self._data = {
            "parent_resources": [],
            "child_resources": [],
            "parent_activities": [],
            "child_activities": [],
            "avail_parent_amt": {},
            "avail_child_amt": {},
            "req_parent_amt": {},
            "req_child_amt": {},
            "child_score": {},
            "force_list": [],
            "forbid_list": [],
            "parent_possible_allocations": {},
            "child_possible_allocations": {},
            "resource_families": {},
            "activity_children": {},
        }  # type: Dict[AnyStr, Union[List, Dict[Any, Union[float, Dict, List]]]]

        if activity_scores_names is not None:
            self._data["child_score"] = dict.fromkeys(activity_scores_names, 0)

        scores_path = constraints_path + "/scores.json"
        if os.path.exists(scores_path):
            with open(scores_path) as f:
                scores_dict = json.load(f)
                self._data["child_score"] = {}
                for ca_name, amount in scores_dict.items():
                    log.debug("%s has a value of %s", ca_name, amount)
                    self._data["child_activities"].append(ca_name)
                    self._data["child_score"][ca_name] = amount
        else:
            log.info("There is no scores.json file in this dataset.  The scorer must be run in order to get values")

        # handle resourceGroups
        group_list = []
        for group in constraints["resourceGroups"]:
            self._data["resource_families"][group] = {"parent_resources": [], "child_resources": []}
            group_list.append(group)

        # handle groupCapItemMap
        for group in constraints["groupCapItemMap"]:
            for ci in constraints["groupCapItemMap"][group]:
                child_res = group + ci["type"]
                self._data["child_resources"].append(child_res)
                self._data["avail_child_amt"][child_res] = ci["capacity"]
                self._data["child_possible_allocations"][child_res] = []

        # handle groupResourceMap
        for group in constraints["groupResourceMap"]:
            parent_res_list = constraints["groupResourceMap"][group]
            self._data["resource_families"][group]["parent_resources"].extend(parent_res_list)
            self._data["parent_resources"].extend(parent_res_list)

            # has to assume in common2 that avail_parent_amt is always 1
            self._data["avail_parent_amt"].update(dict.fromkeys(parent_res_list, 1))

        # handle costs
        self._data["child_activities"].extend(constraints["costs"].keys())
        self._data["child_activities"] = sorted(set(self._data["child_activities"]))
        for child_act in constraints["costs"]:
            for group in group_list:
                for ci in constraints["costs"][child_act]:
                    child_res = group + ci["type"]
                    tuple_arc = (child_res, child_act)
                    self._data["req_child_amt"][tuple_arc] = ci["cost"]
                    if child_res not in self._data["resource_families"][group]["child_resources"]:
                        self._data["resource_families"][group]["child_resources"].append(child_res)
                    if child_res not in self._data["child_possible_allocations"]:
                        raise ValueError("{} is not a valid child resource".format(child_res))
                    self._data["child_possible_allocations"][child_res].append(child_act)

        # handle resource SetDuMap
        for parent_res in constraints["resourceSetDuMap"]:
            self._data["parent_possible_allocations"][parent_res] = []
            for parent_act in constraints["resourceSetDuMap"][parent_res]:
                self._data["parent_activities"].append(parent_act)
                self._data["parent_possible_allocations"][parent_res].append(parent_act)
                self._data["activity_children"][parent_act] = constraints["resourceSetDuMap"][parent_res][parent_act]

                # has to assume in common2 that req_parent_amt is always 1
                tuple_arc = (parent_res, parent_act)
                self._data["req_parent_amt"][tuple_arc] = 1

        # handle force/forbid
        self._data["force_list"] = constraints["forceList"]
        self._data["forbid_list"] = constraints["forbidList"]

        # validate
        validation_errors = self._validate(constraints, self._data["child_score"])

        # fix
        fatal = self._fix(constraints, self._data["child_score"], validation_errors)

        if fatal:
            return fatal, validation_errors

        return False, validation_errors

    def add_scores(self, activity_scores):
        """
        Update this input (i.e. the self._data attribute) with the activity scores

        NOTE - this function assumes that both 'validate' and 'ingest' have been already run

        :param dict activity_scores: a dictionary of activity names as keys and activity scores as values
        :return: None (this function modifies the self._data attribute)
        """
        self._data["child_score"] = activity_scores

    def _validate(self, constraints, values):
        """
        Determines if the constraints and values are valid set

        ERROR_CODE      DESCRIPTION
                1           the necessary constraints files do not exist
                2           the formats of the constraints files are incorrect
                3           the data within the constraints files are not consistent with each other
                4           the data within the constraints files and the activity names are not consistent

        :param dict constraints: a dict of domain specific constraints (with format defined within this translator function)
        :param dict values: a dict of domain specific values (with format defined within this translator function)
        :return list validation_errors: a list of errors where each error is a dict with the following attributes...
                        "err_code" : <a int where int is key in VALIDATE_ERROR_CODE>,
                        "err_txt" : <human readable text that describes the error>,
                        "offender" : <string or list of name(s) (of DU, resource, or resource group) that is causing error>,
                        "fix" : <string of fix applied, initially is none>
                        "is_fatal_error": <boolean; True = error is fatal, False = error is fixable>

        """
        validation_errors = []

        # are all the items in constraints
        needed_constraint_keys = [
            "resourceGroups",
            "resourceSetDuMap",
            "groupResourceMap",
            "groupCapItemMap",
            "costs",
            "bundles",
            "bundleScores",
            "forbidList",
            "forceList",
        ]
        fatal_constraint_keys = ["resourceGroups", "resourceSetDuMap", "groupResourceMap", "groupCapItemMap", "costs"]

        for key in needed_constraint_keys:
            if key not in constraints:
                if key in fatal_constraint_keys:
                    err = {
                        "err_code": 2,
                        "sub_code": 0,
                        "err_txt": (key + " not in constraints"),
                        "offender": None,
                        "fix": None,
                        "is_fatal_error": True,
                    }
                else:
                    err = {
                        "err_code": 2,
                        "sub_code": 1,
                        "err_txt": (key + " not in constraints"),
                        "offender": None,
                        "fix": None,
                        "is_fatal_error": False,
                    }
                log.warning("%s not in constraint file attributes...this may cause future errors", key)
                validation_errors.append(err)

        dus_in_costs = constraints["costs"].keys()

        # every du in values should be in constraint cost
        if values and "costs" in constraints:
            dus_in_values_not_costs = list(set(values.keys()) - set(dus_in_costs))
            if len(dus_in_values_not_costs) > 100:
                err_txt = "{} different DUs in values but are not in costs".format(len(dus_in_values_not_costs))
            else:
                err_txt = "{} in values but are not in costs".format(dus_in_values_not_costs)

            if dus_in_values_not_costs:
                err = {
                    "err_code": 4,
                    "sub_code": 2,
                    "err_txt": (err_txt),
                    "offender": dus_in_values_not_costs,
                    "fix": None,
                    "is_fatal_error": False,
                }
                validation_errors.append(err)

        # Find all dus listed in resourceSetDuMap
        # Much faster to do uniqueness by using the set method
        dus_in_resource_map = []
        if "resourceSetDuMap" in constraints:
            for r in constraints["resourceSetDuMap"]:
                for dus in constraints["resourceSetDuMap"][r].values():
                    dus_in_resource_map.extend(dus)

        # Make list unique
        dus_in_resource_map = list(set(dus_in_resource_map))

        # every du in resourceSetDuMap should be in values
        dus_in_resources_not_values = list(set(dus_in_resource_map) - set(values.keys()))
        if len(dus_in_resources_not_values) > 100:
            err_txt = "{} different DUs in resourceSetDuMap but are not in values".format(len(dus_in_resources_not_values))
        else:
            err_txt = "{} in resourceSetDuMap but are not in values".format(dus_in_resources_not_values)

        if dus_in_resources_not_values:
            err = {
                "err_code": 4,
                "sub_code": 3,
                "err_txt": (err_txt),
                "offender": dus_in_resources_not_values,
                "fix": None,
                "is_fatal_error": False,
            }
            validation_errors.append(err)

        # every du in resourceSetDuMap should be in costs
        dus_in_resources_not_costs = list(set(dus_in_resource_map) - set(dus_in_costs))
        if dus_in_resources_not_costs:
            err = {
                "err_code": 3,
                "sub_code": 4,
                "err_txt": ("{} in resourceSetDuMap but not in costs".format(dus_in_resources_not_costs)),
                "offender": dus_in_resources_not_costs,
                "fix": None,
                "is_fatal_error": False,
            }
            validation_errors.append(err)

        # every resourceGroup should be in groupResourceMap and groupCapItemMap
        if "resourceGroups" in constraints:
            resource_groups = constraints["resourceGroups"]
            if "groupResourceMap" in constraints:
                groups_not_in_resource_map = list(set(resource_groups) - set(constraints["groupResourceMap"].keys()))
                if groups_not_in_resource_map:
                    err = {
                        "err_code": 3,
                        "sub_code": 5,
                        "err_txt": (groups_not_in_resource_map + " is not in groupResourceMap"),
                        "offender": groups_not_in_resource_map,
                        "fix": None,
                        "is_fatal_error": False,
                    }
                    validation_errors.append(err)

            if "groupCapItemMap" in constraints:
                groups_no_in_cap_map = list(set(resource_groups) - set(constraints["groupCapItemMap"].keys()))
                if groups_no_in_cap_map:
                    err = {
                        "err_code": 3,
                        "sub_code": 5,
                        "err_txt": (groups_no_in_cap_map + " is not in groupCapItemMap"),
                        "offender": groups_no_in_cap_map,
                        "fix": None,
                        "is_fatal_error": False,
                    }
                    validation_errors.append(err)

        # every resource in resourceSetDuMap should be in groupResourceMap
        resources_in_groups = []
        if "groupResourceMap" in constraints and "resourceSetDuMap" in constraints:
            for resources in constraints["groupResourceMap"].values():
                resources_in_groups.extend(resources)
        resources_not_in_du_map = list(set(resources_in_groups) - set(constraints["resourceSetDuMap"].keys()))
        if resources_not_in_du_map:
            err = {
                "err_code": 3,
                "sub_code": 6,
                "err_txt": (resources_not_in_du_map + " in groupResourceMap is not in resourceSetDuMap"),
                "offender": resources_not_in_du_map,
                "fix": None,
                "is_fatal_error": False,
            }
            validation_errors.append(err)

        # every du in costs should be in values
        if "costs" in constraints:
            dus_in_costs_not_values = list(set(dus_in_costs) - set(values.keys()))
            if dus_in_costs_not_values:
                if len(dus_in_costs_not_values) > 100:
                    err_txt = "{} different DUs in costs but are not in values".format(len(dus_in_costs_not_values))
                else:
                    err_txt = "{} in costs but are not in values".format(dus_in_costs_not_values)

                err = {
                    "err_code": 4,
                    "sub_code": 7,
                    "err_txt": (err_txt),
                    "offender": dus_in_costs_not_values,
                    "fix": None,
                    "is_fatal_error": False,
                }
                validation_errors.append(err)

        # every du in costs should be in resourceSetDuMap
        dus_in_costs_not_resources = list(set(dus_in_costs) - set(dus_in_resource_map))
        if dus_in_costs_not_resources:
            err = {
                "err_code": 3,
                "sub_code": 8,
                "err_txt": ("{} in costs but is not in resourceSetDuMap".format(dus_in_costs_not_resources)),
                "offender": dus_in_costs_not_resources,
                "fix": None,
                "is_fatal_error": False,
            }
            validation_errors.append(err)

        return validation_errors

    def _fix(self, constraints, values, validation_errors):
        """
        Attempts to fix errors with the initially created input dictionary.  Returns errors if it is unable to.

        :param dict constraints: a dict of domain specific constraints (with format defined within this translator function)
        :param dict values: a dict of domain specific values (with format defined within this translator function)
        :param list validation_errors: a list of errors where each error is a dict with the following attributes...
                        "sub_code" : <a int where int is key in VALIDATE_ERROR_CODE>,
                        "err_txt" : <human readable text that describes the error
                        "offender" : <string or list of name(s) (of DU, resource, or resource group) that is causing error>,

        :return bool fatal: True=a fatal error has been found, the optimizer should not continue

            NOTE - constraints, values, and validation_errors will also be modified

        """
        # if no errors, get out
        if len(validation_errors) == 0:
            log.debug("No Errors found to fix")
            return False

        log.info("Attempting to fix errors....")
        for err in validation_errors:
            code = err["sub_code"]
            reason = err["err_txt"]
            keys = err["offender"]
            # offender could be a string or list.  Convert to list if string
            if not isinstance(keys, list):
                keys = [keys]

            fatal = err["is_fatal_error"]

            # if error is fatal, raise exception
            if fatal:
                log.error(reason)
                err["fix"] = "Fatal Error - Cant fix!"
                return True

            log.info(reason)
            for key in keys:
                # non-fatal format error
                if code == 1:
                    log.debug(VALIDATE_ERROR_CODE[code])
                    added_in_list = []
                    if "bundles" not in constraints:
                        constraints["bundles"] = {}
                        added_in_list.append("bundles")
                        log.info("  ADDED Empty Bundles into Constraints")

                    if "bundleScores" not in constraints:
                        constraints["bundleScores"] = {}
                        added_in_list.append("bundleScores")
                        log.info("  ADDED Empty BundleScores into Constraints")

                    if "forceList" not in constraints:
                        constraints["forceList"] = []
                        added_in_list.append("forceList")
                        log.info("  ADDED Empty forceList into Constraints")

                    if "forbidList" not in constraints:
                        constraints["forbidList"] = []
                        added_in_list.append("forbidList")
                        log.info("  ADDED Empty forbidList into Constraints")

                    added_in = ",".join(added_in_list)
                    err["fix"] = "ADDED: {} to constraints".format(added_in)

                # DU in resourceSetDuMap not in values, remove the du from constraints
                #   OR
                # DU in resourceSetDuMap not in costs, remove the du from resourceSetDuMap
                #   OR
                # DU in values but not in costs, remove the du from values
                elif code in (2, 3, 4, 7, 8):
                    log.debug(VALIDATE_ERROR_CODE[code])
                    if key in values:
                        del values[key]
                        err["fix"] = "REMOVED DU: {} from Values".format(key)
                        log.debug("   REMOVED DU: %s from Values", key)

                    costs = constraints["costs"]
                    if key in costs:
                        del costs[key]
                        err["fix"] = "REMOVED DU: {} from Constraints[costs]".format(key)
                        log.debug("   REMOVED DU: %s from Constraints[costs]", key)

                    force = constraints["forceList"]
                    if key in force:
                        force.remove(key)
                        err["fix"] = "REMOVED DU: {} from Constraints[forceList]".format(key)
                        log.debug("   REMOVED DU: %s from Constraints[forceList]", key)

                    forbid = constraints["forbidList"]
                    if key in forbid:
                        forbid.remove(key)
                        err["fix"] = "REMOVED DU: {} from Constraints[forbidList]".format(key)
                        log.debug("   REMOVED DU: %s from Constraints[forbidList]", key)

                    bundles = constraints["bundles"]
                    bundle_scores = constraints["bundleScores"]
                    for name in bundles:
                        if key in bundles[name]:
                            del bundles[name]
                            log.warning("   REMOVED Bundle: %s from Constraints[bundles] because it contained DU: %s", name, key)
                            if name in bundle_scores:
                                del bundle_scores[name]
                                err["fix"] = "REMOVED Bundle: {0} from bundles and bundle_scores because it contained DU: {1}".format(
                                    name, key
                                )
                                log.warning("  REMOVED Bundle: %s from Constraints[bundle_scores] because it contained DU: %s", name, key)
                            else:
                                err["fix"] = "REMOVED Bundle: {0} from Constraints[bundles] because it contained DU: {1}".format(name, key)

                    res_set_du_map = constraints["resourceSetDuMap"]
                    for r in res_set_du_map:
                        for s in res_set_du_map[r]:
                            if key in res_set_du_map[r][s]:
                                res_set_du_map[r][s].remove(key)
                                err["fix"] = "REMOVED DU: {0} from Constraints[resourceSetDuMap][{1}][{2}]".format(key, r, s)
                                log.debug("   REMOVED DU: %s from Constraints[resourceSetDuMap][%s][%s]", key, r, s)

                # resourceGroup not in groupResourceMap and groupCapItemMap, remove the resourceGroup
                elif code == 5:
                    log.debug(VALIDATE_ERROR_CODE[code])
                    if key in constraints["groupResourceMap"]:

                        # need to eliminate any resources only associated with that group
                        not_needed_resources = constraints["groupResourceMap"][key]

                        # go through other resource groups to ensure not shared resources
                        for rg in constraints["groupResourceMap"]:
                            if rg != key:
                                for r in constraints["groupResourceMap"][rg]:
                                    if r in not_needed_resources:
                                        not_needed_resources.remove(r)

                        # get rid of not need resources
                        if len(not_needed_resources) > 0:
                            log.warning("   FOUND related resources for resource group that need to be also removed!!!")
                        for n in not_needed_resources:
                            if n in constraints["resourceSetDuMap"]:
                                del constraints["resourceSetDuMap"][n]
                                err["fix"] = "REMOVED Resource: {} from Constraints[resourceSetDuMap]".format(n)
                                log.warning("      REMOVED Resource: %s from Constraints[resourceSetDuMap]", n)

                        del constraints["groupResourceMap"][key]
                        err["fix"] = "REMOVED RG: {} from Constraints[groupResourceMap]".format(key)
                        log.warning("   REMOVED RG: %s from Constraints[groupResourceMap]", key)

                    if key in constraints["groupCapItemMap"]:
                        del constraints["groupCapItemMap"][key]
                        err["fix"] = "REMOVED RG: {} from Constraints[groupCapItemMap]".format(key)
                        log.warning("   REMOVED RG: %s from Constraints[groupCapItemMap]", key)

                    if key in constraints["resourceGroups"]:
                        constraints["resourceGroups"].remove(key)
                        err["fix"] = "REMOVED RG: {} from Constraints[resourceGroups]".format(key)
                        log.warning("   REMOVED RG: %s from Constraints[resourceGroups]", key)

                # resource in resourceSetDuMap not in groupResourceMap, remove the resource
                elif code == 6:
                    log.debug(VALIDATE_ERROR_CODE[code])
                    if key in constraints["resourceSetDuMap"]:
                        del constraints["resourceSetDuMap"][key]
                        err["fix"] = "REMOVED Resource: {} from Constraints[resourceSetDuMap]".format(key)
                        log.warning("   REMOVED Resource: %s from Constraints[resourceSetDuMap]", key)

                    for group in constraints["groupResourceMap"]:
                        if key in constraints["groupResourceMap"][group]:
                            constraints["groupResourceMap"][group].remove(key)
                            err["fix"] = "REMOVED Resource: {} from Constraints[groupResourceMap]".format(key)
                            log.warning("   REMOVED Resource: %s from Constraints[groupResourceMap][%s]", key, group)

                else:
                    # should Not happen
                    raise KeyError("Error Code {} is not recognized".format(code))

        log.warning("...NEW Constraint File...")
        if len(constraints["costs"].keys()) > 100:
            date_str = datetime.datetime.now().isoformat()
            constraints_log_name = os.path.join(LOG_DIR, "constraints_new_" + date_str)
            with open(constraints_log_name, "w") as f:
                json.dump(constraints, f, indent=4)
        else:
            log.info(json.dumps(constraints, indent=4))

        return False
