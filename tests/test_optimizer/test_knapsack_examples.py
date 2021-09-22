"""
Tests knapsack from internal interface
"""

import logging
import sys
import unittest

from .test_optimizer_helper import TestOptimizer

log = logging.getLogger(__name__)


class TestKnapsack(TestOptimizer):
    def setUp(self):
        log.info("Testing: " + self.__class__.__name__ + " " + self._testMethodName + "----------")
        self._opt = None
        self._opt_name = "KnapsackViz"

    def tearDown(self):
        pass

    def test_simple_knapsack(self):
        input_dict, output = self._all_steps("simpleKnapsack.json", self._opt_name)
        self._check_all(output, input_dict, 1)

        self.assertEqual(output.result["per_resource_score"]["backpack_Resource_instance_0"], 1)
        self.assertEqual(output.get_trace_df().iloc[0]["activity"], "item_Activity_instance_0")
        self.assertTrue(output.get_trace_df().iloc[0]["selected"])

    def test_simple_knapsack_contains_reward(self):
        input_dict, output = self._all_steps("simpleKnapsack_containsReward.json", self._opt_name)
        self._check_all(output, input_dict, 7)

    def test_multi_budget_knapsack(self):
        input_dict, output = self._all_steps("multiBudgetKnapsack.json", self._opt_name)
        self._check_all(output, input_dict, 4)

        self.assertEqual(output.result["per_resource_score"]["node_Resource_instance_0"], 2)
        self.assertEqual(output.result["per_resource_score"]["node_Resource_instance_1"], 2)
        self.assertEqual(output.get_trace_df().iloc[0]["activity"], "job_Activity_instance_2")
        self.assertTrue(output.get_trace_df().iloc[0]["selected"])
        self.assertEqual(output.get_trace_df().iloc[1]["activity"], "job_Activity_instance_1")
        self.assertTrue(output.get_trace_df().iloc[1]["selected"])
        self.assertEqual(output.get_trace_df().iloc[2]["activity"], "job_Activity_instance_3")
        self.assertTrue(output.get_trace_df().iloc[2]["selected"])

    def test_fanout_knapsack(self):
        input_dict, output = self._all_steps("fanOutKnapsack.json", self._opt_name)
        self._check_all(output, input_dict, 6)

        self.assertEqual(output.result["per_resource_score"]["bag_Resource_instance_0"], 3)
        self.assertEqual(output.result["per_resource_score"]["bag_Resource_instance_1"], 3)
        self.assertEqual(output.get_trace_df().iloc[0]["activity"], "food_Activity_instance_4")
        self.assertEqual(output.get_trace_df().iloc[0]["resource"], "bag_Resource_instance_0")
        self.assertTrue(output.get_trace_df().iloc[0]["selected"])
        self.assertEqual(output.get_trace_df().iloc[1]["activity"], "clean_Activity_instance_4")
        self.assertEqual(output.get_trace_df().iloc[1]["resource"], "bag_Resource_instance_1")
        self.assertTrue(output.get_trace_df().iloc[1]["selected"])
        self.assertEqual(output.get_trace_df().iloc[2]["activity"], "food_Activity_instance_0")
        self.assertEqual(output.get_trace_df().iloc[2]["resource"], "bag_Resource_instance_0")
        self.assertTrue(output.get_trace_df().iloc[2]["selected"])
        self.assertEqual(output.get_trace_df().iloc[3]["activity"], "clean_Activity_instance_0")
        self.assertEqual(output.get_trace_df().iloc[3]["resource"], "bag_Resource_instance_1")
        self.assertTrue(output.get_trace_df().iloc[3]["selected"])

    def test_fanout_knapsack_contains_reward(self):
        input_dict, output = self._all_steps("fanOutKnapsack_containsReward.json", self._opt_name)
        self._check_all(output, input_dict, 15)

    def test_fanin_knnapsack(self):
        input_dict, output = self._all_steps("fanInKnapsack.json", self._opt_name)
        self._check_all(output, input_dict, 6)

        self.assertEqual(output.result["per_resource_score"]["funding_Resource_instance_0"], 2)
        self.assertEqual(output.result["per_resource_score"]["funding_Resource_instance_1"], 4)
        self.assertEqual(output.result["per_resource_score"]["staff_Resource_instance_0"], 4)
        self.assertEqual(output.result["per_resource_score"]["staff_Resource_instance_1"], 2)

        self.assertEqual(output.get_trace_df().iloc[0]["resource"], "funding_Resource_instance_1")
        self.assertEqual(output.get_trace_df().iloc[0]["activity"], "startup_Activity_instance_2")
        self.assertTrue(output.get_trace_df().iloc[0]["selected"])
        self.assertEqual(output.get_trace_df().iloc[1]["resource"], "funding_Resource_instance_1")
        self.assertEqual(output.get_trace_df().iloc[1]["activity"], "startup_Activity_instance_4")
        self.assertTrue(output.get_trace_df().iloc[1]["selected"])

        self.assertEqual(output.get_trace_df().iloc[2]["resource"], "staff_Resource_instance_0")
        self.assertEqual(output.get_trace_df().iloc[2]["activity"], "startup_Activity_instance_2")
        self.assertTrue(output.get_trace_df().iloc[2]["selected"])
        self.assertEqual(output.get_trace_df().iloc[3]["resource"], "staff_Resource_instance_0")
        self.assertEqual(output.get_trace_df().iloc[3]["activity"], "startup_Activity_instance_4")
        self.assertTrue(output.get_trace_df().iloc[3]["selected"])

        self.assertEqual(output.get_trace_df().iloc[4]["resource"], "funding_Resource_instance_0")
        self.assertEqual(output.get_trace_df().iloc[4]["activity"], "startup_Activity_instance_1")
        self.assertTrue(output.get_trace_df().iloc[4]["selected"])
        self.assertEqual(output.get_trace_df().iloc[5]["resource"], "funding_Resource_instance_0")
        self.assertEqual(output.get_trace_df().iloc[5]["activity"], "startup_Activity_instance_3")
        self.assertTrue(output.get_trace_df().iloc[5]["selected"])

        self.assertEqual(output.get_trace_df().iloc[6]["resource"], "staff_Resource_instance_1")
        self.assertEqual(output.get_trace_df().iloc[6]["activity"], "startup_Activity_instance_1")
        self.assertTrue(output.get_trace_df().iloc[6]["selected"])
        self.assertEqual(output.get_trace_df().iloc[7]["resource"], "staff_Resource_instance_1")
        self.assertEqual(output.get_trace_df().iloc[7]["activity"], "startup_Activity_instance_3")
        self.assertTrue(output.get_trace_df().iloc[7]["selected"])

    def test_multi_problem_knnapsack(self):
        input_dict, output = self._all_steps("multiProblemKnapsack.json", self._opt_name)
        self._check_all(output, input_dict, 12)

        self.assertEqual(output.result["per_resource_score"]["funding_Resource_instance_0"], 2)
        self.assertEqual(output.result["per_resource_score"]["funding_Resource_instance_1"], 4)
        self.assertEqual(output.result["per_resource_score"]["staff_Resource_instance_0"], 4)
        self.assertEqual(output.result["per_resource_score"]["staff_Resource_instance_1"], 2)

        self.assertEqual(output.result["per_resource_score"]["bag_Resource_instance_0"], 3)
        self.assertEqual(output.result["per_resource_score"]["bag_Resource_instance_1"], 3)

    def test_combo_problem_knapsack(self):
        input_dict, output = self._all_steps("comboProblemKnapsack.json", self._opt_name)
        self._check_all(output, input_dict, 13)

    def test_fanout_knapsack_if_not(self):
        input_dict, output = self._all_steps("fanOutKnapsack_ifNot.json", self._opt_name)
        self._check_all(output, input_dict, 11)

    def test_fanout_knapsack_if_not_multi(self):
        input_dict, output = self._all_steps("fanOutKnapsack_ifNot_multi.json", self._opt_name)
        self._check_all(output, input_dict, 32)

    def test_fanout_knapsack_if_not_multi_combo(self):
        input_dict, output = self._all_steps("fanOutKnapsack_ifNot_multi_combo.json", self._opt_name)
        self._check_all(output, input_dict, 31)

    def test_simple_awd(self):
        input_dict, output = self._all_steps("SimpleAlienWorldDomination.json", self._opt_name)
        self._check_all(output, input_dict, 6)

    def test_awd_with_ship(self):
        input_dict, output = self._all_steps("AlienWorldDomination_wShip.json", self._opt_name)
        self._check_all(output, input_dict, 6)

    def test_camping(self):
        input_dict, output = self._all_steps("Camping.json", self._opt_name)
        self._check_all(output, input_dict, 24)

    def test_allocation_of_staff_to_tasks_user_stories_customers(self):
        input_dict, output = self._all_steps("AllocationOfStaffToTasksUserStoriesCustomers.json", self._opt_name)
        self._check_all(output, input_dict, 19)


if __name__ == "__main__":
    # FOR DEBUGGING USE...
    log = logging.getLogger()
    log.level = logging.DEBUG
    stream_handler = logging.StreamHandler(sys.stdout)
    log.addHandler(stream_handler)

    unittest.main()
