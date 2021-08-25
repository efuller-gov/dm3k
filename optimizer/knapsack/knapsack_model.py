"""
A component-based way of solving the knapsack problem

What are the characteristics of a knapsack problem
    - a resource can have 1 or more budgets
    - multiple activities
    - each activity has "rewards" attribute and some have "costs" attribute
    - activity can only have 1 reward   **INPUT CHECK**
    - resource classes can be allocated to 1 or more activity classes (allocated activity classes have "costs" )
    - a resource instance can be allocated to one or more activity instances (as long as total budget for resource
        is not violated)
    - resources cannot pool budgets to allocated to an activity (2 resources cannot be allocated to the same activity)
    - all activity and resource instance names must be unique  **INPUT CHECK**
    - all budgets and costs defined by resource classes or activity classes must have instance values in each instance  **INPUT CHECK**
    - activities can be contained by other activities
    - containing activities can have rewards, which are given if all children of group is allocated
    - allocated to links can be constrained with IF NOT (if you allocate a resource instance to an activity instance of one activity class,
        you may not allocate it an activity instance of another activity class)
    - allocated to links can be constrained with IF CONTAINS (a child resource can only be allocated to a child activity, if a parent
        resource that contains the child resource is allocated to a parent activity that contains the child activity)

The following constraints use abbreviations:
a_id = activity id
ca_id = child activity id
r_id = resource id
b_id = budget_id

"""

import logging
import sys
from collections import deque

from pyomo.environ import Any, Binary, ConcreteModel, Constraint, NonNegativeReals, Objective, Param, Set, Var, maximize

from optimizer.knapsack.knapsack_input_viz import KnapsackInputViz
from optimizer.slim_optimizer_base import ModelBase

log = logging.getLogger(__name__)


# -------------------------------------------------------------------------------
# OBJECTIVES
# -------------------------------------------------------------------------------
def objective_rule(model):
    """
    Maximize the sum of all rewards of activities that are 'picked' (selected)
    """
    return sum(model.PICKED[a_id] * model.reward[a_id] for a_id in model.act_id_index)


# -------------------------------------------------------------------------------
# CONSTRAINTS
# -------------------------------------------------------------------------------
def required_amount_rule(model, r_id, a_id, b_id):
    """
    In order for a resource to be allocated to an activity, a certain amount of budget is required.
    A activity is selected if and only if the provided amount is sufficient. (across all budgets)

    :param ConcreteModel model:
    :param int r_id: the id number of the resource instance
    :param int a_id: the id number of the activity instance
    :param int b_id:  the id number of the budget class
    :return: boolean indicating whether the needed amount is allocated from resource to activity
    """
    return model.ALLOCATED_AMT[r_id, a_id, b_id] == model.required_amount[a_id, b_id] * model.ALLOCATED[r_id, a_id]


def act_picked_rule(model, a_id):
    """
    An activity is picked (selected) if a resource was allocated to it along all the possible incoming 'allocated to'
    arrows

    NOTE -  this was necessary to handle fan-in conditions where multiple incoming allocation arrows have to be
            satisfied

    :param ConcreteModel model:
    :param int a_id: the id number of the activity instance
    :return: boolean indicating whether resource have been allocated along all possible incoming allocation paths
    """
    return (
        sum(model.ALLOCATED[r_id, a_id] for r_id in model.total_reverse_allocations[a_id])
        >= model.num_incoming_pairs[a_id] * model.PICKED[a_id]
    )


def act_picked_contains_rule(model, a_id):
    """
    An activity is picked (selected) if all the child activities contained by this activity are picked

    :param ConcreteModel model:
    :param a_id: the id number of the activity instance
    :return: boolean indicating whether all activities contained are picked
    """
    return model.num_contained_activities[a_id] * model.PICKED[a_id] <= sum(
        model.PICKED[ca_id] for ca_id in model.contained_activities[a_id]
    )


def available_amount_rule(model, r_id, b_id):
    """
    Each resource has a limited resource budget; it cannot allocate more than that.

    :param ConcreteModel model:
    :param int r_id: the id number of the resource instance
    :param int b_id:  the id number of the budget class
    :return: boolean indicating whether pr is staying within budget
    """

    if model.possible_allocations[r_id]:
        return (
            sum(model.ALLOCATED_AMT[r_id, a_id, b_id] for a_id in model.possible_allocations[r_id]) <= model.available_amount[r_id, b_id]
        )
    else:
        return Constraint.Skip


def allocated_limit_rule(model, p_id, a_id):
    """
    An activity may not be allocated more than once by a resource-activity pair

    :param ConcreteModel model:
    :param int p_id: the id number of the resource-activity pair
    :param int a_id: the id number of the activity instance
    :return: boolean indicating whether ca is allocated at most once.
    """
    if model.reverse_allocations[p_id, a_id]:
        return sum(model.ALLOCATED[r_id, a_id] for r_id in model.reverse_allocations[p_id, a_id]) <= 1
    else:
        return Constraint.Skip


def if_not_limit_rule(model, r_id, a_id):
    """
    "IF-NOT" allocation constraints prevent a Resource Instances from being allocated to more than one class of Activity.

    (e.g. if I am allocating grocery bags to different types of grocery items, and I don't want grocery items that are
    cleaning supplies to be in the same bag as food items...I can use an IF-NOT allocation constraint to enforce this)

    :param ConcreteModel model:
    :param int r_id: the id number of the resource instance
    :param int a_id: the id number of the activity instance
    :return: [description]
    """
    if model.not_allocations[r_id, a_id]:
        return len(model.not_allocations[r_id, a_id]) * model.ALLOCATED[r_id, a_id] + sum(
            model.ALLOCATED[r_id, not_a_id] for not_a_id in model.not_allocations[r_id, a_id]
        ) <= len(model.not_allocations[r_id, a_id])
    else:
        return Constraint.Skip


