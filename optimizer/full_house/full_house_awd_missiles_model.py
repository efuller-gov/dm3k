"""
This is the simplest model for full house problems.  It turns constraints data into a pyomo model, which can be solved.
Although phrased in terms of Alien World Domination missiles, it can apply to other problems.

s = ship = resource container (with child resource built in)

t = target = VIP = child activity

m = missile launcher (launcher) = parent resource

o = orientation = parent activity
"""
import logging
from collections import defaultdict

#from dm3k.data_access_layer import db_helper
from optimizer.full_house.full_house_input import FullHouseInput
from optimizer.slim_optimizer_base import ModelBase
from pyomo.environ import Any, Binary, ConcreteModel, Constraint, Objective, Param, Set, Var, maximize

log = logging.getLogger(__name__)


# -------------------------------------------------------------------------------
# OBJECTIVES
# -------------------------------------------------------------------------------
def objective_rule(model):
    return sum(model.FIRE[m, t] * model.targetValues[t] for (m, t) in model.launcherTargetArcs)


# -------------------------------------------------------------------------------
# CONSTRAINTS
# -------------------------------------------------------------------------------
def avail_targets_rule(model, m, t):
    """
    Launchers may only fire on available targets (given their orientation)

    :param ConcreteModel model: the active pyomo model being optimized
    :param int m: launcher
    :param int t: target
    :return: boolean indicating whether that missile can fire on the target
    """
    return model.FIRE[m, t] <= sum(model.ORIENT[m, o] for o in model.targetOrientations[t] if model.launcherOrientationCheck[m, o])


def avail_missiles_rule(model, s):
    """
    Each ship may not fire more missiles than it has available

    :param ConcreteModel model:
    :param int s: ship
    :return: boolean indicating whether that ship fires at most its number of available missiles
    """
    # added a check in case launcher is removed from ship without any other launchers
    if not any(i == s for (m, i) in model.launcherShipArcs):
        return Constraint.Skip
    else:
        return sum(model.FIRE[m, t] for m in model.shipLaunchers[s] for t in model.launcherTargets[m]) <= model.availableMissiles[s]


def orientation_limit_rule(model, m):
    """
    Each launcher must be in exactly one orientation

    :param ConcreteModel model:
    :param int m: launcher
    :return: boolean indicating whether that launcher has a single orientation
    """
    if model.launcherOrientations[m]:
        return sum(model.ORIENT[m, o] for o in model.launcherOrientations[m]) == 1
    else:
        return Constraint.Skip


def engage_limit_rule(model, t):
    """
    Each target may not be engaged more than once

    :param ConcreteModel model:
    :param int t: target
    :return: boolean indicating whether that target is engaged at most once
    """
    if model.targetLaunchers[t]:
        return sum(model.FIRE[m, t] for m in model.targetLaunchers[t]) <= 1
    else:
        return Constraint.Skip


def force_rule(model, t):
    """
    Each target in force list must be engaged

    :param ConcreteModel model:
    :param int t: target
    :return: boolean indicating whether that target is fired on
    """
    return sum(model.FIRE[m, t] for m in model.targetLaunchers[t]) == 1


def forbid_rule(model, t):
    """
    Each target in forbid list must not be engaged

    :param ConcreteModel model:
    :param int t: target
    :return: boolean indicating whether that target is *not* fired on
    """
    return sum(model.FIRE[m, t] for m in model.targetLaunchers[t]) == 0


def force_ship_to_vip_rule(model, s, t):
    """
    In case of force a ship to take out specific VIP (rare)

    :param ConcreteModel model:
    :param int s: ship
    :param int t: target
    :return: boolean indicating whether that ship fires at that VIP
    """
    return (
        sum(model.FIRE[m, t] for (m, i) in model.launcherShipArcs if i == s for (j, k) in model.launcherTargetArcs if j == m and k == t)
        == 1
    )


''' Combos are not yet used
def combo_rule(model, c):
    """
    Combo variable is activated if all targets are selected

    :param ConcreteModel model:
    :param int c: combo
    :return: boolean indicating whether all targets from that combination have been selected
    """
    return model.COMBO[c] >= sum(model.FIRE[m, t] for t in model.cList[c] for (m, t) in model.launcherTargetArcs) - (
        len(model.cList[c]) - 1
    )
'''


