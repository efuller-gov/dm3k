"""
This greedy heuristic is not actually an optimizer.  It provides a possible allocation that tries to allocate
resources to DUs in order of value, thus giving an approximation of an optimal solution.  It can be used to compare
with the optimization models, or to quickly give an allocation that might be helpful.
"""


from collections import defaultdict
from copy import copy

import pandas as pd
# from dm3k.dm3k_utils.data_utils import reverse_dict_of_lists
from optimizer.full_house.full_house_input import FullHouseInput
from optimizer.slim_optimizer_base import ModelBase, OutputBase
from optimizer.util.util import full_house_full_trace_keys


class GreedyOutput(OutputBase):
    def __init__(self, model_obj):
        df = pd.DataFrame(model_obj.get_model().solution, columns=full_house_full_trace_keys())
        self.set_objective_value(df.value.sum())

        self.set_results(
            {
                "full_trace": df.to_dict("list"),
                "parent_score": df.groupby("parent_resource")["value"].sum().to_dict(),
                "child_score": df.groupby("child_resource")["value"].sum().to_dict(),
                "container_score": df.groupby("container_name")["value"].sum().to_dict(),
            }
        )

        parent = df.groupby("parent_resource")["parent_activity"].apply(set).to_dict()
        child = df.groupby("child_resource")["child_activity"].apply(set).to_dict()

        self.set_allocations({"parent": {k: list(v) for k, v in parent.items()}, "child": {k: list(v) for k, v in child.items()}})

    def to_dict(self):
        return self._result


class FullHouseModelGreedy(ModelBase):
    def __init__(self):
        super().__init__()

    def build(self, data):
        self._model = GreedyModel(data)

    def solve(self, **kwargs):
        self._model.solve()

    def can_solve(self, input_instance):
        """
        In the event the system can leverage multiple models, this function is used to determine if this model
        can solve the input.

        :param input_instance  : a instance of the InputBase class
        :return: Boolean, True = yes, this model can solve it.  False = something about input cannot be solved by model
        """
        # the FullHouseModel can solve any input in the form of the FullHouseInput class
        return isinstance(input_instance, FullHouseInput)

    def fill_output(self, output_class=GreedyOutput):
        return output_class(self)


class GreedyModel:
    def __init__(self, data):
        self.avail_parent_amt = data["avail_parent_amt"]
        self.avail_child_amt = data["avail_child_amt"]
        self.req_parent_amt = data["req_parent_amt"]
        self.req_child_amt = data["req_child_amt"]
        self.child_score = data["child_score"]
        self.parent_pos_alloc = data["parent_possible_allocations"]
        self.child_pos_alloc = data["child_possible_allocations"]
        self.resource_fam = data["resource_families"]
        self.act_children = data["activity_children"]

        # make working copies that can be changed repeatedly
        self.working_child_amt = copy(self.avail_child_amt)
        self.working_parent_amt = copy(self.avail_parent_amt)
        self.working_parent_req = copy(self.req_parent_amt)

        self.du_par = reverse_dict_of_lists(self.act_children)
        self.rev_par_al = reverse_dict_of_lists(self.parent_pos_alloc)
        self.rev_cont = defaultdict(list)
        self.solution = []

        for key in self.resource_fam:
            for val in self.resource_fam[key]["parent_resources"]:
                self.rev_cont[val].append(key)

    def __find_first_feasible(self, du):
        """
        check whether du can be reached given the current state by:
        1. What parents does it have?
        2. What resources can be allocated to those?  Pick the first one that has capacity and a matching child resource with capacity

        Args:
            du: name of du to check if can be added

        Returns:
            a row of the allocation set, suitable for output
        """
        for par_act in self.du_par[du]:
            for par_res in self.rev_par_al[par_act]:
                if self.working_parent_req[(par_res, par_act)] <= self.working_parent_amt[par_res]:
                    for container in self.rev_cont[par_res]:
                        for child_res in self.resource_fam[container]["child_resources"]:
                            if du in self.child_pos_alloc[child_res]:
                                if self.req_child_amt[(child_res, du)] <= self.working_child_amt[child_res]:
                                    self.working_parent_amt[par_res] -= self.working_parent_req[(par_res, par_act)]
                                    self.working_child_amt[child_res] -= self.req_child_amt[(child_res, du)]
                                    self.working_parent_req[par_res, par_act] = 0  # since we already picked it, no addl cost

                                    return (
                                        container,
                                        self.req_child_amt[(child_res, du)],
                                        child_res,
                                        du,
                                        self.req_parent_amt[(par_res, par_act)],
                                        par_res,
                                        par_act,
                                        1,
                                        self.child_score[du],
                                    )
        return None

    def solve(self):
        self.solution = []
        for du, score in sorted(self.child_score.items(), key=lambda x: x[1], reverse=True):
            used = self.__find_first_feasible(du)
            if used:
                # list of allocations
                self.solution.append(used)
