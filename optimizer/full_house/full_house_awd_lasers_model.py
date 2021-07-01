"""
This needs to contain all the pyomo junk and be extension of base_model

s = ship = resource container

b = battery = child resource

t = target = VIP = child activity

m = laser = parent resource

o = orientation = parent activity
"""
import logging
from collections import defaultdict

from dm3k.data_access_layer import db_helper
from dm3k.slim_optimizer.full_house.full_house_input import FullHouseInput
from dm3k.slim_optimizer.slim_optimizer_base import ModelBase
from pyomo.environ import Any, Binary, ConcreteModel, Constraint, NonNegativeReals, Objective, Param, Set, Var, maximize

log = logging.getLogger(__name__)


# -------------------------------------------------------------------------------
# OBJECTIVES
# -------------------------------------------------------------------------------
def objective_rule(model):
    return sum(model.ENGAGE[b, t] * model.targetValues[t] for (b, t) in model.batteryTargetArcs)


# -------------------------------------------------------------------------------
# CONSTRAINTS
# -------------------------------------------------------------------------------


def avail_power_rule(model, b):
    """
    Each battery has a limit to available power

    :param ConcreteModel model: the active pyomo model being optimized
    :param int b: battery
    :return: boolean indicating whether that battery can supply the power for all allocated targets
    """
    return sum(model.POWER[b, t] for (i, t) in model.batteryTargetArcs if i == b) <= model.availablePower[b]


def required_power_rule(model, b, t):
    """
    Each target requires a certain amount of power, and a target is not engaged unless that power is provided

    :param ConcreteModel model:
    :param int b: battery
    :param int t: target
    :return: boolean indicating whether that battery is supplying power to that target
    """
    return model.POWER[b, t] == model.requiredPower[b, t] * model.ENGAGE[b, t]


def engage_limit_rule(model, t):
    """
    Each target may not be engaged more than once

    :param ConcreteModel model:
    :param int t: target
    :return: boolean indicating whether that target is engaged at most once
    """
    return sum(model.ENGAGE[b, t] for b in model.targetBatteries[t]) <= 1


def orientation_limit_rule(model, m):
    """
    Each laser must be in exactly one orientation

    :param ConcreteModel model:
    :param int m: laser
    :return: boolean indicating whether that laser has selected exactly one orientation
    """
    # Ignore this constraint if this laser isn't in laserOrientationArcs
    try:
        return sum(model.ORIENT[m, o] for (i, o) in model.laserOrientationArcs if i == m) == 1
    except EnvironmentError:
        return Constraint.Skip


def link_parent_to_child_rule(model, b, t):
    """
    A child resource can only be allocated to a child activity if a parent resource in the same resource container
    is allocated to a parent activity which is a direct parent of the child activity

    :param ConcreteModel model:
    :param int b: battery
    :param int t: target
    :return: boolean indicating whether there is at least one laser on the same ship that is pointed at an orientation
        that allows for that battery to take out that target
    """
    return model.ENGAGE[b, t] <= sum(
        model.ORIENT[m, o] for m in model.batteryLasers[b] for o in model.targetOrientations[t] if (m, o) in model.laserOrientationArcs
    )


def force_rule(model, t):
    """
    Each target in force list must be engaged

    :param ConcreteModel model:
    :param int t: target
    :return: boolean indicating whether that target is engaged by a battery
    """
    return sum(model.ENGAGE[b, t] for b in model.targetBatteries[t]) == 1


def forbid_rule(model, t):
    """
    Each target in forbid list must not be engaged

    :param ConcreteModel model:
    :param int t: target
    :return: boolean indicating whether that target is *not* engaged by a battery
    """
    return sum(model.ENGAGE[b, t] for b in model.targetBatteries[t]) == 0