class FullHouseAWDMissilesModel(ModelBase):
    def __init__(self):
        super().__init__()
        self._data = {}

    def can_solve(self, input_instance):
        """
        In the event the system can leverage multiple models, this function is used to determine if this model
        can solve the input.

        :param FullHouseInput input_instance: a instance of the InputBase class
        :return: Boolean, True = yes, this model can solve it.  False = something about input cannot be solved by model
        """
        # the FullHouseAWDMissilesModel can solve any input in the form of the FullHouseInput class
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

            for cr_name, ca_name in data["req_child_amt"]:
                amt = data["req_child_amt"][cr_name, ca_name]
                if not amt == 1:
                    return False

            for cr_name in data["child_resources"]:
                if cr_name not in data["child_possible_allocations"]:
                    return False
                if set(data["child_possible_allocations"][cr_name]) != set(data["child_activities"]):
                    return False

            return True
        else:
            return False

    def build(self, data):
        """
        Build the pyomo model in self._model

        :param dict data: a dictionary containing all necessary data for the model
        :return: None

        .. note:
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

        data["containers"] = list(data["resource_families"].keys())
        self._data = data  # store this for filling output later
        self.__initialize_model()
        self.__set_relationships()
        self.__create_vars_params()
        self.__create_constraints()

    def __initialize_model(self):
        data = self._data
        log.info("Building Pyomo model...")
        self._model = ConcreteModel()

        # First build basic sets from the resource model and dictionaries from name to index
        log.info("Creating indices...")
        # Index on each ship
        self._model.s = Set(initialize=list(range(0, len(data["resource_families"]))), ordered=True)
        self._rev_s = {name: i for (i, name) in enumerate(data["resource_families"])}

        # self._rev_cr = {name: i for (i, name) in enumerate(data["child_resources"])}

        # Index on each VIP target
        self._model.t = Set(initialize=list(range(0, len(data["child_activities"]))), ordered=True)
        self._rev_t = {name: i for (i, name) in enumerate(data["child_activities"])}

        # Index on each missile launcher
        self._model.m = Set(initialize=list(range(0, len(data["parent_resources"]))), ordered=True)
        self._rev_m = {name: i for (i, name) in enumerate(data["parent_resources"])}

        # Index on each available orientation
        self._model.o = Set(initialize=list(range(0, len(data["parent_activities"]))), ordered=True)
        self._rev_o = {name: i for (i, name) in enumerate(data["parent_activities"])}

        # force set
        force_index = []
        for name in data["force_list"]:
            force_index.append(self._rev_t[name])
        self._model.force = Set(initialize=force_index, ordered=True)

        # forbid set
        forbid_index = []
        for name in data["forbid_list"]:
            forbid_index.append(self._rev_t[name])
        self._model.forbid = Set(initialize=forbid_index, ordered=True)

        # force ship to hit a VIP
        force_ship_to_vip = []  # placeholder since input doesnt cover this yet
        self._model.forceShip2Vip = Set(within=self._model.s * self._model.t, initialize=force_ship_to_vip)

        # input doesn't cover combinations yet
        """
        # Index on each penalized combination
        num_combinations = 0  # placeholder since input doesnt cover this yet
        self._model.c = Set(initialize=list(range(0, num_combinations)), ordered=True)

        # Set of all the combinations (which are themselves sets)
        self._model.cList = Set(self._model.c)

        combo_list = []
        for c in self._model.c:  # Populate each subset of combinations
            for t in combo_list[c]:
                self._model.cList[c].add(t)
        """

    def __set_relationships(self):
        """
        Sets up relationships in data structures that speed up optimization
            (at the cost of some redundancy).
        The convention is that 2-word camelCase variables give dicts from one object (resource of activity)
        to another that can be used in combination, while 3-word XYArcs give a set of tuples that are possible.
        Words such as 'ship' are used for the name of an object, while letters like 's' are used for the index of
        the object.
        """
        log.info("Creating relationships...")
        data = self._data

        # launcher-ship relationships
        launcherShipArcs = []
        shipLaunchers = {ship: [] for ship in self._model.s}
        for container_name in data["resource_families"]:
            s = self._rev_s[container_name]
            for pr_name in data["resource_families"][container_name]["parent_resources"]:
                m = self._rev_m[pr_name]
                launcherShipArcs.append((m, s))
                shipLaunchers[s].append(m)

        # launcher-orientation-target relationships
        self.launcherOrientations = {m: set() for m in self._model.m}
        launcherOrientationArcs = []
        self.launcherTargets = {m: set() for m in self._model.m}
        targetLaunchers = {t: set() for t in self._model.t}
        launcherTargetCheck = defaultdict(bool)
        self.targetOrientations = {t: set() for t in self._model.t}
        orientationLaunchers = {o: set() for o in self._model.o}
        launcherOrientationCheck = defaultdict(bool)

        for launcher in data["parent_possible_allocations"]:
            m = self._rev_m[launcher]
            for orientation in data["parent_possible_allocations"][launcher]:
                o = self._rev_o[orientation]
                launcherOrientationArcs.append((m, o))
                self.launcherOrientations[m].add(o)
                orientationLaunchers[o].add(m)
                launcherOrientationCheck[m, o] = 1
                for target in data["activity_children"][orientation]:
                    t = self._rev_t[target]
                    launcherTargetCheck[m, t] = 1
                    self.targetOrientations[t].add(o)
                    self.launcherTargets[m].add(t)
                    targetLaunchers[t].add(m)

        self._model.launcherShipArcs = Set(within=self._model.m * self._model.s, initialize=launcherShipArcs)
        self._model.launcherTargetArcs = Set(within=self._model.m * self._model.t, initialize=list(launcherTargetCheck.keys()))
        self._model.launcherOrientationArcs = Set(within=self._model.m * self._model.o, initialize=launcherOrientationArcs)
        self._model.targetLaunchers = Param(self._model.t, initialize=targetLaunchers, within=Any)
        self._model.targetOrientations = Param(self._model.t, initialize=self.targetOrientations, within=Any)
        self._model.launcherTargets = Param(self._model.m, initialize=self.launcherTargets, within=Any)
        self._model.shipLaunchers = Param(self._model.s, initialize=shipLaunchers, within=Any)
        self._model.launcherOrientations = Param(self._model.m, initialize=self.launcherOrientations, within=Any)
        self._model.launcherOrientationCheck = Param(
            self._model.m * self._model.o, initialize=launcherOrientationCheck, default=0, within=Any
        )

    def __create_vars_params(self):
        # Define variables
        log.info("Creating variables...")
        data = self._data
        # Indicates if missile launcher m fires on target t
        self._model.FIRE = Var(self._model.launcherTargetArcs, domain=Binary, initialize=0)

        # Indicates if missile launcher m is in orientation o
        self._model.ORIENT = Var(self._model.launcherOrientationArcs, domain=Binary, initialize=0)

        # Indicates if combination c was activated
        # self._model.COMBO = Var(self._model.c, domain=Binary, initialize=0)

        # Create parameters (i.e., data)
        log.info("Creating parameters...")

        self.targetValues = {self._rev_t[target]: data["child_score"][target] for target in data["child_score"]}
        self._model.targetValues = Param(self._model.t, initialize=self.targetValues, within=Any)

        availableMissiles = {
            self._rev_s[ship]: sum(data["avail_child_amt"][target] for target in data["resource_families"][ship]["child_resources"])
            for ship in data["resource_families"]
        }
        self._model.availableMissiles = Param(self._model.s, initialize=availableMissiles, within=Any)

    def __create_constraints(self):
        # Create objective function
        log.info("Creating objective function...")
        self._model.objective = Objective(rule=objective_rule, sense=maximize)

        # Create constraints

        log.info("Creating constraints on number of available targets...")
        # Launchers may only fire on available targets (given their orientation)
        self._model.availTargets = Constraint(self._model.launcherTargetArcs, rule=avail_targets_rule)

        log.info("Creating constraints on number of available missiles...")
        # Each ship may not fire more missiles than it has available
        self._model.missileLimit = Constraint(self._model.s, rule=avail_missiles_rule)

        log.info("Creating constraints on number of times a target may be engaged...")
        # Each target may not be engaged more than once
        self._model.engageLimit = Constraint(self._model.t, rule=engage_limit_rule)

        log.info("Creating constraints ensuring each launcher has exactly one orientation...")
        # Each launcher must be in exactly one orientation
        self._model.orientationLimit = Constraint(self._model.m, rule=orientation_limit_rule)

        # Enforce Force list/ forbid list
        self._model.forceLimit = Constraint(self._model.force, rule=force_rule)
        self._model.forbidLimit = Constraint(self._model.forbid, rule=forbid_rule)

        # Combo not added yet
        """
        tempDict = {}  # Must convert into dictionary, for Pyomo
        for c in model.c: tempDict[c] = theData.comboValues[c]
        model.comboValues = Param(model.c, initialize=tempDict, within=Any)
        print("Creating constraints on enforcing definition of combinations...")
        Enforce definition on COMBO
        model.enforceCombo = Constraint(model.c, rule=combo_rule)

        Enforce "individual selection," i.e., certain targets must be hit (extension #3)
        NOPE THIS IS A DIRECT ALLOCATION OF A LAUNCHER TO A TARGET
        Constraints take this form:
        model.FIRE[0,0].value = 1
        model.FIRE[0,0].fixed = True

        NOT NEEDED YET
        for l, v in theData.fixedFIREValues:
            print("Fixing values for FIRE...using launcher# {} and vip# {}".format(l, v))
            model.FIRE[l, v].value = 1
            model.FIRE[l, v].fixed = True

        for l, o in theData.fixedORIENTValues:
            print("Fixing values for ORIENT...using launcher# {} and orient# {}".format(l, o))
            model.ORIENT[l, o].value = 1
            model.ORIENT[l, o].fixed = True
        Enforce <-- not used yet
        model.forceShip2VipLimit = Constraint(model.forceShip2Vip, rule=force_ship_to_vip_rule)
        """
        log.info("DONE!!")
        # log.debug(self._model.pprint())

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
        for m, s in self._model.launcherShipArcs:
            # remember: child resources get combined for missiles; just 1 quantity per ship
            container_name = self._data["containers"][s]
            parent_resource = self._data["parent_resources"][m]
            if self._data["resource_families"][container_name]["child_resources"]:
                child_resource = self._data["resource_families"][container_name]["child_resources"][0]
            else:
                child_resource = "child_resource_".format(s)
            for t in self.launcherTargets[m]:
                child_picked = self._model.FIRE[(m, t)].value
                du_val = self.targetValues[t]
                child_activity = self._data["child_activities"][t]
                for o in self.launcherOrientations[m]:
                    if o in self.targetOrientations[t]:
                        parent_picked = self._model.ORIENT[m, o].value
                        picked = parent_picked * child_picked
                        parent_activity = self._data["parent_activities"][o]
                        result["full_trace"]["container_name"].append(container_name)
                        result["full_trace"]["parent_resource"].append(parent_resource)
                        result["full_trace"]["parent_activity"].append(parent_activity)
                        result["full_trace"]["child_resource"].append(child_resource)
                        result["full_trace"]["child_activity"].append(child_activity)
                        # Creating the "camkeys" key here to control order when displaying in table
                        result["full_trace"]["camkeys"].append("")
                        result["full_trace"]["parent_budget_used"].append(1 * picked)
                        result["full_trace"]["child_budget_used"].append(1 * picked)
                        result["full_trace"]["value"].append(du_val)
                        result["full_trace"]["selected"].append(picked)

                        if picked:
                            parent_score[parent_resource] += du_val
                            container_score[container_name] += du_val
                            child_score[child_resource] += du_val

                        if parent_picked:
                            parent_allocated[parent_resource][parent_activity] = 1
                        if child_picked:
                            child_allocated[container_name][child_activity] = 1
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
