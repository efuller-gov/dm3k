"""
This ingests spreadsheet constraints for full house problems.

input_base needs to hold the modifications (adjusting constraints after they have been loaded).

"""

import difflib
import glob
import json
import logging
import os
from collections import defaultdict
from pprint import pformat
from typing import Any, AnyStr, Dict, List, Union

import optimizer.util.util
import pandas as pd
from optimizer.slim_optimizer_base import InputBase
from optimizer.util.util import fh_append, fh_extend, full_house_input_keys

log = logging.getLogger(__name__)


class FullHouseInput(InputBase):
    def __init__(self):
        super().__init__()
        self._fatal_error = False
        self._removed_data_queue = {}
        self._validation_errors = []
        self._max_items_display = 5

    def ingest_validate(self, constraints_path, activity_scores_names=None):
        """
        Ingest and validate constraints.

        :param str constraints_path: Full path to the dataset
        :param list activity_scores_names: list of DUs/child_activities
        :return bool: self._fatal_error True when the validation error found is fatal
        :return list: self._validation_errors list of all validation errors
        """

        self._fatal_error = False
        self._validation_errors = []
        # fh_dict is the placeholder to build the input dictionary and will be set to self._data once complete
        # child_score is also a key, but this can be set after the constraints have been processed
        fh_dict = {
            "resource_families": {},
            "req_child_amt": {},
            "req_parent_amt": {},
            "avail_child_amt": {},
            "avail_parent_amt": {},
            "child_resources": [],
            "parent_resources": [],
            "force_list": [],
            "forbid_list": [],
            "child_activities": [],
            "parent_activities": [],
            "child_possible_allocations": {},
            "parent_possible_allocations": {},
            "activity_children": {},
        }  # type: Dict[AnyStr, Union[List, Dict[Any, Union[float, Dict, List]]]]

        expected_csv_basenames = [
            "activity.csv",
            "child_allocations.csv",
            "child_budget.csv",
            "child_cost.csv",
            "container_child_resource.csv",
            "container_parent_resource.csv",
            "parent_allocations.csv",
            "parent_budget.csv",
            "parent_cost.csv",
        ]

        constraints_dir = constraints_path + "/constraints"
        if not os.path.exists(constraints_dir):
            self._add_to_validation_errors("Path to {} does not exist".format(constraints_dir), err_code=1)
            return True, self._validation_errors

        csv_files = glob.glob(constraints_dir + "/*.csv")
        csv_basenames = [os.path.basename(x) for x in csv_files]

        # force_forbid.csv is an optional file
        if "force_forbid.csv" in csv_basenames:
            csv_basenames.remove("force_forbid.csv")

        if set(csv_basenames) != set(expected_csv_basenames):
            missing_files = ", ".join(set(expected_csv_basenames) - set(csv_basenames))
            if missing_files:
                self._add_to_validation_errors("Following files are missing in {}: {}".format(constraints_path, missing_files), err_code=1)
            additional_files = ", ".join(set(csv_basenames) - set(expected_csv_basenames))
            if additional_files:
                self._add_to_validation_errors("Following files have unexpected names: {}".format(additional_files), err_code=1)

        if activity_scores_names is not None:
            fh_dict["child_activities"] = activity_scores_names
            fh_dict["child_score"] = dict.fromkeys(fh_dict["child_activities"], 0)

        # The order that the csv files are processed does matter
        # Doing a simple sort and going through them alphabetically works
        csv_files.sort()

        scores_path = constraints_path + "/scores.json"
        if os.path.exists(scores_path):
            with open(scores_path) as f:
                try:
                    scores_dict = json.load(f)
                except json.decoder.JSONDecodeError as e:
                    raise ValueError("Error processing {} file\n\t{}".format(scores_path, str(e))) from e

                fh_dict["child_score"] = {}
                new_child_activities = list(set(scores_dict.keys()) - set(fh_dict["child_activities"]))
                fh_dict["child_activities"].extend(new_child_activities)
                for ca_name, amount in scores_dict.items():
                    log.debug("%s has a score of %s", ca_name, amount)
                    fh_dict["child_score"][ca_name] = amount
        else:
            log.info("There is no scores.json file in this dataset.  The scorer must be run in order to get values")

        resource_type_lookup = defaultdict(list)  # this dict will be used to find resources that can satisfy a cost type
        for csv_file in csv_files:
            file_dict = {}
            # These files must have column names in the first row of the file
            header_required = ["child_budget", "parent_budget", "child_cost", "parent_cost", "force_forbid"]
            basename = os.path.basename(csv_file).split(".csv")[0]
            log.info("Working on... %s", basename)
            try:
                # A hack to figure out which row has the most columns
                max_comma_count = 0
                with open(csv_file) as f:
                    for line in f:
                        count = line.count(",")
                        if count > max_comma_count:
                            max_comma_count = count
                col_names = list(range(max_comma_count + 1))
                if basename in header_required:
                    csv_df = pd.read_csv(csv_file, index_col=0, skipinitialspace=True)
                else:
                    csv_df = pd.read_csv(
                        csv_file, header=None, index_col=0, names=col_names, skipinitialspace=True, skiprows=1, engine="python"
                    )
            except pd.errors.ParserError as e:
                # Changing this to an immediate error to limit further errors due to this file not being processed correctly

                raise TypeError(
                    "{}.csv is in an invalid format and pandas could not create a proper dataframe.  {}".format(basename, e)
                ) from e

            if basename == "activity":
                for pa_name, ca_names in zip(csv_df.index.values.tolist(), csv_df.values.tolist()):
                    # Remove null values and duplicates
                    ca_names = list({str(ca_name) for ca_name in ca_names if ca_name is not None and str(ca_name) != "nan"})
                    if pa_name not in fh_dict["parent_activities"]:
                        fh_dict["parent_activities"].append(pa_name)
                    log.debug("Parent activity %s has the following child activities %s", pa_name, ca_names)
                    fh_extend(file_dict, pa_name, ca_names)
                fh_dict["activity_children"] = file_dict
            elif basename in ("child_allocations", "parent_allocations"):
                if basename == "child_allocations":
                    req_amt, resources, possible_allocations = "req_child_amt", "child_resources", "child_possible_allocations"
                else:  # parent_allocations
                    req_amt, resources, possible_allocations = "req_parent_amt", "parent_resources", "parent_possible_allocations"

                for resource_name, activity_names in zip(csv_df.index.values.tolist(), csv_df.values.tolist()):
                    # Remove null values and duplicates
                    activity_names = list({str(a_name) for a_name in activity_names if a_name is not None and str(a_name) != "nan"})
                    # Initialize cost dictionary to 0, validate method will check to make sure it does not stay at 0
                    for activity_name in activity_names:
                        fh_dict[req_amt][(resource_name, activity_name)] = 0.0
                    if resource_name not in fh_dict[resources]:
                        fh_dict[resources].append(resource_name)
                    log.debug("Resource %s has the following activities: %s", resource_name, activity_names)
                    fh_extend(file_dict, resource_name, activity_names)
                fh_dict[possible_allocations] = file_dict
            elif basename in ("child_budget", "parent_budget"):
                if basename == "child_budget":
                    allocations_file, avail_amt, resources = "child_allocations.csv", "avail_child_amt", "child_resources"
                else:  # parent_budget
                    allocations_file, avail_amt, resources = "parent_allocations.csv", "avail_parent_amt", "parent_resources"

                # Initialize budget dictionary to 0, validate method will check to make sure it does not stay at 0
                fh_dict[avail_amt] = dict.fromkeys(fh_dict[resources], 0)
                try:
                    budget_dict = csv_df.to_dict("index")
                except pd.errors.ParserError as e:
                    raise ValueError("Error processing {}.csv file\n{}".format(basename, str(e))) from e

                default_type = ""
                default_budget = 0
                error_found = False
                budgets_not_numeric = []
                for resource_name, row in budget_dict.items():
                    budget = None
                    if resource_name != "_default_" and resource_name not in fh_dict[resources]:
                        self._add_to_validation_errors("Resource {} not listed in {}".format(resource_name, allocations_file), err_code=3)

                    for resource_type, value in row.items():
                        # There only can one budget/value given per row/resource
                        if str(value) != "nan":
                            # It will be an error if two budgets are listed in the same row
                            if budget is None:
                                budget = value
                                if not isinstance(budget, (int, float)):
                                    budgets_not_numeric.append(resource_name)
                                    error_found = True
                                if resource_name == "_default_":
                                    # Save the default budget/type, and read in rest of file before applying
                                    default_budget = budget
                                    default_type = resource_type
                                else:
                                    if resource_name not in fh_dict[avail_amt]:
                                        self._add_to_validation_errors(
                                            "Resource {} not found in {}".format(resource_name, allocations_file), err_code=2
                                        )
                                        error_found = True
                                    elif fh_dict[avail_amt][resource_name] == 0:
                                        log.debug("%s has a budget of %s", resource_name, budget)
                                        resource_type_lookup[resource_type].append(resource_name)
                                        fh_dict[avail_amt][resource_name] = budget
                                    else:
                                        self._add_to_validation_errors(
                                            "A budget was already given for resource {}".format(resource_name), err_code=2
                                        )
                            else:
                                self._add_to_validation_errors("Two budgets given for resource {}".format(resource_name), err_code=2)

                    # Even if only one line has a non-numeric value for a budget, it will consider the entire column as string values
                    if error_found:
                        self._add_to_validation_errors(
                            "There are {} {}(s) not of numeric type: {}".format(
                                len(budgets_not_numeric), basename, budgets_not_numeric[: self._max_items_display]
                            ),
                            err_code=2,
                        )
                    if budget is None:
                        self._add_to_validation_errors("Could not find a budget for resource {}".format(resource_name), err_code=2)
                if default_budget != 0:
                    for name, budget in fh_dict[avail_amt].items():
                        if budget == 0:
                            log.debug("Setting %s to default budget of %s", name, budget)
                            fh_dict[avail_amt][name] = default_budget
                            resource_type_lookup[default_type].append(name)
            elif basename in ("child_cost", "parent_cost"):
                if basename == "child_cost":
                    req_amt = "req_child_amt"
                    possible_allocations = "child_possible_allocations"
                    activities = "child_activities"
                    file_list_all_activities = "scores.json"
                else:  # parent_cost
                    req_amt = "req_parent_amt"
                    possible_allocations = "parent_possible_allocations"
                    activities = "parent_activities"
                    file_list_all_activities = "activity.csv"

                try:
                    cost_dict = csv_df.to_dict("index")
                except pd.errors.ParserError as e:
                    raise ValueError("Error processing {}.csv file\n{}".format(basename, str(e))) from e

                default_cost_dict = {}
                error_found = False
                costs_not_numeric = []
                for activity_name, row in cost_dict.items():
                    if activity_name != "_default_" and activity_name not in fh_dict[activities]:
                        self._add_to_validation_errors(
                            "Activity {} listed in {}.csv but not found in {}".format(activity_name, basename, file_list_all_activities),
                            err_code=4,
                        )

                    for resource_type, cost in row.items():
                        if str(cost) != "nan":
                            if not isinstance(cost, (int, float)):
                                costs_not_numeric.append(activity_name)
                                error_found = True
                            if activity_name == "_default_":
                                # Save the default cost/type, and read in rest of file before applying
                                default_cost_dict[resource_type] = cost
                            else:
                                # This assumes that the associated budget file has already been processed
                                if resource_type not in resource_type_lookup:
                                    self._add_to_validation_errors("Resource Types in budget/costs files do not match", err_code=3)
                                # find all resources with budget of right type
                                for resource_name in resource_type_lookup[resource_type]:
                                    # cost/req_amt dict has been initialized with possible allocations
                                    # do not create a new entry
                                    if (resource_name, activity_name) in fh_dict[req_amt]:
                                        # set each required amount to cost for that type
                                        log.debug("%s has a budget of %s", (resource_name, activity_name), cost)
                                        if fh_dict[req_amt][(resource_name, activity_name)] == 0:
                                            fh_dict[req_amt][(resource_name, activity_name)] = cost
                                        else:
                                            self._add_to_validation_errors(
                                                "A cost was already given for resource/activity pair {}/{}".format(
                                                    resource_name, activity_name
                                                ),
                                                err_code=2,
                                            )

                        else:
                            log.debug("Activity %s has no cost for resource type %s", activity_name, resource_type)

                    # Even if only one line has a non-numeric value for a cost, it will consider the entire column as string values
                    if error_found:
                        self._add_to_validation_errors(
                            "There are {} {}(s) not of numeric type: {}".format(
                                len(costs_not_numeric), basename, costs_not_numeric[: self._max_items_display]
                            ),
                            err_code=2,
                        )
                # go back and put in defaults where appropriate
                # note: I reversed loop order for efficiency
                for default_type, default_cost in default_cost_dict.items():
                    if default_type not in resource_type_lookup:
                        self._add_to_validation_errors(
                            "Could not resolve resource type {}.  Make sure cost and budget files are valid".format(default_type),
                            err_code=2,
                        )
                    else:
                        for resource in resource_type_lookup[default_type]:
                            if resource in fh_dict[possible_allocations]:
                                for activity in fh_dict[possible_allocations][resource]:
                                    # should exist because only going over possibles
                                    if fh_dict[req_amt][(resource, activity)] == 0:
                                        log.debug("Setting %s to default cost of %s", (resource, activity), default_cost)
                                        fh_dict[req_amt][(resource, activity)] = default_cost
                            else:
                                self._add_to_validation_errors(
                                    "Resource {} not listed in {} dictionary".format(resource, possible_allocations), err_code=3
                                )
            elif basename in ("container_child_resource", "container_parent_resource"):
                for container_name, resource_names in zip(csv_df.index.values.tolist(), csv_df.values.tolist()):
                    # Remove nan/null values
                    file_dict[container_name] = list(
                        {str(r_name) for r_name in resource_names if r_name is not None and str(r_name) != "nan"}
                    )
                    if basename == "container_child_resource":
                        log.debug("Container %s has the following child resources %s", container_name, file_dict[container_name])
                        fh_extend(
                            fh_dict["resource_families"], container_name, file_dict[container_name], type_resources="child_resources",
                        )
                    else:  # container_parent_resource
                        log.debug("Container %s has the following parent resources %s", container_name, file_dict[container_name])
                        fh_extend(
                            fh_dict["resource_families"], container_name, file_dict[container_name], type_resources="parent_resources",
                        )
            elif basename == "force_forbid":
                try:
                    force_forbid_dict = csv_df.to_dict("index")
                except pd.errors.ParserError as e:
                    raise ValueError("Error processing {}.csv file\n{}".format(basename, str(e))) from e

                for ca_name, row in force_forbid_dict.items():
                    acceptable_keys = ["level", "force", "forbid"]
                    if set(row.keys()) != set(acceptable_keys):
                        self._add_to_validation_errors(
                            "Unexpected column name found in force_forbid.csv. Acceptable names are: {}".format(acceptable_keys),
                            err_code=2,
                        )
                    action = ""
                    if row["level"] != "child_activity":
                        self._add_to_validation_errors("Only forcing/forbidding of child activities is allowed at this time")
                    else:
                        if row["force"] == 1:
                            action = "force"
                        elif str(row["force"]) != "nan":
                            self._add_to_validation_errors("Unexpected value found in force column of force_forbid.csv")

                        if row["forbid"] == 1:
                            if action == "":
                                action = "forbid"
                            else:
                                self._add_to_validation_errors("Both force and forbid are set in the same row", err_code=2)
                        elif str(row["forbid"]) != "nan":
                            self._add_to_validation_errors("Unexpected value found in forbid column of force_forbid.csv")

                        if action != "":
                            list_name = action + "_list"
                            log.debug("%s added to the %s", ca_name, list_name)
                            if ca_name in fh_dict["child_activities"]:
                                fh_dict[list_name].append(ca_name)
                            else:
                                self._add_to_validation_errors("{} is not a current activity".format(ca_name))

                        else:
                            self._add_to_validation_errors("Neither force or forbid is set for {} in force_forbid.csv".format(ca_name))
            else:
                self._add_to_validation_errors("Unexpected {}.csv file found in {} dataset".format(basename, constraints_path), err_code=1)

        self._data = fh_dict.copy()  # type: Dict[AnyStr, Union[List, Dict[Any, Union[float, Dict, List]]]]

        log.debug("Calling validate method")
        self._validate()
        log.debug("Calling fix method")
        self._fix()
        return self._fatal_error, self._validation_errors

    def _add_to_validation_errors(self, error_message, is_fatal_error=True, err_code=None, offender=None, fix=None):
        self._validation_errors.append(
            {"err_code": err_code, "err_txt": error_message, "offender": offender, "fix": fix, "is_fatal_error": is_fatal_error}
        )
        if is_fatal_error:
            self._fatal_error = True
        log.error(error_message)

    def _validate(self):
        all_pr_names, all_cr_names, all_pa_names, all_pa_ca_names, all_cr_ca_names, all_ca_budget_names = [], [], [], [], [], []

        for resources in self._data["resource_families"].values():
            all_pr_names.extend(resources["parent_resources"])
            all_cr_names.extend(resources["child_resources"])
        for pa_names in self._data["parent_possible_allocations"].values():
            all_pa_names.extend(pa_names)
        for ca_names in self._data["child_possible_allocations"].values():
            all_cr_ca_names.extend(ca_names)
        for ca_names in self._data["activity_children"].values():
            all_pa_ca_names.extend(ca_names)
        for cr_ca in self._data["req_child_amt"].keys():
            all_ca_budget_names.append(cr_ca[1])
        all_ca_budget_names = sorted(set(all_ca_budget_names))

        for child_activity in self._data["child_activities"].copy():
            if child_activity not in all_ca_budget_names:
                self._data["child_activities"].remove(child_activity)
        for child_activity in self._data["child_score"].copy().keys():
            if child_activity not in all_ca_budget_names:
                self._data["child_score"].pop(child_activity)

        missing_keys = []
        for key, value in self._data.items():
            if len(value) == 0:
                if key not in ("force_list", "forbid_list"):
                    missing_keys.append(key)
        if missing_keys:
            self._add_to_validation_errors("{} are not set in _data dictionary".format(missing_keys), err_code=2)

        pa_diff = {x[1] for x in self._data["req_parent_amt"]}.difference(set(self._data["parent_activities"]))
        if pa_diff:
            self._add_to_validation_errors(
                "There are {} parent activit(ies) listed in parent_allocations.csv and not in activity.csv: {}".format(
                    len(pa_diff), list(pa_diff)[: self._max_items_display]
                ),
                err_code=4,
            )

        pa_diff = set(self._data["parent_activities"]).difference({x[1] for x in self._data["req_parent_amt"]})
        if pa_diff:
            self._add_to_validation_errors(
                "There are {} parent activit(ies) listed in activity.csv and not in parent_allocations.csv: {}".format(
                    len(pa_diff), list(pa_diff)[: self._max_items_display]
                ),
                err_code=4,
            )

        pr_diff = set(all_pr_names).difference(set(self._data["parent_resources"]))
        if pr_diff:
            self._add_to_validation_errors(
                "There are {} parent resource(s) listed in container_parent_resource.csv and not in parent_allocations.csv: {}".format(
                    len(pr_diff), list(pr_diff)[: self._max_items_display]
                ),
                err_code=3,
            )

        pr_diff = set(self._data["parent_resources"]).difference(set(all_pr_names))
        if pr_diff:
            self._add_to_validation_errors(
                "There are {} parent resource(s) listed in parent_allocations.csv and not in container_parent_resource.csv: {}".format(
                    len(pr_diff), list(pr_diff)[: self._max_items_display]
                ),
                err_code=3,
            )

        cr_diff = set(all_cr_names).difference(set(self._data["child_resources"]))
        if cr_diff:
            self._add_to_validation_errors(
                "There are {} child resource(s) listed in container_child_resource.csv and not in child_allocations.csv: {}".format(
                    len(cr_diff), list(cr_diff)[: self._max_items_display]
                ),
                err_code=3,
            )

        cr_diff = set(self._data["child_resources"]).difference(set(all_cr_names))
        if cr_diff:
            self._add_to_validation_errors(
                "There are {} child resource(s) listed in child_allocations.csv and not in container_child_resource.csv: {}".format(
                    len(cr_diff), list(cr_diff)[: self._max_items_display]
                ),
                err_code=3,
            )

        pa_diff = set(all_pa_names).difference(set(self._data["parent_activities"]))
        if pa_diff:
            self._add_to_validation_errors(
                "There are {} parent activit(ies) listed in parent_cost.csv and not in parent_allocations.csv: {}".format(
                    len(pa_diff), list(pa_diff)[: self._max_items_display]
                ),
                err_code=4,
            )

        pa_diff = set(self._data["parent_activities"]).difference(set(all_pa_names))
        if pa_diff:
            self._add_to_validation_errors(
                "There are {} parent activit(ies) listed in parent_allocations.csv and not in parent_cost.csv: {}".format(
                    len(pa_diff), list(pa_diff)[: self._max_items_display]
                ),
                err_code=4,
            )

        ca_diff = set(all_pa_ca_names).difference(set(self._data["child_activities"]))
        if ca_diff:
            self._add_to_validation_errors(
                "There are {} child activit(ies) listed in activity.csv and not in the child activities list: {}".format(
                    len(ca_diff), list(ca_diff)[: self._max_items_display]
                ),
                err_code=4,
            )

        ca_diff = set(self._data["child_activities"]).difference(set(all_pa_ca_names))
        if ca_diff:
            self._add_to_validation_errors(
                "There are {} child activit(ies) listed in the child activities list and not in activity.csv: {}".format(
                    len(ca_diff), list(ca_diff)[: self._max_items_display]
                ),
                err_code=4,
            )

        ca_diff = set(all_cr_ca_names).difference(set(self._data["child_activities"]))
        if ca_diff:
            self._add_to_validation_errors(
                "There are {} child activit(ies) listed in child_allocations.csv and not in the child activities list: {}".format(
                    len(ca_diff), list(ca_diff)[: self._max_items_display]
                ),
                err_code=4,
            )

        ca_diff = set(self._data["child_activities"]).difference(set(all_cr_ca_names))
        if ca_diff:
            self._add_to_validation_errors(
                "There are {} child activit(ies) listed in the child activities list and not in child_allocations.csv: {}".format(
                    len(ca_diff), list(ca_diff)[: self._max_items_display]
                ),
                err_code=4,
            )

        pr_pas_no_cost = []
        for pr_pa, cost in self._data["req_parent_amt"].items():
            if cost == 0:
                pr_pas_no_cost.append(pr_pa)
        if pr_pas_no_cost:
            self._add_to_validation_errors(
                "There are {} parent resource/activity pair(s) that have no cost.  Make sure parent_cost.csv is valid: {}".format(
                    len(pr_pas_no_cost), pr_pas_no_cost[: self._max_items_display]
                ),
                err_code=4,
            )

        cr_cas_no_cost = []
        for cr_ca, cost in self._data["req_child_amt"].items():
            if cost == 0:
                cr_cas_no_cost.append(cr_ca)
        if cr_cas_no_cost:
            self._add_to_validation_errors(
                "There are {} child resource/activity pair(s) that have no cost.  Make sure child_cost.csv is valid: {}".format(
                    len(cr_cas_no_cost), cr_cas_no_cost[: self._max_items_display]
                ),
                err_code=4,
            )

        prs_no_budget = []
        for pr, budget in self._data["avail_parent_amt"].items():
            if budget == 0:
                prs_no_budget.append(pr)
        if prs_no_budget:
            self._add_to_validation_errors(
                "There are {} parent resource(s) that have no budget.  Make sure parent_budget.csv is valid: {}".format(
                    len(prs_no_budget), prs_no_budget[: self._max_items_display]
                ),
                err_code=3,
            )

        crs_no_budget = []
        for cr, budget in self._data["avail_child_amt"].items():
            if budget == 0:
                crs_no_budget.append(cr)
        if crs_no_budget:
            self._add_to_validation_errors(
                "There are {} child resource(s) that have no budget.  Make sure child_budget.csv is valid: {}".format(
                    len(crs_no_budget), crs_no_budget[: self._max_items_display]
                ),
                err_code=3,
            )

        for cr, cas in self._data["child_possible_allocations"].copy().items():
            if len(cas) == 0:
                self._add_to_validation_errors(
                    "Child resource {} has no allocations".format(cr), err_code=3, is_fatal_error=False,
                )
                log.info("Removing child resource %s from input", cr)
                self._data["child_possible_allocations"].pop(cr)
                if cr in self._data["child_resources"]:
                    self._data["child_resources"].remove(cr)
                for container in self._data["resource_families"].keys():
                    if cr in self._data["resource_families"][container]["child_resources"]:
                        self._data["resource_families"][container]["child_resources"].remove(cr)
                for cr_ca in self._data["req_child_amt"].keys():
                    if cr == cr_ca[0]:
                        self._data["req_child_amt"].pop(cr_ca)
                if cr in self._data["avail_child_amt"].keys():
                    self._data["avail_child_amt"].pop(cr)

        for pr, pas in self._data["parent_possible_allocations"].copy().items():
            if len(pas) == 0:
                self._add_to_validation_errors(
                    "Parent resource {} has no allocations".format(pr), err_code=3, is_fatal_error=False,
                )
                log.info("Removing parent resource %s from input", pr)
                self._data["parent_possible_allocations"].pop(pr)
                if pr in self._data["parent_resources"]:
                    self._data["parent_resources"].remove(pr)
                for container in self._data["resource_families"].keys():
                    if pr in self._data["resource_families"][container]["parent_resources"]:
                        self._data["resource_families"][container]["parent_resources"].remove(pr)
                for pr_pa in self._data["req_parent_amt"].keys():
                    if pr == pr_pa[0]:
                        self._data["req_parent_amt"].pop(pr_pa)
                if pr in self._data["avail_parent_amt"].keys():
                    self._data["avail_parent_amt"].pop(pr)

    def _fix(self):
        # if no errors, get out
        if len(self._validation_errors) == 0:
            log.debug("No Errors found to fix")
            return

        log.warning("Attempting to fix errors....")
        for err in self._validation_errors:
            reason = err["err_txt"]
            # if error is fatal, raise exception
            if err["is_fatal_error"]:
                err["fix"] = "Fatal Error - Cant fix!"
                raise TypeError(pformat(self._validation_errors, width=120))

            log.warning(reason)

        # Attempt to fix errors here

    def add_scores(self, activity_scores):
        """
        Add activity scores to the _data input dictionary

        :param dict activity_scores: Dictionary of DU scores.  Keys are child_activities
        """
        if activity_scores is None:
            activity_scores = {}

        if "child_score" not in self._data:
            self._data["child_score"] = {}
        log.debug("Updating activity scores")
        if set(activity_scores.keys()) == set(self._data["child_activities"]):
            self._data["child_score"] = activity_scores
        else:
            raise ValueError(
                "Activity names do not match names in dataset:\n{}\n{}\n".format(
                    set(activity_scores.keys()), set(self._data["child_activities"])
                )
            )

    def align_check_scores(self, activity_scores, dus_in_constraints_not_scores_check=False):
        """
        Check to see if activity scores from data_access_layer and optimizer constraints align
        Then Fix them if you can

        :param dict activity_scores: a dictionary of activity names as keys and activity scores as values
        :param bool dus_in_constraints_not_scores_check: Set to True if it should be an error if dus in constraints are
                    not in scores
        :return: None
        """
        errors_with_scores = ""
        child_score_keys = self.to_data()["child_score"].keys()
        if activity_scores is not None:
            if sorted(activity_scores.keys()) == sorted(full_house_input_keys()):
                raise ValueError("This method does not accept input data")
            for k, v in activity_scores.copy().items():
                if not isinstance(v, (int, float)):
                    errors_with_scores += "\nActivity {} has an invalid score entry of {}\n".format(k, v)
                if k not in child_score_keys:
                    activity_scores.pop(k)
            if errors_with_scores != "":
                raise ValueError(errors_with_scores)
            self.add_scores(activity_scores)

        data = self.to_data()
        # Throw an error if the DUs in constraints and scores do not match
        du_mismatch_messages = ""
        in_scores_not_constraints = sorted(set(data["child_score"].keys()) - set(data["child_activities"]))
        if in_scores_not_constraints:
            if len(in_scores_not_constraints) < 5:
                du_mismatch_messages = "\nFollowing DUs found in scores but not found in constraints: {}\n".format(
                    in_scores_not_constraints
                )
                close_list = []
                for name in in_scores_not_constraints:
                    close_matches = difflib.get_close_matches(name, data["child_activities"], n=1, cutoff=0.8)
                    if close_matches:
                        close_list.append(close_matches[0])
                if close_list:
                    du_mismatch_messages += "Did you mean? {}".format(sorted(set(close_list)))
            else:
                len_dus_scores = len(data["child_score"].keys())
                len_dus_constraints = len(data["child_activities"])
                du_mismatch_messages = "There are {} DUs found in scores, but only {} DUs found in constraints".format(
                    len_dus_scores, len_dus_constraints
                )

        if dus_in_constraints_not_scores_check:
            in_constraints_not_scores = sorted(set(data["child_activities"]) - set(data["child_score"].keys()))
            if in_constraints_not_scores:
                if len(in_constraints_not_scores) < 5:
                    du_mismatch_messages += "\nFollowing DUs found in constraints not found in scores: {}\n".format(
                        in_constraints_not_scores
                    )
                    close_list = []
                    for name in in_constraints_not_scores:
                        close_matches = difflib.get_close_matches(name, data["child_score"].keys(), n=1, cutoff=0.8)
                        if close_matches:
                            close_list.append(close_matches[0])
                    if close_list:
                        du_mismatch_messages += "Did you mean? {}".format(close_list)
                else:
                    len_dus_constraints = len(data["child_activities"])
                    len_dus_scores = len(data["child_score"].keys())
                    du_mismatch_messages = "There are {} DUs found in constraints, but only {} DUs found in scores".format(
                        len_dus_constraints, len_dus_scores
                    )

        # This will make sure errors are displayed if there is a mismatch in both directions
        if du_mismatch_messages != "":
            raise ValueError(du_mismatch_messages)

    def modify(self, cmd_dict, timestamp, removed_data=None):
        """
        Apply the cmd to the input data, effectively modifying the input

        :param dict cmd_dict: command
        :param DateTime timestamp: Used to lookup what was executed previous when running an undo command
        :param dict removed_data: Used when modify calls itself
        """

        if removed_data is None:
            removed_data = {}

        cmd_name = cmd_dict["cmd"]
        cmd_args = cmd_dict["args"]
        empty_container_dict = {"parent_resources": [], "child_resources": []}
        recursive_call = True
        if removed_data == {}:
            # modify can call itself.  The initial modify call should not be called with a removed_data parameter
            recursive_call = False
            # Used to keep track of what exactly was removed with each command, to make the undoing of commands easier
            removed_data = {
                "resource_families": {},
                "req_child_amt": {},
                "req_parent_amt": {},
                "avail_child_amt": {},
                "avail_parent_amt": {},
                "child_resources": [],
                "parent_resources": [],
                "force_list": [],
                "forbid_list": [],
                "child_activities": [],
                "parent_activities": [],
                "child_score": {},
                "child_possible_allocations": {},
                "parent_possible_allocations": {},
                "activity_children": {},
            }  # type: Dict[AnyStr, Union[List, Dict[Any, Union[float, Dict, List]]]]

        # set system to rebuild
        self._needs_rebuild = True
        add_removed_data = removed_data.copy()
        # If this command was called via undo, use timestamp to check to see what was removed previously (if anything)
        if timestamp in self._removed_data_queue:
            add_removed_data = self._removed_data_queue.pop(timestamp)

        # 1) force_child_activity - child activity must be selected in the solution (regardless of value)
        #              ARG_1 = "<nameOfChildActivity>"
        #          Ex:  {"cmd": "force_child_activity", "args":["VIP1"]}
        if cmd_name == "force_child_activity":
            ca = cmd_args[0]
            if ca in self._data["child_activities"]:
                if ca not in self._data["force_list"]:
                    log.info("Child activity %s added to the force list", ca)
                    self._data["force_list"].append(ca)
                    if ca in self._data["forbid_list"]:
                        log.info("Child activity %s removed from the forbid list", ca)
                        self._data["forbid_list"].remove(ca)
                else:
                    raise ValueError("Child activity {} was already added to the force child activity list".format(ca))
            else:
                raise ValueError("Child activity {} was not found in current problem".format(ca))

        # 2) forbid_child_activity - child activity must NOT be selected in the solution (regardless of value)
        elif cmd_name == "forbid_child_activity":
            ca = cmd_args[0]
            if ca in self._data["child_activities"]:
                if ca not in self._data["forbid_list"]:
                    log.info("Child activity %s added to the forbid list", ca)
                    self._data["forbid_list"].append(ca)
                    if ca in self._data["force_list"]:
                        log.info("Child activity %s removed from the force list", ca)
                        self._data["force_list"].remove(ca)
                else:
                    raise ValueError("Child activity {} was already added to the forbid child activity list".format(ca))
            else:
                raise ValueError("Child activity {} was not found in current problem".format(ca))

        # 3) clear_child_force
        elif cmd_name == "clear_child_force":
            ca = cmd_args[0]
            if ca in self._data["child_activities"]:
                if ca in self._data["force_list"]:
                    log.info("Child activity %s removed from the force list", ca)
                    self._data["force_list"].remove(ca)
                else:
                    raise ValueError("Child activity {} not found in force list".format(ca))
            else:
                raise ValueError("Child activity {} was not found in current problem".format(ca))

        # 4) clear_child_forbid
        elif cmd_name == "clear_child_forbid":
            ca = cmd_args[0]
            if ca in self._data["child_activities"]:
                if ca in self._data["forbid_list"]:
                    log.info("Child activity %s removed from the forbid list", ca)
                    self._data["forbid_list"].remove(ca)
                else:
                    raise ValueError("Child activity {} not found in forbid list".format(ca))
            else:
                raise ValueError("Child activity {} was not found in current problem".format(ca))

        elif cmd_name == "remove_from_resource_container":
            container, resource = cmd_args
            if container not in self._data["resource_families"]:
                raise ValueError("Resource container {} was not found in current problem".format(container))

            if resource in self._data["resource_families"][container]["parent_resources"]:
                log.info("Parent resource %s removed from container %s", resource, container)
                self._data["resource_families"][container]["parent_resources"].remove(resource)
                removed_data["resource_families"].setdefault(container, {"parent_resources": [], "child_resources": []})
                removed_data["resource_families"][container]["parent_resources"].append(resource)
                modify_cmd = {"cmd": "remove_parent_resource", "args": [resource]}
                self.modify(modify_cmd, timestamp, removed_data=removed_data)
                if not self._data["resource_families"][container]["parent_resources"]:
                    log.warning("Container %s no longer has any parent resources", container)
                    for child_resource in self._data["resource_families"][container]["child_resources"]:
                        log.info("Removing child resource %s from container %s", child_resource, container)
                        self._data["resource_families"][container]["child_resources"].remove(child_resource)
                        removed_data["resource_families"][container]["child_resources"].append(child_resource)
                        modify_cmd = {"cmd": "remove_child_resource", "args": [child_resource]}
                        self.modify(modify_cmd, timestamp, removed_data=removed_data)
            elif resource in self._data["resource_families"][container]["child_resources"]:
                log.info("Child resource %s removed from container %s", resource, container)
                self._data["resource_families"][container]["child_resources"].remove(resource)
                removed_data["resource_families"].setdefault(container, {"parent_resources": [], "child_resources": []})
                removed_data["resource_families"][container]["child_resources"].append(resource)
                modify_cmd = {"cmd": "remove_child_resource", "args": [resource]}
                self.modify(modify_cmd, timestamp, removed_data=removed_data)
                if not self._data["resource_families"][container]["child_resources"]:
                    log.warning("Container %s no longer has any child resources", container)
                    for parent_resource in self._data["resource_families"][container]["parent_resources"]:
                        log.info("Removing parent resource %s from container %s", parent_resource, container)
                        self._data["resource_families"][container]["parent_resources"].remove(parent_resource)
                        removed_data["resource_families"][container]["parent_resources"].append(parent_resource)
                        modify_cmd = {"cmd": "remove_parent_resource", "args": [parent_resource]}
                        self.modify(modify_cmd, timestamp, removed_data=removed_data)
            else:
                raise ValueError("Resource {} was not found in current problem".format(resource))

        elif cmd_name == "return_to_resource_container":
            container, resource = cmd_args
            # If this was called directly and not via an undo command
            if add_removed_data["resource_families"] == {}:
                # Keys in this case are timestamps
                for check in sorted(self._removed_data_queue.keys(), reverse=True):
                    if container in self._removed_data_queue[check]["resource_families"]:
                        add_removed_data = self._removed_data_queue[check].copy()
                        break

            if add_removed_data["resource_families"] != {}:
                self._move_all_to_data(add_removed_data)
            else:
                if container not in self._data["resource_families"]:
                    raise ValueError("Container {} was not found in current problem".format(container))
                if resource in self._data["parent_resources"]:
                    log.info("Parent resource %s returned to container %s", resource, container)
                    self._data["resource_families"][container]["parent_resources"].append(resource)
                elif resource in self._data["child_resources"]:
                    log.info("Child resource %s returned to container %s", resource, container)
                    self._data["resource_families"][container]["child_resources"].append(resource)
                else:
                    raise ValueError("Resource {} was not found in current problem".format(resource))

        elif cmd_name == "remove_from_parent_activity":
            parent_activity, child_activity = cmd_args
            if parent_activity not in self._data["activity_children"]:
                raise ValueError("Parent activity {} was not found in current problem".format(parent_activity))
            if child_activity not in self._data["activity_children"][parent_activity]:
                raise ValueError("Child activity {} was not found in current problem".format(child_activity))

            log.info("Child activity %s removed from parent activity %s", child_activity, parent_activity)
            self._data["activity_children"][parent_activity].remove(child_activity)
            if not self._data["activity_children"][parent_activity]:
                log.warning("Parent activity %s no longer has any related child activities", parent_activity)
            fh_append(removed_data["activity_children"], parent_activity, child_activity)

        elif cmd_name == "return_to_parent_activity":
            parent_activity, child_activity = cmd_args
            if child_activity not in self._data["child_activities"]:
                raise ValueError("Child activity {} was not found in current problem".format(child_activity))
            if parent_activity not in self._data["parent_activities"]:
                raise ValueError("Parent activity {} was not found in current problem".format(parent_activity))

            if parent_activity not in self._data["activity_children"]:
                log.info("First child activity %s added for parent activity %s", child_activity, parent_activity)
                self._data["activity_children"][parent_activity] = []
            if child_activity in self._data["activity_children"][parent_activity]:
                raise ValueError(
                    "Child activity {} has already been returned to parent activity {}".format(child_activity, parent_activity)
                )
            log.info("Adding child activity %s to parent activity %s", child_activity, parent_activity)
            self._data["activity_children"][parent_activity].append(child_activity)
        elif cmd_name in ("modify_parent_budget", "modify_child_budget"):
            if cmd_name == "modify_parent_budget":
                resources, avail_amt = "parent_resources", "avail_parent_amt"
            else:  # modify_child_budget
                resources, avail_amt = "child_resources", "avail_child_amt"

            budget, resource = cmd_args
            if resource not in self._data[resources]:
                raise ValueError("Resource {} was not found in current problem".format(resource))
            log.info("cmd_name %s: Resource %s now has a budget of %s", cmd_name, resource, budget)
            self._data[avail_amt][resource] = budget
        elif cmd_name in ("modify_parent_cost", "modify_child_cost"):
            if cmd_name == "modify_parent_cost":
                resources, activities, req_amt = "parent_resources", "parent_activities", "req_parent_amt"
            else:  # modify_child_cost
                resources, activities, req_amt = "child_resources", "child_activities", "req_child_amt"

            cost, resource, activity = cmd_args
            if resource not in self._data[resources]:
                raise ValueError("Resource {} was not found in current problem".format(resource))
            if activity not in self._data[activities]:
                raise ValueError("Activity {} was not found in current problem".format(activity))
            res_act = (resource, activity)
            log.info("Resource/Activity %s has a cost of %s", res_act, cost)
            self._data[req_amt][res_act] = cost
        elif cmd_name in ("add_parent_allocation", "add_child_allocation"):
            resource, activity = cmd_args
            if cmd_name == "add_parent_allocation":
                resources, activities, possible_allocations = "parent_resources", "parent_activities", "parent_possible_allocations"
            else:  # add_child_allocation
                resources, activities, possible_allocations = "child_resources", "child_activities", "child_possible_allocations"

            if resource not in self._data[resources]:
                raise ValueError("Resource {} was not found in current problem".format(resource))
            if activity not in self._data[activities]:
                raise ValueError("Activity {} was not found in current problem".format(activity))

            if resource not in self._data[possible_allocations]:
                log.info("First allocations added for resource %s", resource)
                self._data[possible_allocations][resource] = []
            if activity in self._data[possible_allocations][resource]:
                raise ValueError("Activity {} has already been added as an allocation to resource {}".format(activity, resource))
            log.info("Resource %s can now be allocated to activity %s", resource, activity)
            self._data[possible_allocations][resource].append(activity)

        elif cmd_name in ("remove_parent_allocation", "remove_child_allocation"):
            if cmd_name == "remove_parent_allocation":
                possible_allocations = "parent_possible_allocations"
            else:  # remove_child_allocation
                possible_allocations = "child_possible_allocations"
            resource, activity = cmd_args
            if resource not in self._data[possible_allocations]:
                raise ValueError("Resource {} was not found in current problem".format(resource))
            if activity not in self._data[possible_allocations][resource]:
                raise ValueError("Activity {} was not found in current problem".format(activity))
            log.info("Resource %s can no longer be allocated to activity %s", resource, activity)
            self._data[possible_allocations][resource].remove(activity)
            if not self._data[possible_allocations][resource]:
                log.warning("Resource %s no longer has any possible allocations", resource)
            fh_append(removed_data[possible_allocations], resource, activity)

        elif cmd_name == "add_new_resource_container":
            container = cmd_args[0]
            if container in self._data["resource_families"]:
                raise ValueError("Resource container {} already exists in current problem".format(container))
            log.info("Added %s as a new resource container", container)
            self._data["resource_families"][container] = empty_container_dict
            if container in add_removed_data["resource_families"]:
                self._move_all_to_data(add_removed_data)

        elif cmd_name == "remove_resource_container":
            container = cmd_args[0]
            if container not in self._data["resource_families"]:
                raise ValueError("Resource container {} was not found in current problem".format(container))

            log.info("Removed %s as a resource container", container)
            for parent_resource in self._data["resource_families"][container]["parent_resources"]:
                modify_cmd = {"cmd": "remove_parent_resource", "args": [parent_resource]}
                self.modify(modify_cmd, timestamp, removed_data=removed_data)
            for child_resource in self._data["resource_families"][container]["child_resources"]:
                modify_cmd = {"cmd": "remove_child_resource", "args": [child_resource]}
                self.modify(modify_cmd, timestamp, removed_data=removed_data)
            family = self._data["resource_families"].pop(container)
            fh_extend(
                removed_data["resource_families"], container, family["parent_resources"], type_resources="parent_resources",
            )
            fh_extend(
                removed_data["resource_families"], container, family["child_resources"], type_resources="child_resources",
            )
            if not self._data["resource_families"]:
                log.warning("There are no more containers in the current problem")

        elif cmd_name in ("add_new_parent_resource", "add_new_child_resource"):
            resource = cmd_args[0]
            if cmd_name == "add_new_parent_resource":
                resources, possible_allocations = "parent_resources", "parent_possible_allocations"
            else:  # add_new_child_resource
                resources, possible_allocations = "child_resources", "child_possible_allocations"

            if resource in self._data[resources]:
                raise ValueError("Resource {} already exists in current problem".format(resource))
            log.info("Cmd %s: Added %s as a resource", cmd_name, resource)
            if add_removed_data[resources]:
                self._move_all_to_data(add_removed_data)
            else:
                self._data[resources].append(resource)

        elif cmd_name in ("remove_parent_resource", "remove_child_resource"):
            if cmd_name == "remove_parent_resource":
                resources, activities = "parent_resources", "parent_activities"
                possible_allocations, avail_amt, req_amt = "parent_possible_allocations", "avail_parent_amt", "req_parent_amt"
            else:  # remove_child_resource
                resources, activities = "child_resources", "child_activities"
                possible_allocations, avail_amt, req_amt = "child_possible_allocations", "avail_child_amt", "req_child_amt"

            resource = cmd_args[0]
            if resource not in self._data[resources]:
                raise ValueError("Resource {} was not found in current problem".format(resource))
            log.info("Removed %s as a resource", resource)
            self._data[resources].remove(resource)
            if not self._data[resources]:
                log.warning("There are no longer any %s in the current problem", resources)
            removed_data[resources].append(resource)

            if resource not in self._data[possible_allocations]:
                raise ValueError("Resource {} was not found in current problem".format(resource))
            activities_allocated_removed = self._data[possible_allocations].pop(resource)
            log.info("Removed %s as possible allocations for %s", activities_allocated_removed, resource)
            fh_extend(removed_data[possible_allocations], resource, activities_allocated_removed)

            for container in self._data["resource_families"].copy():
                if resource in self._data["resource_families"][container][resources]:
                    log.info("Removed resource %s from container %s", resource, container)
                    self._data["resource_families"][container][resources].remove(resource)
                    if not self._data["resource_families"][container][resources]:
                        log.warning("Container %s no longer has any %s", container, resources)
                    fh_append(removed_data["resource_families"], container, resource, type_resources=resources)

            if resource in self._data[avail_amt]:
                log.info("Removed budget associated with resource %s", resource)
                removed_data[avail_amt][resource] = self._data[avail_amt].pop(resource)

            for activity in self._data[activities]:
                res_act = (resource, activity)
                if res_act in self._data[req_amt]:
                    log.info("Removed cost associated with %s", res_act)
                    removed_data[req_amt][res_act] = self._data[req_amt].pop(res_act)

        elif cmd_name in ("add_new_parent_activity", "add_new_child_activity"):
            activity = cmd_args[0]
            if cmd_name == "add_new_parent_activity":
                activities = "parent_activities"
            else:  # add_new_child_activity
                activities = "child_activities"

            if activity in self._data[activities]:
                raise ValueError("Activity {} already exists in current problem".format(activity))
            log.info("cmd_name %s: Added %s as a activity", cmd_name, activity)
            if add_removed_data[activities]:
                self._move_all_to_data(add_removed_data)
            else:
                self._data[activities].append(activity)

        elif cmd_name in ("remove_parent_activity", "remove_child_activity"):
            activity = cmd_args[0]
            if cmd_name == "remove_parent_activity":
                resources, activities = "parent_resources", "parent_activities"
                possible_allocations, req_amt = "parent_possible_allocations", "req_parent_amt"

                if activity not in self._data["activity_children"]:
                    raise ValueError("Parent activity {} was not found in current problem".format(activity))
                child_activities = self._data["activity_children"].pop(activity)
                log.info("Removed child activities %s from parent activity %s", child_activities, activity)
                fh_extend(removed_data["activity_children"], activity, child_activities)

            else:  # remove_child_activity
                resources, activities = "child_resources", "child_activities"
                possible_allocations, req_amt = "child_possible_allocations", "req_child_amt"

                if activity in self._data["force_list"]:
                    self._data["force_list"].remove(activity)
                    log.info("Removed %s from force list", activity)
                    removed_data["force_list"].append(activity)

                if activity in self._data["forbid_list"]:
                    self._data["forbid_list"].remove(activity)
                    log.info("Removed %s from forbid list", activity)
                    removed_data["forbid_list"].append(activity)

                if activity in self._data["child_score"]:
                    log.info("Removed %s from set of values", activity)
                    removed_data["child_score"][activity] = self._data["child_score"].pop(activity)

                for parent_activity in self._data["activity_children"].copy():
                    if activity in self._data["activity_children"][parent_activity]:
                        log.info("Removed child activity %s from list of parent activity %s", activity, parent_activity)
                        self._data["activity_children"][parent_activity].remove(activity)
                        if not self._data["activity_children"][parent_activity]:
                            log.warning("Parent activity %s no longer has any related child activities", parent_activity)
                        fh_append(removed_data["activity_children"], parent_activity, activity)

            if activity not in self._data[activities]:
                raise ValueError("Activity {} was not found in current problem".format(activity))
            log.info("Removed %s as an activity", activity)
            self._data[activities].remove(activity)
            if not self._data[activities]:
                log.warning("There are no longer any %s in the current problem", activities)
            removed_data[activities].append(activity)

            for resource in self._data[possible_allocations].copy():
                if activity in self._data[possible_allocations][resource]:
                    log.info("Removed %s as a possible allocation from %s", activity, resource)
                    self._data[possible_allocations][resource].remove(activity)
                    if not self._data[possible_allocations][resource]:
                        log.warning("Resource %s no longer has any possible allocations", resource)
                    fh_append(removed_data[possible_allocations], resource, activity)

            for resource in self._data[resources]:
                res_act = (resource, activity)
                if res_act in self._data[req_amt]:
                    log.info("Removed cost associated with %s", res_act)
                    removed_data[req_amt][res_act] = self._data[req_amt].pop(res_act)
        else:
            raise ValueError("Cmd {} is not recognized".format(cmd_name))

        # Only copy removed_data to self._removed_data_queue once back at the original call to this modify_method
        if not recursive_call:
            num_entries = 0
            # Only copy to ._removed_data_queue if anything has been added to removed_data
            for v in removed_data.values():
                num_entries += len(v)
            if num_entries != 0:
                self._removed_data_queue[timestamp] = removed_data.copy()

    # Goes through all of the keys in the return_dict and puts them back into self._data
    def _move_all_to_data(self, return_dict):
        for container in return_dict["resource_families"]:
            if container not in self._data["resource_families"]:
                self._data["resource_families"][container] = {"parent_resources": [], "child_resources": []}
            self._data["resource_families"][container]["parent_resources"].extend(
                return_dict["resource_families"][container]["parent_resources"]
            )
            self._data["resource_families"][container]["child_resources"].extend(
                return_dict["resource_families"][container]["child_resources"]
            )

        for key in dm3k.slim_optimizer.util.util.full_house_input_dict_keys():
            if key != "resource_families":
                self._data[key].update(return_dict[key])

        for key in dm3k.slim_optimizer.util.util.full_house_input_list_keys():
            self._data[key].extend(return_dict[key])
