"""
File containing methods used by tests
"""
import json
import logging
import os
import sys
from unittest import TestCase

import pandas

log = logging.getLogger(__name__)

# ensure that optimizer directory is in path
app_directory = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..")
if app_directory not in sys.path:
    sys.path.append(app_directory)

from optimizer.slim_optimizer_main import create_opt  # noqa: E402


class TestOptimizer(TestCase):
    def _step1_load(self, data_filename, opt_name):
        path_to_file = os.path.join(app_directory, "examples", data_filename)
        with open(path_to_file, "r") as f:
            input_dict = json.load(f)

        log.debug("WORKING ON DATASET=" + input_dict["datasetName"])

        self._opt, validation_errors = create_opt(input_dict, opt_name)

        return input_dict, validation_errors

    def _step2_build(self):
        self._opt.build()

    def _step3_solve(self):
        self._opt.solve()
        return self._opt.output

    def _all_steps(self, data_filename, opt_name):
        # ### STEP 1  - load data into system
        input_dict, validation_errors = self._step1_load(data_filename, opt_name)

        if len(validation_errors) > 0:
            log.warning("VALIDATION ERRORS...")
            for e in validation_errors:
                log.warning(e)
        else:
            log.debug("No Validation errors")

        # ### STEP 2 - build the model
        self._step2_build()

        # ### STEP 3 / 4  - solving and output
        output = self._step3_solve()

        # check output
        log.debug("output...")
        log.debug("   Objective= " + str(output.objective_value))
        log.debug("   Allocations...")
        log.debug(json.dumps(output.allocations, indent=4))
        log.debug("   Allocated Amount...")
        log.debug(json.dumps(output.result["allocated_amt"], indent=4))
        log.debug("   Per Resource Score...")
        log.debug(json.dumps(output.result["per_resource_score"], indent=4))
        log.debug("   Per Resource Budget Used...")
        log.debug(json.dumps(output.result["per_resource_budget_used"], indent=4))
        log.debug("   Complete Trace...")
        pandas.set_option("display.max_rows", 1000)
        log.debug(output.get_trace_df())
        pandas.reset_option("display.max_rows")

        return input_dict, output

    def _find_instance(self, name, input_json, which="activityInstances"):
        ret_inst = None
        for i in input_json[which]:
            for inst in i["instanceTable"]:
                if inst["instanceName"] == name:
                    ret_inst = inst
        self.assertIsNotNone(ret_inst, msg="Could not find allocated item in input[" + which + "]")
        return ret_inst

    def _check_objective(self, output, predicted_obj_value):
        self.assertEqual(output.objective_value, predicted_obj_value)

    def _check_selected_and_filled(self, output, input_json):
        # checks that all activities selected have received all the budget(s) they need

        # first get all allocated activities
        allocated_activities = []
        allocations = output.allocations
        for res in allocations:
            for act in allocations[res]:
                if act not in allocated_activities:
                    allocated_activities.append(act)

        # second determine the need amounts per activity
        need_amt_per_act = {}
        for act in allocated_activities:

            # find the need (cost)
            act_inst = self._find_instance(act, input_json, which="activityInstances")
            need_amt = act_inst["cost"]
            need_amt_per_act[act] = need_amt

        # then determine the allocated amounts per activity
        allocated_amts = output.result["allocated_amt"]
        alloc_amt_per_act = {}
        for res in allocated_amts:
            for act in allocated_amts[res]:
                if act not in alloc_amt_per_act:
                    alloc_amt_per_act[act] = {}

                alloc_amt_per_act[act].update(allocated_amts[res][act])

        # Finally do these match up
        for act in need_amt_per_act:
            self.assertIn(act, alloc_amt_per_act)  # if act is not in alloc_amt per act, error
            self.assertDictEqual(need_amt_per_act[act], alloc_amt_per_act[act])

    def _check_budget_used(self, output, input_json):
        # checks that budget used per resource does not exceed the budget

        # get all input budgets
        input_budgets = {}
        for res_instances in input_json["resourceInstances"]:
            for res_inst in res_instances["instanceTable"]:
                res_name = res_inst["instanceName"]
                input_budgets[res_name] = res_inst["budget"]

        # make sure total resource budget used is less
        total_res_budget_used = output.result["per_resource_budget_used"]

        for res_name in total_res_budget_used:
            for budget_name in total_res_budget_used[res_name]:
                budget_used = total_res_budget_used[res_name][budget_name]
                self.assertLessEqual(budget_used, input_budgets[res_name][budget_name])

    def _check_all(self, output, input_dict, predicted_obj_value):

        # this type of input only has one file type
        input_data = input_dict["files"][0]["fileContents"]

        self._check_objective(output, predicted_obj_value)
        self._check_selected_and_filled(output, input_data)
        self._check_budget_used(output, input_data)