class FullHouseAWDLasersModel(ModelBase):
    def __init__(self):
        super().__init__()
        self._data = {}

    def can_solve(self, input_instance):
        """
        In the event the system can leverage multiple models, this function is used to determine if this model
        can solve the input.

        :param FullHouseInput input_instance: a instance of the InputBase class
        :return: Boolean, True = this model can solve this input.  False =
            something about input cannot be solved by model
        """
        # the FullHouseAWDLasersModel can solve any input in the form of the FullHouseInput class
        if isinstance(input_instance, FullHouseInput):
            # where the parent resource amount and parent child amount are both all 1s
            data = input_instance.to_data()
            for pr_name in data["avail_parent_amt"]:
                amt = data["avail_parent_amt"][pr_name]
                if not amt == 1:
                    return False

            for pr_name, pa_name in data["req_parent_amt"]:
                amt = data["req_parent_amt"][pr_name, pa_name]
                if not amt == 1:
                    return False
            return True
        else:
            return False

    def build(self, data):
        """
        Build the pyomo model in self._model

        :param dict data: a dictionary containing all necessary data for the model
        :return: None

        **data must be a dictionary with the following keys and values:**

        parent_resources
                    a list containing all the parent resource names
        child_resources
                     a list containing all the child resource names
        parent_activities
                   a list containing all the parent activity names
        child_activities
                    a list containing all the child activity names
        avail_parent_amt
                    a dict of the total budget for each parent resource: keys are parent resource names, values are float amounts
        avail_child_amt
                     a dict of the total budget for each child resource: keys are child resource names, values are float amounts
        req_parent_amt
                     a dict of the required cost (amount of budget) for a parent resource to select a
                     parent activity. keys are tuples (prn,pan) where prn is the parent resource name
                     and pan is the parent activity name, values are float amounts
        req_child_amt
                        a dict of the required cost (amount of budget) for a child resource to select a
                        child activity. keys are tuples (crn,can) where crn is the child resource name
                        and can is the child activity name, values are float amounts
        child_score
                         a dict of the float value of each child activity
                         keys are child activity names, values are float amounts
        force_list
                          a list of child activity names that are to be selected
        forbid_list
                         a list of child activity names that are NOT to be selected
        parent_possible_allocations
                        a dict containing the list of possible parent activity allocations for each parent
                        resource.  keys are parent resource names and values are lists of parent activity names

        child_possible_allocations
                        a dict containing the list of possible child activity allocations for each child
                        resource.  keys are child resource names and values are lists of child activity names

        resource_families
                     a dict containing the parent resources and child resources for each resource
                     container.  keys are resource container names and values are dicts with 2 keys
                     'parent_resources' (referencing the list of parent resources under this resource
                     container) and 'child_resources' (referencing the list of child resources under
                     this resource container)
        activity_children
                    a dict containing the child activities of each parent activity.  keys are parent
                    activity names, values are list of child activity names for that parent


        """
        self._data = data  # store this for filling output later
        self.__initialize_model()
        self.__set_relationships()
        self.__create_vars_params()
        self.__create_constraints()

    def __initialize_model(self):
        data = self._data
        log.info("Building Pyomo model...")
        self._model = ConcreteModel()

        log.info("Creating indices...")
        # Index on each ship
        self._model.s = Set(initialize=list(range(0, len(data["resource_families"]))), ordered=True)
        self._rev_rc = {name: i for (i, name) in enumerate(data["resource_families"])}

        # Index on each battery
        self._model.b = Set(initialize=list(range(0, len(data["child_resources"]))), ordered=True)
        self._rev_cr = {name: i for (i, name) in enumerate(data["child_resources"])}

        # Index on each VIP target
        self._model.t = Set(initialize=list(range(0, len(data["child_activities"]))), ordered=True)
        self._rev_ca = {name: i for (i, name) in enumerate(data["child_activities"])}

        # Index on each laser
        self._model.m = Set(initialize=list(range(0, len(data["parent_resources"]))), ordered=True)
        self._rev_pr = {name: i for (i, name) in enumerate(data["parent_resources"])}

        # Index on each available orientation
        self._model.o = Set(initialize=list(range(0, len(data["parent_activities"]))), ordered=True)
        self._rev_pa = {name: i for (i, name) in enumerate(data["parent_activities"])}

        # Combinations are not enabled, but the below could help build those once they are
        """
        # Index on each penalized combination
        num_combinations = 0  # placeholder since input doesnt cover this yet
        self._model.c = Set(initialize=list(range(0, num_combinations)), ordered=True)

        # Set of all the combinations (which are themselves sets)
        self._model.cList = Set(self._model.c)

        combo_list = []  # placeholder since input doesnt cover this yet
        for c in self._model.c:  # Populate each subset of combinations
            for t in combo_list[c]:
                self._model.cList[c].add(t)
        """

        # force set
        force_index = []
        for name in data["force_list"]:
            force_index.append(self._rev_ca[name])
        self._model.force = Set(initialize=force_index, ordered=True)

        # forbid set
        forbid_index = []
        for name in data["forbid_list"]:
            forbid_index.append(self._rev_ca[name])
        self._model.forbid = Set(initialize=forbid_index, ordered=True)

    def __set_relationships(self):
        data = self._data
        log.info("Creating relationships...")

        pr_pa_ca_arcs = []
        pr_pa_arcs = []

        for pr_name, pa_names in data["parent_possible_allocations"].items():
            pr = self._rev_pr[pr_name]
            for pa_name in pa_names:
                pa = self._rev_pa[pa_name]
                pr_pa_arcs.append((pr, pa))
                for ca_name in data["activity_children"][pa_name]:
                    ca = self._rev_ca[ca_name]
                    pr_pa_ca_arcs.append((pr, pa, ca))

        laserOrientationArcs = pr_pa_arcs
        targetBatteries = {t: set() for t in self._model.t}
        batteryTargetArcs = []
        for cr_name, ca_name in data["req_child_amt"]:
            cr = self._rev_cr[cr_name]
            ca = self._rev_ca[ca_name]
            batteryTargetArcs.append((cr, ca))
            targetBatteries[ca].add(cr)

        self.batteryLasers = {b: set() for b in self._model.b}
        for container_name in data["resource_families"]:
            for cr_name in data["resource_families"][container_name]["child_resources"]:
                for pr_name in data["resource_families"][container_name]["parent_resources"]:
                    pr = self._rev_pr[pr_name]
                    cr = self._rev_cr[cr_name]
                    self.batteryLasers[cr].add(pr)

        self._model.laserOrientationArcs = Set(within=self._model.m * self._model.o, initialize=laserOrientationArcs)
        self._model.batteryTargetArcs = Set(within=self._model.b * self._model.t, initialize=batteryTargetArcs)

        targetOrientations = {ca: [] for ca in self._model.t}
        for pa_name in self._data["activity_children"]:
            for ca_name in self._data["activity_children"][pa_name]:
                ca = self._rev_ca[ca_name]
                pa = self._rev_pa[pa_name]
                targetOrientations[ca].append(pa)
        self._model.targetOrientations = Param(self._model.t, initialize=targetOrientations, within=Any)
        self._model.targetBatteries = Param(self._model.t, initialize=targetBatteries, within=Any)

    def __create_vars_params(self):
        data = self._data
        # Define variables
        log.info("Creating variables...")
        # Indicates if battery b fires on target t
        self._model.ENGAGE = Var(self._model.batteryTargetArcs, domain=Binary, initialize=0)
        # Indicates the amount of power needed for target t using battery b
        self._model.POWER = Var(self._model.batteryTargetArcs, domain=NonNegativeReals, initialize=0)
        # Indicates if laser m is in orientation o
        self._model.ORIENT = Var(self._model.laserOrientationArcs, domain=Binary, initialize=0)

        # Indicates if combination c was activated (once we start using this)
        # self._model.COMBO = Var(self._model.c, domain=Binary, initialize=0)

        # Create parameters (i.e., data)
        log.info("Creating parameters...")
        targetValues = {}
        for ca_name in data["child_score"]:
            ca = self._rev_ca[ca_name]
            amt = data["child_score"][ca_name]
            targetValues[ca] = amt

        self._model.targetValues = Param(self._model.t, initialize=targetValues, within=Any)
        self._model.batteryLasers = Param(self._model.b, initialize=self.batteryLasers, within=Any)

        availablePower = {}
        for container_name in data["resource_families"]:
            for cr_name in data["resource_families"][container_name]["child_resources"]:
                amt = data["avail_child_amt"][cr_name]
                cr = self._rev_cr[cr_name]
                availablePower[cr] = amt

        self._model.availablePower = Param(self._model.b, initialize=availablePower, mutable=True, within=Any)

        requiredPower = {}
        for cr_name, ca_name in data["req_child_amt"]:
            cr = self._rev_cr[cr_name]
            ca = self._rev_ca[ca_name]
            amt = data["req_child_amt"][(cr_name, ca_name)]
            requiredPower[(cr, ca)] = amt

        self._model.requiredPower = Param(self._model.batteryTargetArcs, initialize=requiredPower, within=Any)

        maxSelectedOrientations = {}
        for container_name in data["resource_families"]:
            rc = self._rev_rc[container_name]
            amt = len(data["resource_families"][container_name]["parent_resources"])
            maxSelectedOrientations[rc] = amt

        self._model.maxSelectedOrientations = Param(self._model.s, initialize=maxSelectedOrientations, within=Any)

        # Combo not added yet
        # tempDict = {}  # Must convert into dictionary, for Pyomo
        # for c in model.c: tempDict[c] = theData.comboValues[c]
        # model.comboValues = Param(model.c, initialize=tempDict, within=Any)

    def __create_constraints(self):
        # Create objective function
        log.info("Creating objective function...")
        self._model.objective = Objective(rule=objective_rule, sense=maximize)

        # Create constraints

        log.info("Creating constraints on available power...")
        # Each battery has limited power available
        self._model.availPower = Constraint(self._model.b, rule=avail_power_rule)

        log.info("Creating constraints on required power to engage a target...")
        # Each battery has limited power available
        self._model.requiredPowerToEngage = Constraint(self._model.batteryTargetArcs, rule=required_power_rule)

        log.info("Creating constraints on number of times a target may be engaged...")
        # Each target may not be engaged more than once
        self._model.engageLimit = Constraint(self._model.t, rule=engage_limit_rule)

        log.info("Creating constraints ensuring each launcher has exactly one orientation...")
        # Each launcher must be in exactly one orientation
        self._model.orientationLimit = Constraint(self._model.m, rule=orientation_limit_rule)

        log.info("Creating constraints that require resources in same container")
        self._model.link_parent_to_child = Constraint(self._model.batteryTargetArcs, rule=link_parent_to_child_rule)

        # log.info("Creating constraints on enforcing definition of combinations...")
        # Enforce definition on COMBO
        # model.enforceCombo1 = Constraint(model.c, rule=comboDefinition1_rule)
        # model.enforceCombo2 = Constraint(model.c, rule=comboDefinition2_rule)

        # Enforce Force list/ forbid list
        self._model.forceLimit = Constraint(self._model.force, rule=force_rule)
        self._model.forbidLimit = Constraint(self._model.forbid, rule=forbid_rule)

        log.info("DONE!!")

    def fill_output(self, output_class):
        """
        Return the output of the model after it has been solved by instantiating an object of the output class.

        This method must interrogate the model and produce an output object.  Since models may differ,
        this method must be implemented in the subclass

        :param OutputBase output_class: the OutputBase or subclass of output base
        :return output: an instance of the output_class
        """
        output = output_class()

        # objective value
        output.set_objective_value(self._model.objective.expr())

        # results
        parent_allocated = defaultdict(lambda: defaultdict(int))  # nested for efficiency
        child_allocated = defaultdict(lambda: defaultdict(int))
        parent_score, child_score, container_score = defaultdict(float), defaultdict(float), defaultdict(float)
        result = {"full_trace": defaultdict(list)}
        for container_name, data in self._data["resource_families"].items():
            for parent_resource in data["parent_resources"]:
                pr = self._rev_pr[parent_resource]  # initials are for index
                for child_resource in data["child_resources"]:
                    cr = self._rev_cr[child_resource]
                    for child_activity in self._data["child_possible_allocations"][child_resource]:
                        ca = self._rev_ca[child_activity]
                        parent_activities = self._model.targetOrientations[ca]
                        child_picked = self._model.ENGAGE[cr, ca].value
                        du_val = self._model.targetValues[ca]
                        for pa in parent_activities:
                            if (pr, pa) in self._model.laserOrientationArcs:
                                parent_picked = self._model.ORIENT[pr, pa].value
                                picked = parent_picked * child_picked
                                parent_activity = self._data["parent_activities"][pa]  # get name
                                result["full_trace"]["container_name"].append(container_name)
                                result["full_trace"]["parent_resource"].append(parent_resource)
                                result["full_trace"]["parent_activity"].append(parent_activity)
                                result["full_trace"]["child_resource"].append(child_resource)
                                result["full_trace"]["child_activity"].append(child_activity)
                                # Creating the "camkeys" key here to control order when displaying in table
                                result["full_trace"]["camkeys"].append("")
                                result["full_trace"]["parent_budget_used"].append(1 * picked)
                                result["full_trace"]["child_budget_used"].append(self._model.POWER[(cr, ca)].value * picked)
                                result["full_trace"]["value"].append(du_val)
                                result["full_trace"]["selected"].append(picked)

                                if picked:
                                    parent_score[parent_resource] += du_val
                                    container_score[container_name] += du_val
                                    child_score[child_resource] += du_val

                                if parent_picked:
                                    parent_allocated[parent_resource][parent_activity] = 1
                                if child_picked:
                                    child_allocated[child_resource][child_activity] = 1
        result["parent_score"] = parent_score
        result["child_score"] = child_score
        result["container_score"] = container_score
        camkeys = db_helper.get_camkeys(result["full_trace"]["child_activity"])
        if camkeys is not None:
            result["full_trace"]["camkeys"] = camkeys
        else:
            result["full_trace"].pop("camkeys")

        output.set_results(result)

        allocations = {
            "parent": {k: list(parent_allocated[k].keys()) for k in parent_allocated},
            "child": {k: list(child_allocated[k].keys()) for k in child_allocated},
        }
        output.set_allocations(allocations)

        return output
