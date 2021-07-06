"""
Tests knapsack as if system was being used by dm3k-viz
"""
import json
import pandas
import logging
import os
import sys
import unittest
from unittest import TestCase

# ensure that optimizer directory is in path
app_directory = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', '..')
if app_directory not in sys.path:
    sys.path.append(app_directory)

from optimizer.slim_optimizer_main import create_opt

log = logging.getLogger(__name__)

class TestKnapsackE2E(TestCase):
    def setUp(self):
        log.info("Testing: " + self.__class__.__name__ + " " + self._testMethodName + "----------")
        self._opt = None

    def tearDown(self):
        pass

    # ---------------------------------------------
    #  UTILITY FUNCTIONS
    # ---------------------------------------------

    def _step1_load(self, data_filename):
        path_to_file = os.path.join(app_directory, "examples", data_filename)
        with open(path_to_file, "r") as f:
            input_dict = json.load(f)

        config = {"optimizer": "KnapsackViz"}

        log.debug("WORKING ON DATASET=" + input_dict["datasetName"])

        opt, validation_errors = create_opt(input_dict, config)
        self._opt = opt

        return input_dict, validation_errors
    
    def _step2_build(self):
        self._opt.build()
    
    def _step3_solve(self):
        self._opt.solve()
        results = self._opt.get_output()
        return results

    def _all_steps(self, data_filename):
        # ### STEP 1  - load data into system
        input_dict, validation_errors = self._step1_load(data_filename)

        if len(validation_errors) > 0:
            log.warning("VALIDATION ERRORS...")
            for e in validation_errors:
                log.warning(e)
        else:
            log.debug("No Validation errors")

        # ### STEP 2 - build the model
        self._step2_build()
       
        # ### STEP 3 / 4  - solving and output
        results = self._step3_solve()

        # check results
        log.debug("RESULTS...")
        log.debug("   Objective= " + str(results.get_objective_value()))
        log.debug("   Allocations...")
        log.debug(json.dumps(results.get_allocations(), indent=4))
        log.debug("   Allocated Amount...")
        log.debug(json.dumps(results.to_dict()["allocated_amt"], indent=4))
        log.debug("   Per Resource Score...")
        log.debug(json.dumps(results.to_dict()["per_resource_score"], indent=4))
        log.debug("   Per Resource Budget Used...")
        log.debug(json.dumps(results.to_dict()["per_resource_budget_used"], indent=4))
        log.debug("   Complete Trace...")
        pandas.set_option('display.max_rows', 1000)
        log.debug(results.get_trace_df())
        pandas.reset_option('display.max_rows')

        return input_dict, results

    def _find_instance(self, name, input_json, which="activityInstances"):
        ret_inst = None
        for i in input_json[which]:
            for inst in i["instanceTable"]:
                if inst["instanceName"] == name:
                    ret_inst = inst
        self.assertIsNotNone(ret_inst, msg="Could not find allocated item in input[" + which + "]")
        return ret_inst

    def _check_objective(self, results, predicted_obj_value):
        self.assertEqual(results.get_objective_value(), predicted_obj_value)

    def _check_selected_and_filled(self, results, input_json):
        # checks that all activities selected have received all the budget(s) they need

        # first get all allocated activities
        allocated_activities = []
        allocations = results.get_allocations()
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
        allocated_amts = results.to_dict()["allocated_amt"]
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

    def _check_budget_used(self, results, input_json):
        # checks that budget used per resource does not exceed the budget

        # get all input budgets
        input_budgets = {}
        for resI in input_json["resourceInstances"]:
            for res_inst in resI["instanceTable"]:
                res_name = res_inst["instanceName"]
                input_budgets[res_name] = res_inst["budget"]

        # make sure total resource budget used is less
        total_res_budget_used = results.to_dict()["per_resource_budget_used"]

        for res_name in total_res_budget_used:
            for budget_name in total_res_budget_used[res_name]:
                budget_used = total_res_budget_used[res_name][budget_name]
                self.assertLessEqual(budget_used, input_budgets[res_name][budget_name])

    def _check_all(self, results, input_dict, predicted_obj_value):

        # this type of input only has one file type
        input_data = input_dict["files"][0]["fileContents"]

        self._check_objective(results, predicted_obj_value)
        self._check_selected_and_filled(results, input_data)
        self._check_budget_used(results, input_data)

    # ---------------------------------------------
    #  TESTS AGAINST INPUT FILES
    # ---------------------------------------------

    def test_end2end_simpleKnapsack(self):
        input_dict, results = self._all_steps("simpleKnapsack.json")
        self._check_all(results, input_dict, 1)

        self.assertEqual(results.to_dict()["per_resource_score"]["backpack_Resource_instance_0"], 1)
        self.assertEqual(results.get_trace_df().iloc[0]["activity"], "item_Activity_instance_0")
        self.assertTrue(results.get_trace_df().iloc[0]["selected"])

    def test_end2end_simpleKnapsack_contains_reward(self):
        input_dict, results = self._all_steps("simpleKnapsack_containsReward.json")
        self._check_all(results, input_dict, 7)

    def test_end2end_multiBudgetKnapsack(self):
        input_dict, results = self._all_steps("multiBudgetKnapsack.json")
        self._check_all(results, input_dict, 4)

        self.assertEqual(results.to_dict()["per_resource_score"]["node_Resource_instance_0"], 2)
        self.assertEqual(results.to_dict()["per_resource_score"]["node_Resource_instance_1"], 2)
        self.assertEqual(results.get_trace_df().iloc[0]["activity"], "job_Activity_instance_2")
        self.assertTrue(results.get_trace_df().iloc[0]["selected"])
        self.assertEqual(results.get_trace_df().iloc[1]["activity"], "job_Activity_instance_1")
        self.assertTrue(results.get_trace_df().iloc[1]["selected"])
        self.assertEqual(results.get_trace_df().iloc[2]["activity"], "job_Activity_instance_3")
        self.assertTrue(results.get_trace_df().iloc[2]["selected"])

    def test_end2end_fanOutKnapsack(self):
        input_dict, results = self._all_steps("fanOutKnapsack.json")
        self._check_all(results, input_dict, 6)

        self.assertEqual(results.to_dict()["per_resource_score"]["bag_Resource_instance_0"], 3)
        self.assertEqual(results.to_dict()["per_resource_score"]["bag_Resource_instance_1"], 3)
        self.assertEqual(results.get_trace_df().iloc[0]["activity"], "food_Activity_instance_4")
        self.assertEqual(results.get_trace_df().iloc[0]["resource"], "bag_Resource_instance_0")
        self.assertTrue(results.get_trace_df().iloc[0]["selected"])
        self.assertEqual(results.get_trace_df().iloc[1]["activity"], "clean_Activity_instance_4")
        self.assertEqual(results.get_trace_df().iloc[1]["resource"], "bag_Resource_instance_1")
        self.assertTrue(results.get_trace_df().iloc[1]["selected"])
        self.assertEqual(results.get_trace_df().iloc[2]["activity"], "food_Activity_instance_0")
        self.assertEqual(results.get_trace_df().iloc[2]["resource"], "bag_Resource_instance_0")
        self.assertTrue(results.get_trace_df().iloc[2]["selected"])
        self.assertEqual(results.get_trace_df().iloc[3]["activity"], "clean_Activity_instance_0")
        self.assertEqual(results.get_trace_df().iloc[3]["resource"], "bag_Resource_instance_1")
        self.assertTrue(results.get_trace_df().iloc[3]["selected"])

    def test_end2end_fanInKnapsack(self):
        input_dict, results = self._all_steps("fanInKnapsack.json")
        self._check_all(results, input_dict, 6)

        self.assertEqual(results.to_dict()["per_resource_score"]["funding_Resource_instance_0"], 2)
        self.assertEqual(results.to_dict()["per_resource_score"]["funding_Resource_instance_1"], 4)
        self.assertEqual(results.to_dict()["per_resource_score"]["staff_Resource_instance_0"], 4)
        self.assertEqual(results.to_dict()["per_resource_score"]["staff_Resource_instance_1"], 2)

        self.assertEqual(results.get_trace_df().iloc[0]["resource"], "funding_Resource_instance_1")
        self.assertEqual(results.get_trace_df().iloc[0]["activity"], "startup_Activity_instance_2")
        self.assertTrue(results.get_trace_df().iloc[0]["selected"])
        self.assertEqual(results.get_trace_df().iloc[1]["resource"], "funding_Resource_instance_1")
        self.assertEqual(results.get_trace_df().iloc[1]["activity"], "startup_Activity_instance_4")
        self.assertTrue(results.get_trace_df().iloc[1]["selected"])

        self.assertEqual(results.get_trace_df().iloc[2]["resource"], "staff_Resource_instance_0")
        self.assertEqual(results.get_trace_df().iloc[2]["activity"], "startup_Activity_instance_2")
        self.assertTrue(results.get_trace_df().iloc[2]["selected"])
        self.assertEqual(results.get_trace_df().iloc[3]["resource"], "staff_Resource_instance_0")
        self.assertEqual(results.get_trace_df().iloc[3]["activity"], "startup_Activity_instance_4")
        self.assertTrue(results.get_trace_df().iloc[3]["selected"])

        self.assertEqual(results.get_trace_df().iloc[4]["resource"], "funding_Resource_instance_0")
        self.assertEqual(results.get_trace_df().iloc[4]["activity"], "startup_Activity_instance_1")
        self.assertTrue(results.get_trace_df().iloc[4]["selected"])
        self.assertEqual(results.get_trace_df().iloc[5]["resource"], "funding_Resource_instance_0")
        self.assertEqual(results.get_trace_df().iloc[5]["activity"], "startup_Activity_instance_3")
        self.assertTrue(results.get_trace_df().iloc[5]["selected"])

        self.assertEqual(results.get_trace_df().iloc[6]["resource"], "staff_Resource_instance_1")
        self.assertEqual(results.get_trace_df().iloc[6]["activity"], "startup_Activity_instance_1")
        self.assertTrue(results.get_trace_df().iloc[6]["selected"])
        self.assertEqual(results.get_trace_df().iloc[7]["resource"], "staff_Resource_instance_1")
        self.assertEqual(results.get_trace_df().iloc[7]["activity"], "startup_Activity_instance_3")
        self.assertTrue(results.get_trace_df().iloc[7]["selected"])

    def test_end2end_multiProblemKnapsack(self):
        input_dict, results = self._all_steps("multiProblemKnapsack.json")
        self._check_all(results, input_dict, 12)

        self.assertEqual(results.to_dict()["per_resource_score"]["funding_Resource_instance_0"], 2)
        self.assertEqual(results.to_dict()["per_resource_score"]["funding_Resource_instance_1"], 4)
        self.assertEqual(results.to_dict()["per_resource_score"]["staff_Resource_instance_0"], 4)
        self.assertEqual(results.to_dict()["per_resource_score"]["staff_Resource_instance_1"], 2)

        self.assertEqual(results.to_dict()["per_resource_score"]["bag_Resource_instance_0"], 3)
        self.assertEqual(results.to_dict()["per_resource_score"]["bag_Resource_instance_1"], 3)

    def test_end2end_comboProblemKnapsack(self):
        input_dict, results = self._all_steps("comboProblemKnapsack.json")
        self._check_all(results, input_dict, 13)

    def test_end2end_fanOutKnapsack_ifNot(self):
        input_dict, results = self._all_steps("fanOutKnapsack_ifNot.json")
        self._check_all(results, input_dict, 11)

    def test_end2end_fanOutKnapsack_ifNot_multi(self):
        input_dict, results = self._all_steps("fanOutKnapsack_ifNot_multi.json")
        self._check_all(results, input_dict, 32)

    def test_end2end_fanOutKnapsack_ifNot_multi_combo(self):
        input_dict, results = self._all_steps("fanOutKnapsack_ifNot_multi_combo.json")
        self._check_all(results, input_dict, 31)

    def test_end2end_simple_AWD(self):
        input_dict, results = self._all_steps("SimpleAlienWorldDomination.json")
        self._check_all(results, input_dict, 6)

    def test_end2end_AWD_with_ship(self):
        input_dict, results = self._all_steps("AlienWorldDomination_wShip.json")
        self._check_all(results, input_dict, 6)

    def test_end2end_AWD_with_ship_no_connections(self):
        input_dict, results = self._all_steps("AWD_wShip_wNoConnections.json")
        self._check_all(results, input_dict, 0)


if __name__ == "__main__":
    # FOR DEBUGGING USE...
    log = logging.getLogger()
    log.level = logging.DEBUG
    stream_handler = logging.StreamHandler(sys.stdout)
    log.addHandler(stream_handler)

    unittest.main()