def if_contains_rule(model, r_id, a_id):
    """
    when an Contained IF-THEN constraint exists, you can only allocate a resource instance (resource 1) to an activity instance (activity 1) along the allocation
    link (that is the target of the constraint) if you have allocated a resource instance, that is in the contains hierarchy of resource 1, to
    an activity instances, that is in the contains hierarchy of activity 1.

    For example, a missile (resource1) can hit a target (activity1) only if the missile launcher (a container of the missile) is pointed in the
    geographic region in which the target exists (geographic region is a container of target)

    :param ConcreteModel model: [description]
    :param int r_id: the id number of the resource instance (the contained resource, aka child resource)
    :param int a_id: the id number of the activity instance (the contained activity, aka child activity)
    :return: [description]
    """
    return model.ALLOCATED[r_id, a_id] <= sum(model.ALLOCATED[pr, pa] for (pr, pa) in model.containing_allocations[r_id, a_id])


def if_contains_picked(model, a_id):
    """
    When an contained IF-THEN constraint exists, you may have a allocatedTo link without a reward, since the reward of selecting an allocation
    to a activity without a reward may be to open up the ability to allocated to an activity with a reward.

    for example, there may be no reward for allocating a missile launcher to a geographic region...but that allocation is necessary to shot
    missiles at VIPs in that geographic region.

    Therefore the activities without rewards will be not PICKED
    """
    if model.no_reward_allocation[a_id]:
        return (
            sum(model.ALLOCATED[r_id, a_id] for r_id in model.total_reverse_allocations[a_id])
            == model.num_incoming_pairs[a_id] * model.PICKED[a_id]
        )
    else:
        return Constraint.Skip


# -------------------------------------------------------------------------------
# MODEL
# -------------------------------------------------------------------------------
class KnapsackModel(ModelBase):
    def __init__(self):
        super().__init__()
        self._data = None

    def can_solve(self, input_instance):
        """
        In the event the system can leverage multiple models, this function is used to determine if this model
        can solve the input.

        :param KnapsackInputViz input_instance: a instance of the InputBase class
        :return: Boolean, True = yes, this model can solve it.  False = something about input cannot be solved by model
        """
        # the KnapsackComponentModel can solve any input in the form of the KnapsackInputViz class
        return isinstance(input_instance, KnapsackInputViz)

    def build(self, data):
        """
        Build the pyomo model in self._model

        :param data: a dictionary containing all necessary data for the model (this will be defined on a model by model
                     basis)  NOTE - this comes from input class to_data() method
        :return: None
        """
        self._data = data
        log.info("Building Pyomo model...")
        self._model = ConcreteModel()

        # all indices, relationships, params and constraints to support any number of resources allocated to any number of activities
        self.__create_for_base_res_act_relationship()

        # all indices, relationships, params and constraints to support contained rewards
        self.__create_for_contained_reward()

        # all indices, relationships, params, and constraints to support IF-NOT constraints
        self.__create_for_if_not_constraint()

        # all indices, relationships, params, and constraints to support Contained IF-THEN
        self.__create_contained_if_constraint()

        self.__create_objective()

        log.info("....Pyomo model complete")

        if "unittest" not in sys.modules:
            log.debug(self._model.pprint())

    def __create_for_base_res_act_relationship(self):
        log.info("CREATING BASE COMPONENT:  Resource-Activity Allocation...")
        self.__create_indices()
        self.__create_relationships()
        self.__create_params_variables()
        self.__create_constraints()

    def __create_contained_if_constraint(self):
        """
        contained if-then constraints occur when a allocation constraint is placed between two 'allocated to' links where the resources contain
        each other and the activities contain each other
        """
        log.info("CREATING ADDITIONAL COMPONENT: Contained IF-THEN Constraints")
        contained_if_constraint_present = False
        for item in self._data["allocationConstraints"]:
            if item["allocationConstraintType"] == "Contained IF-THEN":
                contained_if_constraint_present = True
                break

        if not contained_if_constraint_present:
            log.info("....NO constrained IF-THEN constraints! cant make this component")
            return

        # indices
        r_a_arcs_for_contains = []  # a list of all possible resource to activity allocations BUT
        #  only for allocations relevant to the contains constraint

        # containing_allocations is a map of pairs (end_resource_instance_name, end_activity_instance_name) to the
        # potential list of pairs (start_resource_instance_name, start_activity_instance_name) that can enable the key pair.
        containing_allocations = {}  # names version
        containing_allocations_id = {}  # a dict with keys = [resource_id, activity_id] and values = list of
        # (res_id, act_id) pairs that contain the (resource_id, activity_id) pair

        for item in self._data["allocationConstraints"]:
            if item["allocationConstraintType"] == "Contained IF-THEN":
                # get the names out
                start_r_name = item["allocationStart"]["resourceClass"]
                start_a_name = item["allocationStart"]["activityClass"]
                end_r_name = item["allocationEnd"]["resourceClass"]
                end_a_name = item["allocationEnd"]["activityClass"]

                # create hierarchies
                start_r_hierarchy = self._get_hierarchy_trace(start_r_name)
                start_a_hierarchy = self._get_hierarchy_trace(start_a_name)
                end_r_hierarchy = self._get_hierarchy_trace(end_r_name)
                end_a_hierarchy = self._get_hierarchy_trace(end_a_name)

                # find first common parents
                res_common_parent = None
                for class_name in end_r_hierarchy:
                    if class_name in start_r_hierarchy:
                        res_common_parent = class_name
                        break

                act_common_parent = None
                for class_name in end_a_hierarchy:
                    if class_name in start_a_hierarchy:
                        act_common_parent = class_name
                        break

                if res_common_parent is None:
                    raise ValueError(
                        "For 'contains IF-THEN' constraint, resources need to share a common parent...these resources do not!"
                    )

                if act_common_parent is None:
                    raise ValueError(
                        "For 'contains IF-THEN' constraint, activities need to share a common parent...these activities do not!"
                    )

                # fill the params
                child_adjacency_matrix = self._get_child_adjacency_matrix()

                # determine which start instances are containers of which end instances
                end_r_start_r_map = self._create_resource_end_to_start_map(
                    child_adjacency_matrix, res_common_parent, start_r_name, end_r_name
                )
                end_a_start_a_map = self._create_activity_end_to_start_map(
                    child_adjacency_matrix, act_common_parent, start_a_name, end_a_name
                )

                # determine the possible allocations of the start and end instances
                start_alloc_list = self._determine_list_all_possible_allocations(start_r_name, start_a_name)
                end_alloc_list = self._determine_list_all_possible_allocations(end_r_name, end_a_name)

                # for each end alloc, use the maps to determine the possible end allocs
                for end_alloc in end_alloc_list:
                    end_r_inst_name = end_alloc[0]
                    end_a_inst_name = end_alloc[1]
                    start_r_name_list = end_r_start_r_map[end_r_inst_name]
                    start_a_name_list = end_a_start_a_map[end_a_inst_name]

                    containing_allocations[end_alloc] = []
                    for start_r_name in start_r_name_list:
                        for start_a_name in start_a_name_list:
                            if (start_r_name, start_a_name) in start_alloc_list:
                                if (start_r_name, start_a_name) not in containing_allocations[end_alloc]:
                                    containing_allocations[end_alloc].append((start_r_name, start_a_name))

        # convert all items in containing_allocations to ids
        for (key_r_name, key_a_name) in containing_allocations:
            key_r_id = self._res_name_to_id[key_r_name]
            key_a_id = self._act_name_to_id[key_a_name]
            r_a_arcs_for_contains.append((key_r_id, key_a_id))
            containing_allocations_id[(key_r_id, key_a_id)] = []
            for (r_name, a_name) in containing_allocations[(key_r_name, key_a_name)]:
                r_id = self._res_name_to_id[r_name]
                a_id = self._act_name_to_id[a_name]
                if (r_id, a_id) not in containing_allocations_id[(key_r_id, key_a_id)]:
                    containing_allocations_id[(key_r_id, key_a_id)].append((r_id, a_id))

        # no_reward allocation
        no_reward_allocation = {}
        for a_id in self._model.act_id_index.data():
            no_reward_allocation[a_id] = False

        for a_class in self._data["activityInstances"]:
            for a_inst in a_class["instanceTable"]:
                if a_inst["reward"] == 0:
                    a_id = self._act_name_to_id[a_inst["instanceName"]]
                    no_reward_allocation[a_id] = True

        # move them to model
        self._model.r_a_arcs_for_contains = Set(initialize=r_a_arcs_for_contains)

        self._model.containing_allocations = Param(self._model.r_a_arcs_for_contains, initialize=containing_allocations_id, within=Any)

        self._model.no_reward_allocation = Param(self._model.act_id_index, initialize=no_reward_allocation, within=Binary)

        # constraints
        self._model.if_contains_constraint = Constraint(self._model.r_a_arcs_for_contains, rule=if_contains_rule)

        self._model.if_contains_picked_constraint = Constraint(self._model.allocatable_act_id_index, rule=if_contains_picked)

    def __create_for_if_not_constraint(self):
        """
        if-not constraints occur when a allocation constraint is placed between two 'allocated to' links and the same resource exists in
        both of the 'allocated to'
        """
        log.info("CREATING ADDITIONAL COMPONENT: IF NOT Constraints")
        if_not_constraint_present = False
        for item in self._data["allocationConstraints"]:
            if item["allocationConstraintType"] == "IF-NOT":
                if_not_constraint_present = True
                break

        if not if_not_constraint_present:
            log.info("....NO IF-NOT constraints! cant make this component")
            return

        # indices
        r_a_arcs_for_not = []  # a list of all possible resource to activity allocations BUT
        #  only for allocations relevant to the not constraint

        # params
        not_allocations = {}  # a dict with keys = [resource_id, activity_id] and values = list
        #  of activity ids that the resource_id cannot be allocated to

        for item in self._data["allocationConstraints"]:
            if item["allocationConstraintType"] == "IF-NOT":
                # get the names out
                start_r_name = item["allocationStart"]["resourceClass"]
                start_a_name = item["allocationStart"]["activityClass"]
                end_r_name = item["allocationEnd"]["resourceClass"]
                end_a_name = item["allocationEnd"]["activityClass"]

                # start_r_name and end_r_name need to be the same or this wont work!!!
                if start_r_name != end_r_name:
                    raise ValueError("For IF-NOT, start resource name and end resource name have to be the same")

                r_name = start_r_name

                # create all ids, in case any ALLs occur in allocations
                all_r_ids = []
                all_a_ids = []
                all_start_a_ids = []
                all_end_a_ids = []

                res_class_inst = self._get_resource_class_instance(r_name)
                start_act_class_inst = self._get_activity_class_instance(start_a_name)
                end_act_class_inst = self._get_activity_class_instance(end_a_name)

                for i in start_act_class_inst["instanceTable"]:
                    all_start_a_ids.append(self._act_name_to_id[i["instanceName"]])

                for i in end_act_class_inst["instanceTable"]:
                    all_end_a_ids.append(self._act_name_to_id[i["instanceName"]])

                for i in res_class_inst["instanceTable"]:
                    all_r_ids.append(self._res_name_to_id[i["instanceName"]])

                # go through all individual instances of the allocation class instances
                #  to construct r_a_arcs_for_not
                for alloc_class_inst in self._data["allocationInstances"]:
                    res_class_name = alloc_class_inst["resourceClassName"]
                    act_class_name = alloc_class_inst["activityClassName"]
                    part_of_not_constraint = False

                    # check to ensure this is part of not constraint
                    if res_class_name == r_name and act_class_name == start_a_name:
                        part_of_not_constraint = True
                        all_a_ids = all_start_a_ids

                    elif res_class_name == r_name and act_class_name == end_a_name:
                        part_of_not_constraint = True
                        all_a_ids = all_end_a_ids

                    if part_of_not_constraint:
                        for alloc_inst in alloc_class_inst["instanceTable"]:
                            res_inst_name = alloc_inst["resourceInstanceName"]
                            act_inst_name = alloc_inst["activityInstanceName"]

                            # handle ALL-to-ALL, 1-to-ALL, and ALL-to-1
                            if res_inst_name != "ALL":
                                r_ids = [self._res_name_to_id[res_inst_name]]
                            else:
                                r_ids = all_r_ids

                            if act_inst_name != "ALL":
                                a_ids = [self._act_name_to_id[act_inst_name]]
                            else:
                                a_ids = all_a_ids

                            # create all res-to-act arcs
                            for r_id in r_ids:
                                for a_id in a_ids:
                                    if (r_id, a_id) not in r_a_arcs_for_not:
                                        r_a_arcs_for_not.append((r_id, a_id))

                        # create not_allocations
                        for (r_id, a_id) in r_a_arcs_for_not:
                            if a_id in all_start_a_ids:
                                if (r_id, a_id) in not_allocations:
                                    for end_a_id in all_end_a_ids:
                                        if end_a_id not in not_allocations[(r_id, a_id)]:
                                            not_allocations[(r_id, a_id)].append(end_a_id)
                                else:
                                    not_allocations[(r_id, a_id)] = all_end_a_ids

                            elif a_id in all_end_a_ids:
                                if (r_id, a_id) in not_allocations:
                                    for start_a_id in all_start_a_ids:
                                        if start_a_id not in not_allocations[(r_id, a_id)]:
                                            not_allocations[(r_id, a_id)].append(start_a_id)
                                else:
                                    not_allocations[(r_id, a_id)] = all_start_a_ids

        # move them to model
        self._model.r_a_arcs_for_not = Set(initialize=r_a_arcs_for_not)

        self._model.not_allocations = Param(self._model.r_a_arcs_for_not, initialize=not_allocations, within=Any)

        # constraints
        self._model.if_not_limit_constraint = Constraint(self._model.r_a_arcs_for_not, rule=if_not_limit_rule)

    def __create_for_contained_reward(self):
        """
        Contained rewards occur when an activity contains another activity and the containing activity has a reward
        """
        log.info("CREATING ADDITIONAL COMPONENT: Contained Reward")
        if len(self._data["containsInstances"]) == 0:
            log.info("....NO CONTAINS RELATIONSHIPS! cant make this component")
            return

        # indices
        container_act_id_index = []  # the ids for all activities that are not allocated and that contain other activities

        # params
        contained_activities = {}  # a dict with keys= activity id and values = list of activity ids that the key contains

        for contains_arrow in self._data["containsInstances"]:
            if contains_arrow["parentType"] != "activity":
                log.info(
                    "...Contains Instance from {} to {} is not an activity contains".format(
                        contains_arrow["parentClassName"], contains_arrow["childClassName"]
                    )
                )
                continue

            # if parent is allocated to a resource...this reward does not apply
            if self._is_activity_allocated(contains_arrow["parentClassName"]):
                log.info("...Contains instance parent class is allocated, so cannot be apart of contains reward")
                continue

            for instance in contains_arrow["instanceTable"]:
                parent_act_id = self._act_name_to_id[instance["parentInstanceName"]]
                child_act_id = self._act_name_to_id[instance["childInstanceName"]]

                if parent_act_id not in container_act_id_index:
                    container_act_id_index.append(parent_act_id)

                if parent_act_id not in contained_activities:
                    contained_activities[parent_act_id] = []

                if child_act_id not in contained_activities[parent_act_id]:
                    contained_activities[parent_act_id].append(child_act_id)

        num_contained_activities = {}  # a dict with keys = activity id and value equal to the total
        for a_id, contained_act_list in contained_activities.items():
            num_contained_activities[a_id] = len(contained_act_list)

        # move them to model
        self._model.container_act_id_index = Set(initialize=container_act_id_index)

        self._model.contained_activities = Param(self._model.container_act_id_index, initialize=contained_activities, within=Any)

        self._model.num_contained_activities = Param(
            self._model.container_act_id_index, initialize=num_contained_activities, within=NonNegativeReals
        )

        # constraints
        self._model.act_picked_contains_constraint = Constraint(self._model.container_act_id_index, rule=act_picked_contains_rule)

    def __create_indices(self):
        log.info("Creating indices...")

        # allocation pair id index...every possible allocation gets a unique number
        self._model.pair_id_index = Set(initialize=list(range(0, len(self._data["allocationInstances"]))), ordered=True)
        self._pair_name_to_id = {self._get_alloc_inst_name(p): i for (i, p) in enumerate(self._data["allocationInstances"])}
        self._pair_id_to_name = {i: self._get_alloc_inst_name(p) for (i, p) in enumerate(self._data["allocationInstances"])}

        # resource id index....every resource instance gets a unique number
        max_res_id = 0
        self._res_name_to_id = {}
        self._res_name_to_class = {}
        self._res_id_to_name = {}
        for ri in self._data["resourceInstances"]:
            class_name = ri["className"]
            for it in ri["instanceTable"]:
                self._res_name_to_id[it["instanceName"]] = max_res_id
                self._res_name_to_class[it["instanceName"]] = class_name
                self._res_id_to_name[max_res_id] = it["instanceName"]
                max_res_id += 1
        self._model.res_id_index = Set(initialize=list(range(0, max_res_id)), ordered=True)

        # activity id index....every activity instance gets a unique number
        max_act_id = 0
        self._act_name_to_id = {}
        self._act_name_to_class = {}
        self._act_id_to_name = {}
        for ai in self._data["activityInstances"]:
            class_name = ai["className"]
            for it in ai["instanceTable"]:
                self._act_name_to_id[it["instanceName"]] = max_act_id
                self._act_name_to_class[it["instanceName"]] = class_name
                self._act_id_to_name[max_act_id] = it["instanceName"]
                max_act_id += 1
        self._model.act_id_index = Set(initialize=list(range(0, max_act_id)), ordered=True)

        # allocate-able activity id index (an activity without a cost cannot be allocated?)
        allocatable_act = []
        for ai in self._data["activityInstances"]:
            for it in ai["instanceTable"]:
                if it["cost"]:  # if cost is not empty
                    allocatable_act.append(self._act_name_to_id[it["instanceName"]])
        self._model.allocatable_act_id_index = Set(initialize=allocatable_act)

        # budget-cost index...every unique budget-cost pair get a unique number
        max_budget_id = 0
        self._budget_name_to_id = {}
        self._budget_id_to_name = {}
        for rc in self._data["resourceClasses"]:
            for b in rc["budgets"]:
                if b not in self._budget_name_to_id:
                    self._budget_name_to_id[b] = max_budget_id
                    self._budget_id_to_name[max_budget_id] = b
                    max_budget_id += 1
        self._max_budget_id = max_budget_id
        self._model.budget_index = Set(initialize=list(range(0, max_budget_id)), ordered=True)

        # force set
        # TODO

        # forbid set
        # TODO
        log.debug("   res-act pair indices..." + str(len(self._model.pair_id_index.data())))
        log.debug("     " + str(self._model.pair_id_index.data()))
        log.debug("   resource indices..." + str(len(self._model.res_id_index.data())))
        log.debug("     " + str(self._model.res_id_index.data()))
        log.debug("   activity indices..." + str(len(self._model.act_id_index.data())))
        log.debug("     " + str(self._model.act_id_index.data()))
        log.debug("   allocatable activity indices..." + str(len(self._model.allocatable_act_id_index.data())))
        log.debug("     " + str(self._model.allocatable_act_id_index.data()))
        log.debug("   budget indices..." + str(len(self._model.budget_index.data())))
        log.debug("     " + str(self._model.budget_index.data()))

    def __create_relationships(self):
        log.info("Creating relationships...")
        r_a_arcs = []  # list of all possible resource to activity allocations
        r_a_b_arcs = []  # list of all possible resource to activity allocations for each relevant budget
        r_b_arcs = []  # list of all possible resource to budget class
        a_b_arcs = []  # list of all possible activities to budget(cost) class
        p_a_arcs = []  # list of all possible res-act pairs to activities in that pair

        poss_alloc = {}  # dict of r_id keys with list of a_ids as value
        rev_alloc = {}  # dict of (p_id, a_id) keys with list of r_ids as value
        num_budgets = {}  # dict of a_id keys with int number of different costs for that activity
        incoming = {}  # a dict of a_id keys with int number of pairs into that activity

        num_incoming_pairs = {}
        for alloc_class_inst in self._data["allocationInstances"]:
            act_class_name = alloc_class_inst["activityClassName"]
            if act_class_name in num_incoming_pairs:
                num_incoming_pairs[act_class_name] += 1
            else:
                num_incoming_pairs[act_class_name] = 1

        for alloc_class_inst in self._data["allocationInstances"]:
            alloc_name = self._get_alloc_inst_name(alloc_class_inst)
            p_id = self._pair_name_to_id[alloc_name]

            num_incoming = num_incoming_pairs[alloc_class_inst["activityClassName"]]

            # get all act ids and res ids for later, in case user wants ALL
            act_class_inst = self._get_activity_class_instance(alloc_class_inst["activityClassName"])
            act_num_budgets = len(act_class_inst["instanceTable"][0]["cost"])  # use the first...should be same for all
            all_a_ids = []
            for i in act_class_inst["instanceTable"]:
                all_a_ids.append(self._act_name_to_id[i["instanceName"]])
            res_class_inst = self._get_resource_class_instance(alloc_class_inst["resourceClassName"])
            all_r_ids = []
            for i in res_class_inst["instanceTable"]:
                all_r_ids.append(self._res_name_to_id[i["instanceName"]])

            # get all corresponding budgets between the resource class and activity class
            all_budget_ids = []
            for b in res_class_inst["instanceTable"][0]["budget"]:  # use the first one...should be same for all
                all_budget_ids.append(self._budget_name_to_id[b])

            # go through all individual instances of the allocation class instance
            for alloc_inst in alloc_class_inst["instanceTable"]:
                res_inst_name = alloc_inst["resourceInstanceName"]
                act_inst_name = alloc_inst["activityInstanceName"]

                # handle ALL-to-ALL, 1-to-ALL, and ALL-to-1
                if res_inst_name != "ALL":
                    r_ids = [self._res_name_to_id[res_inst_name]]
                else:
                    r_ids = all_r_ids

                if act_inst_name != "ALL":
                    a_ids = [self._act_name_to_id[act_inst_name]]
                else:
                    a_ids = all_a_ids

                # create ...
                for a_id in a_ids:

                    # create all possible activity-budget(cost) arcs
                    for b_id in all_budget_ids:
                        if (a_id, b_id) not in a_b_arcs:
                            a_b_arcs.append((a_id, b_id))

                    # create reverse allocation from all possible combinations
                    if (p_id, a_id) not in rev_alloc:
                        rev_alloc[p_id, a_id] = r_ids
                    else:
                        for r_id in r_ids:
                            if r_id not in rev_alloc[p_id, a_id]:
                                rev_alloc[p_id, a_id].append(r_id)

                    # create all possible pair-activity arcs
                    if (p_id, a_id) not in p_a_arcs:
                        p_a_arcs.append((p_id, a_id))

                    # create num_budgets
                    if a_id not in num_budgets:
                        num_budgets[a_id] = act_num_budgets

                    # create incoming
                    if a_id not in incoming:
                        incoming[a_id] = num_incoming

                # create ...
                for r_id in r_ids:

                    # create all possible resource-budget arcs
                    for b_id in all_budget_ids:
                        if (r_id, b_id) not in r_b_arcs:
                            r_b_arcs.append((r_id, b_id))

                    # create possible allocations from all possible combinations,
                    if r_id not in poss_alloc:
                        poss_alloc[r_id] = a_ids
                    else:
                        for a_id in a_ids:
                            if a_id not in poss_alloc[r_id]:
                                poss_alloc[r_id].append(a_id)

                    # create all res-to-act arcs and res-act-budget arcs
                    for a_id in a_ids:
                        if (r_id, a_id) not in r_a_arcs:
                            r_a_arcs.append((r_id, a_id))

                        for b_id in all_budget_ids:
                            if (r_id, a_id, b_id) not in r_a_b_arcs:
                                r_a_b_arcs.append((r_id, a_id, b_id))

        log.debug("    Resource Activity Arcs..." + str(len(r_a_arcs)))
        log.debug("     " + str(r_a_arcs))
        log.debug("    Resource Activity Budget Arcs..." + str(len(r_a_b_arcs)))
        log.debug("     " + str(r_a_b_arcs))
        log.debug("    Resource Budget Arcs..." + str(len(r_b_arcs)))
        log.debug("     " + str(r_b_arcs))
        log.debug("    Activity Budget Arcs..." + str(len(a_b_arcs)))
        log.debug("     " + str(a_b_arcs))
        log.debug("    Pair Activity Arcs..." + str(len(p_a_arcs)))
        log.debug("     " + str(p_a_arcs))
        log.debug("    Possible Allocations..." + str(len(poss_alloc)))
        log.debug("     " + str(poss_alloc))
        log.debug("    Reverse Allocations..." + str(len(rev_alloc)))
        log.debug("     " + str(rev_alloc))
        log.debug("    Number of Budgets..." + str(len(num_budgets)))
        log.debug("     " + str(num_budgets))
        log.debug("    Number of Incoming Pairs..." + str(len(incoming)))
        log.debug("     " + str(incoming))

        # resource-activity arcs
        self._model.r_a_arcs = Set(within=self._model.res_id_index * self._model.act_id_index, initialize=r_a_arcs)

        # resource-activity-budget arcs
        self._model.r_a_b_arcs = Set(
            within=self._model.res_id_index * self._model.act_id_index * self._model.budget_index, initialize=r_a_b_arcs
        )

        # resource-budget arcs
        self._model.r_b_arcs = Set(within=self._model.res_id_index * self._model.budget_index, initialize=r_b_arcs)

        # activity-budget(cost) arcs
        self._model.a_b_arcs = Set(within=self._model.act_id_index * self._model.budget_index, initialize=a_b_arcs)

        # res-act pair to activity arcs
        self._model.p_a_arcs = Set(within=self._model.pair_id_index * self._model.act_id_index, initialize=p_a_arcs)

        # possible allocations
        self._model.possible_allocations = Param(self._model.res_id_index, initialize=poss_alloc, within=Any)

        # reverse allocations
        self._model.reverse_allocations = Param(self._model.pair_id_index * self._model.act_id_index, initialize=rev_alloc, within=Any)

        # number of budgets
        self._model.num_budgets = Param(self._model.act_id_index, initialize=num_budgets, within=NonNegativeReals)

        # number of incoming allocation paths into an activity
        self._model.num_incoming_pairs = Param(self._model.act_id_index, initialize=incoming, within=NonNegativeReals)

        total_rev_alloc = {}
        for (p_id, a_id) in rev_alloc:
            if a_id not in total_rev_alloc:
                total_rev_alloc[a_id] = rev_alloc[(p_id, a_id)].copy()
            else:
                r_ids = rev_alloc[(p_id, a_id)].copy()
                for r_id in r_ids:
                    if r_id not in total_rev_alloc[a_id]:
                        total_rev_alloc[a_id].append(r_id)

        log.debug("Creating total reverse allocations...")
        log.debug(total_rev_alloc)
        self._model.total_reverse_allocations = Param(self._model.act_id_index, initialize=total_rev_alloc, within=Any)

    def __create_params_variables(self):
        log.info("Creating variables and parameters...")

        # parameters that are needed to optimize
        act_reward = {}  # TODO - should be dict of a_id and reward value
        act_costs = {}  # TODO - should be a dict of (a_id, b_id) and list of cost values
        res_budgets = {}  # TODO - should be a dict of (r_id, b_id) and list of budget values

        # rewards and costs
        for act_class_instance in self._data["activityInstances"]:
            for act_instance in act_class_instance["instanceTable"]:
                a_id = self._act_name_to_id[act_instance["instanceName"]]
                act_reward[a_id] = act_instance["reward"]

                for c_name in act_instance["cost"]:
                    b_id = self._budget_name_to_id[c_name]
                    act_costs[(a_id, b_id)] = act_instance["cost"][c_name]

        # budgets
        for res_class_instance in self._data["resourceInstances"]:
            for res_instance in res_class_instance["instanceTable"]:
                r_id = self._res_name_to_id[res_instance["instanceName"]]

                for b_name in res_instance["budget"]:
                    b_id = self._budget_name_to_id[b_name]
                    res_budgets[(r_id, b_id)] = res_instance["budget"][b_name]

        log.debug("   reward Param..." + str(len(act_reward)))
        log.debug("     " + str(act_reward))
        log.debug("   required_amount Param..." + str(len(act_costs)))
        log.debug("     " + str(act_costs))
        log.debug("   available_amount Param..." + str(len(res_budgets)))
        log.debug("     " + str(res_budgets))

        total_costs = {}
        for (a_id, b_id) in act_costs:
            if a_id not in total_costs:
                total_costs[a_id] = act_costs[(a_id, b_id)]
            else:
                total_costs[a_id] += act_costs[(a_id, b_id)]

        # reward parameter
        self._model.reward = Param(self._model.act_id_index, initialize=act_reward, within=Any)

        # required amount parameter
        self._model.required_amount = Param(self._model.a_b_arcs, initialize=act_costs, within=Any)

        # available amount parameter
        self._model.available_amount = Param(self._model.r_b_arcs, initialize=res_budgets, within=Any)

        # Variables that will be set while the model is being solved:
        # 1) indicates which resource instance is allocated to which activity instances
        self._model.ALLOCATED = Var(self._model.r_a_arcs, domain=Binary, initialize=0)

        # 2) indicates how much budget is allocated from resources to activities
        self._model.ALLOCATED_AMT = Var(self._model.r_a_b_arcs, domain=NonNegativeReals, initialize=0)

        # 3)
        self._model.PICKED = Var(self._model.act_id_index, domain=Binary, initialize=0)

    def __create_constraints(self):
        log.info("Creating constraints...")
        self._model.required_amount_constraint = Constraint(self._model.r_a_b_arcs, rule=required_amount_rule)
        self._model.act_picked_constraint = Constraint(self._model.allocatable_act_id_index, rule=act_picked_rule)
        self._model.available_amount_constraint = Constraint(self._model.r_b_arcs, rule=available_amount_rule)
        self._model.allocated_limit_constraint = Constraint(self._model.p_a_arcs, rule=allocated_limit_rule)

    def __create_objective(self):
        log.info("Creating objective function...")
        self._model.objective = Objective(rule=objective_rule, sense=maximize)
        # TODO should we have a condition to minimize as well

    def fill_output(self, output_class):
        """
        Return the output of the model after it has been solved by instantiating an object of the output class.

        This method must interrogate the model and produce an output object.  Since models may differ,
        this method must be implemented in the subclass

        :param output_class: the OutputBase or subclass of output base
        :return output: an instance of the output_class
        """
        output = output_class()

        # start with a dict skeleton with objective value filled in
        result = {
            "objective_value": self._model.objective.expr(),
            "full_trace": {"resource": [], "activity": [], "budget_used": [], "value": [], "selected": [], "picked": [], "allocated": []},
            "allocated_amt": {},
            "per_resource_score": {},
            "per_resource_budget_used": {},
        }

        # calculate allocated amount
        for (r_id, a_id, b_id) in self._model.r_a_b_arcs:
            if self._model.ALLOCATED[r_id, a_id].value and self._model.PICKED[a_id].value:
                res_name = self._res_id_to_name[r_id]
                act_name = self._act_id_to_name[a_id]
                budget_name = self._budget_id_to_name[b_id]
                if res_name in result["allocated_amt"]:
                    if act_name in result["allocated_amt"][res_name]:
                        if budget_name in result["allocated_amt"][res_name][act_name]:
                            log.warning("Attempt to overwrite a budget that already existed")
                        else:
                            result["allocated_amt"][res_name][act_name][budget_name] = self._model.ALLOCATED_AMT[r_id, a_id, b_id].value
                    else:
                        result["allocated_amt"][res_name][act_name] = {}
                        result["allocated_amt"][res_name][act_name][budget_name] = self._model.ALLOCATED_AMT[r_id, a_id, b_id].value
                else:
                    result["allocated_amt"][res_name] = {}
                    result["allocated_amt"][res_name][act_name] = {}
                    result["allocated_amt"][res_name][act_name][budget_name] = self._model.ALLOCATED_AMT[r_id, a_id, b_id].value

        # calculate per_resource amount - from allocated amount
        for res_name in result["allocated_amt"]:
            result["per_resource_budget_used"][res_name] = {}
            for act_name in result["allocated_amt"][res_name]:
                for budget_name in result["allocated_amt"][res_name][act_name]:
                    if budget_name not in result["per_resource_budget_used"][res_name]:
                        result["per_resource_budget_used"][res_name][budget_name] = result["allocated_amt"][res_name][act_name][
                            budget_name
                        ]
                    else:
                        result["per_resource_budget_used"][res_name][budget_name] += result["allocated_amt"][res_name][act_name][
                            budget_name
                        ]

        #  3) allocations - the mapping of resources to activities
        allocations = {}

        for (r_id, a_id) in self._model.r_a_arcs:
            res_name = self._res_id_to_name[r_id]
            act_name = self._act_id_to_name[a_id]
            act_value = self._get_activity_instance(self._act_name_to_class[act_name], act_name)["reward"]
            act_selected = 0
            budget_used = [0] * self._max_budget_id

            if self._model.ALLOCATED[r_id, a_id].value and self._model.PICKED[a_id].value:
                act_selected = 1

                # handle allocations
                if res_name in allocations:
                    allocations[res_name].append(act_name)
                else:
                    allocations[res_name] = [act_name]

                # handle resource score
                if res_name in result["per_resource_score"]:
                    result["per_resource_score"][res_name] += act_value
                else:
                    result["per_resource_score"][res_name] = act_value

                # handle budget used
                for b_id in range(0, self._max_budget_id):
                    if (r_id, a_id, b_id) in self._model.r_a_b_arcs:
                        budget_used[b_id] = self._model.ALLOCATED_AMT[(r_id, a_id, b_id)].value

            # handle full_trace
            result["full_trace"]["resource"].append(res_name)
            result["full_trace"]["activity"].append(act_name)
            result["full_trace"]["budget_used"].append(budget_used)
            result["full_trace"]["value"].append(act_value)
            result["full_trace"]["selected"].append(act_selected)
            result["full_trace"]["picked"].append(self._model.PICKED[a_id].value)
            result["full_trace"]["allocated"].append(self._model.ALLOCATED[(r_id, a_id)].value)

        result["allocations"] = allocations
        output.result = result

        return output

    # HELPER FUNCTIONS
    def _get_alloc_inst_name(self, alloc_inst):
        return alloc_inst["resourceClassName"] + "_" + alloc_inst["activityClassName"]

    def _get_alloc_inst(self, r_class_name, a_class_name):
        alloc_inst = None
        for ai in self._data["allocationInstances"]:
            if ai["resourceClassName"] == r_class_name and ai["activityClassName"] == a_class_name:
                alloc_inst = ai
                return alloc_inst

        return alloc_inst

    def _get_activity_class_instance(self, name):
        for i in self._data["activityInstances"]:
            if i["className"] == name:
                return i
        return None

    def _get_activity_instance(self, class_name, instance_name):
        act_class = self._get_activity_class_instance(class_name)
        for i in act_class["instanceTable"]:
            if i["instanceName"] == instance_name:
                return i
        return None

    def _get_resource_class_instance(self, name):
        for i in self._data["resourceInstances"]:
            if i["className"] == name:
                return i
        return None

    def _is_activity_allocated(self, name):
        allocated_classes = []
        for r in self._data["resourceClasses"]:
            for a in r["canBeAllocatedToClasses"]:
                if a not in allocated_classes:
                    allocated_classes.append(a)
        return name in allocated_classes

    def _get_hierarchy_trace(self, class_name):
        """
        breadth first search through the contains instances class hierarchy
        """

        q = deque()
        q.append(class_name)
        trace = []

        while q:
            v = q.popleft()
            trace.append(v)

            for ci in self._data["containsInstances"]:
                if ci["childClassName"] == v:
                    q.append(ci["parentClassName"])

        return trace

    def _get_all_resource_instance_names(self, name):

        rc = self._get_resource_class_instance(name)
        rin = []
        for i in rc["instanceTable"]:
            rin.append(i["instanceName"])
        return rin

    def _get_all_activity_instance_names(self, name):

        rc = self._get_activity_class_instance(name)
        rin = []
        for i in rc["instanceTable"]:
            rin.append(i["instanceName"])
        return rin

    def _get_child_adjacency_matrix(self):
        # starting with parent class work way down through all
        adjacency_matrix = {}
        for ci in self._data["containsInstances"]:
            for i in ci["instanceTable"]:
                if i["parentInstanceName"] in adjacency_matrix:
                    adjacency_matrix[i["parentInstanceName"]].append(i["childInstanceName"])
                else:
                    adjacency_matrix[i["parentInstanceName"]] = [i["childInstanceName"]]
        return adjacency_matrix

    def _depth_search_for_children(self, adjacency_matrix, parent_inst, child_inst_list):
        stack = [parent_inst]
        children_of_parent_inst = []

        while stack:
            vertex = stack.pop()
            if vertex in child_inst_list:
                if vertex not in children_of_parent_inst:
                    children_of_parent_inst.append(vertex)

            if vertex in adjacency_matrix:
                for neighbor in adjacency_matrix[vertex]:
                    stack.append(neighbor)

        return children_of_parent_inst

    def _create_resource_start_to_end_map(self, child_adjacency_matrix, res_common_parent, start_r_name, end_r_name):

        start_instances = self._get_all_resource_instance_names(start_r_name)
        end_instances = self._get_all_resource_instance_names(end_r_name)
        parent_instances = self._get_all_resource_instance_names(res_common_parent)

        start_end_map = {}
        for parent_inst in parent_instances:

            # from the common parent, determine which start_r and end_r children descend from that parent
            start_child_inst_list = self._depth_search_for_children(child_adjacency_matrix, parent_inst, start_instances)
            end_child_inst_list = self._depth_search_for_children(child_adjacency_matrix, parent_inst, end_instances)

            # assemble a pseudo parent-child map
            for start_inst in start_child_inst_list:
                start_end_map[start_inst] = []
                for end_inst in end_child_inst_list:
                    start_end_map[start_inst].append(end_inst)

        return start_end_map

    def _create_resource_end_to_start_map(self, child_adjacency_matrix, res_common_parent, start_r_name, end_r_name):

        start_instances = self._get_all_resource_instance_names(start_r_name)
        end_instances = self._get_all_resource_instance_names(end_r_name)
        parent_instances = self._get_all_resource_instance_names(res_common_parent)

        end_start_map = {}
        for parent_inst in parent_instances:

            # from the common parent, determine which start_r and end_r children descend from that parent
            start_child_inst_list = self._depth_search_for_children(child_adjacency_matrix, parent_inst, start_instances)
            end_child_inst_list = self._depth_search_for_children(child_adjacency_matrix, parent_inst, end_instances)

            # assemble a pseudo parent-child map
            for end_inst in end_child_inst_list:
                end_start_map[end_inst] = []
                for start_inst in start_child_inst_list:
                    end_start_map[end_inst].append(start_inst)

        return end_start_map

    def _create_activity_start_to_end_map(self, child_adjacency_matrix, act_common_parent, start_a_name, end_a_name):

        start_instances = self._get_all_activity_instance_names(start_a_name)
        end_instances = self._get_all_activity_instance_names(end_a_name)
        parent_instances = self._get_all_activity_instance_names(act_common_parent)

        start_end_map = {}
        for parent_inst in parent_instances:

            # from the common parent, determine which start_r and end_r children descend from that parent
            start_child_inst_list = self._depth_search_for_children(child_adjacency_matrix, parent_inst, start_instances)
            end_child_inst_list = self._depth_search_for_children(child_adjacency_matrix, parent_inst, end_instances)

            # assemble a pseudo parent-child map
            for start_inst in start_child_inst_list:
                start_end_map[start_inst] = []
                for end_inst in end_child_inst_list:
                    start_end_map[start_inst].append(end_inst)

        return start_end_map

    def _create_activity_end_to_start_map(self, child_adjacency_matrix, act_common_parent, start_a_name, end_a_name):

        start_instances = self._get_all_activity_instance_names(start_a_name)
        end_instances = self._get_all_activity_instance_names(end_a_name)
        parent_instances = self._get_all_activity_instance_names(act_common_parent)

        end_start_map = {}
        for parent_inst in parent_instances:

            # from the common parent, determine which start_r and end_r children descend from that parent
            start_child_inst_list = self._depth_search_for_children(child_adjacency_matrix, parent_inst, start_instances)
            end_child_inst_list = self._depth_search_for_children(child_adjacency_matrix, parent_inst, end_instances)

            # assemble a pseudo parent-child map
            for end_inst in end_child_inst_list:
                end_start_map[end_inst] = []
                for start_inst in start_child_inst_list:
                    end_start_map[end_inst].append(start_inst)

        return end_start_map

    def _determine_list_all_possible_allocations(self, r_name, a_name):

        all_r_instances = self._get_all_resource_instance_names(r_name)
        all_a_instances = self._get_all_activity_instance_names(a_name)

        alloc_inst = self._get_alloc_inst(r_name, a_name)
        alloc_list = []
        for inst in alloc_inst["instanceTable"]:

            if inst["resourceInstanceName"] == "ALL":
                res_inst_list = all_r_instances
            else:
                res_inst_list = [inst["resourceInstanceName"]]

            if inst["activityInstanceName"] == "ALL":
                act_inst_list = all_a_instances
            else:
                act_inst_list = [inst["activityInstanceName"]]

            for res_name in res_inst_list:
                for act_name in act_inst_list:
                    if (res_name, act_name) not in alloc_list:
                        alloc_list.append((res_name, act_name))

        return alloc_list
