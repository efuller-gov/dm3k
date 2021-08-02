"""
This is the main model for full house problems.  It turns constraints data into a pyomo model that can be solved.
rc = resource container
cr = child resource
ca = child activity
pr = parent resource
pa = parent activity



"""
import logging
from collections import defaultdict

from optimizer.full_house.full_house_input import FullHouseInput
from optimizer.slim_optimizer_base import ModelBase
from pyomo.environ import Any, Binary, ConcreteModel, Constraint, NonNegativeReals, Objective, Param, Set, Var, maximize

log = logging.getLogger(__name__)


# -------------------------------------------------------------------------------
# OBJECTIVES
# -------------------------------------------------------------------------------
def objective_rule(model):
    return sum(model.CHILD_ALLOCATED[cr, ca] * model.child_score[ca] for (cr, ca) in model.cr_ca_arcs)


# -------------------------------------------------------------------------------
# CONSTRAINTS
# -------------------------------------------------------------------------------


def required_parent_amount_rule(model, pr, pa):
    """
    In order for a parent resource to be allocated to a parent activity, a certain amount of parent budget is required.
    A parent activity is selected if and only if the provided amount is sufficient.

    :param ConcreteModel model:
    :param int pr: parent resource
    :param int pa: parent activity
    :return: boolean indicating whether the needed amount is allocated from pr to pa
    """
    return model.PARENT_AMT[pr, pa] == model.req_parent_amt[pr, pa] * model.PARENT_ALLOCATED[pr, pa]


def required_child_amount_rule(model, cr, ca):
    """
    In order for a child resource to select a child activity, a certain amount of child budget is required.
    A child activity is selected if and only if the provided amount is sufficient.

    :param ConcreteModel model:
    :param int cr: child resource
    :param int ca: child activity
    :return: boolean indicating whether the needed amount is allocated from cr to ca
    """
    return model.CHILD_AMT[cr, ca] == model.req_child_amt[cr, ca] * model.CHILD_ALLOCATED[cr, ca]


def available_parent_amount_rule(model, pr):
    """
    Each parent has a limited resource budget; it cannot allocate more than that.

    :param ConcreteModel model:
    :param int pr: parent resource
    :return: boolean indicating whether pr is staying within budget
    """
    if model.parent_possible_allocations[pr]:
        return sum(model.PARENT_AMT[pr, i] for i in model.parent_possible_allocations[pr]) <= model.avail_parent_amt[pr]
    else:
        return Constraint.Skip


def available_child_amount_rule(model, cr):
    """
    Each child has a limited resource budget

    :param ConcreteModel model:
    :param int cr: child resource
    :return: boolean indicating whether cr is staying within budget
    """
    return sum(model.CHILD_AMT[cr, ca] for ca in model.child_possible_allocations[cr]) <= model.avail_child_amt[cr]


def link_parent_to_child_rule(model, cr, ca):
    """
    A child resource can only be allocated to a child activity if a parent resource in the same resource container
    is allocated to a parent activity which is a direct parent of the child activity.

    :param ConcreteModel model:
    :param int cr: child resource
    :param int ca: child activity
    :return: boolean indicating whether there is at least one pr in the same container as cr that is allocated to a pa
        above ca (if cr allocated to ca).
    """
    if cr in model.reverse_child_allocations[ca]:
        return model.CHILD_ALLOCATED[cr, ca] <= sum(
            model.PARENT_ALLOCATED[pr, pa] for pr in model.pr for pa in model.list_pa_that_link_pr_cr_ca[pr, cr, ca]
        )
    else:
        return Constraint.Skip


def child_allocated_limit_rule(model, ca):
    """
    A child activity may not be allocated more than once

    :param ConcreteModel model:
    :param int ca: child activity
    :return: boolean indicating whether ca is allocated at most once.
    """
    if model.reverse_child_allocations[ca]:
        return sum(model.CHILD_ALLOCATED[cr, ca] for cr in model.reverse_child_allocations[ca]) <= 1
    else:
        return Constraint.Skip


def force_child_rule(model, ca):
    """
    Force Child Activity (each child activity in the force list must have a child resource allocated to it)

    :param ConcreteModel model:
    :param int ca: child activity
    :return: boolean indicating whether ca is selected
    """
    return sum(model.CHILD_ALLOCATED[cr, ca] for (cr, i) in model.cr_ca_arcs if i == ca) == 1


def forbid_child_rule(model, ca):
    """
    Forbid Child Activity (each child activity in the force list must NOT have a child resource allocated to it)

    :param ConcreteModel model:
    :param int ca: child activity
    :return: boolean indicating whether ca is *not* selected
    """
    return sum(model.CHILD_ALLOCATED[cr, ca] for (cr, i) in model.cr_ca_arcs if i == ca) == 0


class FullHouseModel(ModelBase):
    def __init__(self):
        super().__init__()
        self._data = None
        self._rev_pr = {}
        self._rev_pa = {}
        self._rev_cr = {}
        self._rev_ca = {}

    def can_solve(self, input_instance):
        """
        In the event the system can leverage multiple models, this function is used to determine if this model
        can solve the input.

        :param FullHouseInput input_instance: a instance of the InputBase class
        :return: Boolean, True = yes, this model can solve it.  False = something about input cannot be solved by model
        """
        # the FullHouseModel can solve any input in the form of the FullHouseInput class
        return isinstance(input_instance, FullHouseInput)

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
                            a dict of the total budget for each parent
                            resource: keys are parent resource names, values
                            are float amounts
        avail_child_amt
                            a dict of the total budget for each child resource:
                            keys are child resource names, values are float
                            amounts
        req_parent_amt
                            a dict of the required cost (amount of budget) for
                            a parent resource to select a parent activity. keys
                            are tuples (prn,pan) where prn is the parent
                            resource name and pan is the parent activity name,
                            values are float amounts
        req_child_amt
                            a dict of the required cost (amount of budget) for
                            a child resource to select a child activity. keys
                            are tuples (crn,can) where crn is the child
                            resource name and can is the child activity name,
                            values are float amounts
        child_score
                            a dict of the float value of each child activity
                            keys are child activity names, values are float
                            amounts
        force_list
                            a list of child activity names that are to be
                            selected
        forbid_list
                                        a list of child activity names that are
                                        NOT to be selected
        parent_possible_allocations
                                        a dict containing the list of possible
                                        parent activity allocations for each
                                        parent resource.  keys are parent
                                        resource names and values are lists of
                                        parent activity names

        child_possible_allocations
                                        a dict containing the list of possible
                                        child activity allocations for each
                                        child resource.  keys are child
                                        resource names and values are lists of
                                        child activity names

        resource_families
                            a dict containing the parent resources and child
                            resources for each resource container.  keys are
                            resource container names and values are dicts with
                            2 keys 'parent_resources' (referencing the list of
                            parent resources under this resource container) and
                            'child_resources' (referencing the list of child
                            resources under this resource container)
        activity_children
                            a dict containing the child activities of each
                            parent activity.  keys are parent activity names,
                            values are list of child activity names for that
                            parent


        """

        self._data = data  # store this for filling output later
        self.__initialize_model()
        self.__set_relationships()
        self.__create_vars_params()
        self.__create_constraints()

    def __initialize_model(self):
        log.info("Building Pyomo model...")
        self._model = ConcreteModel()
        data = self._data
        log.info("Creating indices...")
        # parent resources index
        self._model.pr = Set(initialize=list(range(0, len(data["parent_resources"]))), ordered=True)
        self._rev_pr = {name: i for (i, name) in enumerate(data["parent_resources"])}

        # parent activities index
        self._model.pa = Set(initialize=list(range(0, len(data["parent_activities"]))), ordered=True)
        self._rev_pa = {name: i for (i, name) in enumerate(data["parent_activities"])}

        # child resources index
        self._model.cr = Set(initialize=list(range(0, len(data["child_resources"]))), ordered=True)
        self._rev_cr = {name: i for (i, name) in enumerate(data["child_resources"])}

        # child activities index
        self._model.ca = Set(initialize=list(range(0, len(data["child_activities"]))), ordered=True)
        self._rev_ca = {name: i for (i, name) in enumerate(data["child_activities"])}

        # force set
        force_index = [self._rev_ca[name] for name in data["force_list"]]
        self._model.force = Set(initialize=force_index, ordered=True)

        # forbid set
        forbid_index = [self._rev_ca[name] for name in data["forbid_list"]]
        self._model.forbid = Set(initialize=forbid_index, ordered=True)

    def __set_relationships(self):
        data = self._data
        log.info("Creating relationships...")

        # parent possible allocation
        parent_possible_allocations = defaultdict(list)
        pr_pa_arcs = []
        for pr_name, pa_names in data["parent_possible_allocations"].items():
            pr = self._rev_pr[pr_name]
            for pa_name in pa_names:
                pa = self._rev_pa[pa_name]
                pr_pa_arcs.append((pr, pa))
                parent_possible_allocations[pr].append(pa)
        self._model.parent_possible_allocations = Param(self._model.pr, initialize=parent_possible_allocations, within=Any)
        self._model.pr_pa_arcs = Set(within=self._model.pr * self._model.pa, initialize=pr_pa_arcs)

        # child possible allocation
        cr_ca_arcs = []
        child_possible_allocations = defaultdict(list)
        reverse_child_allocations = defaultdict(list)
        for cr_name in data["child_possible_allocations"]:
            cr = self._rev_cr[cr_name]
            for ca_name in data["child_possible_allocations"][cr_name]:
                ca = self._rev_ca[ca_name]
                cr_ca_arcs.append((cr, ca))
                child_possible_allocations[cr].append(ca)
                reverse_child_allocations[ca].append(cr)
        self._model.cr_ca_arcs = Set(within=self._model.cr * self._model.ca, initialize=cr_ca_arcs)
        self._model.child_possible_allocations = Param(self._model.cr, initialize=child_possible_allocations, within=Any)
        self._model.reverse_child_allocations = Param(self._model.ca, initialize=reverse_child_allocations, within=Any)

        # helper check
        activity_matchups = defaultdict(bool)
        for pa_name in data["activity_children"]:
            for ca_name in data["activity_children"][pa_name]:
                pa = self._rev_pa[pa_name]
                ca = self._rev_ca[ca_name]
                activity_matchups[pa, ca] = True

        pr_cr_arcs = []
        list_pa_that_link_pr_cr_ca = defaultdict(list)
        for container_name in data["resource_families"]:
            for pr_name in data["resource_families"][container_name]["parent_resources"]:
                for cr_name in data["resource_families"][container_name]["child_resources"]:
                    pr = self._rev_pr[pr_name]
                    cr = self._rev_cr[cr_name]
                    pr_cr_arcs.append((pr, cr))
                    for ca in child_possible_allocations[cr]:
                        for pa in parent_possible_allocations[pr]:
                            if activity_matchups[pa, ca]:
                                list_pa_that_link_pr_cr_ca[pr, cr, ca].append(pa)

        # note: apparently pyomo does something special with sets, so it's important that a generic set be the default value
        self._model.list_pa_that_link_pr_cr_ca = Param(
            self._model.pr * self._model.cr * self._model.ca, initialize=list_pa_that_link_pr_cr_ca, default=set(), within=Any
        )

    def __create_vars_params(self):
        data = self._data
        log.info("Creating variables and parameters...")
        # Basically, we change the input data to be indexed by numbers
        # the total amount of budget available from parent resource, pr
        avail_parent_amt = {self._rev_pr[pr_name]: amt for (pr_name, amt) in data["avail_parent_amt"].items()}

        # the total amount of budget available from child resource, cr
        avail_child_amt = {self._rev_cr[cr_name]: amt for (cr_name, amt) in data["avail_child_amt"].items()}

        # the required cost (amount of budget) from parent resource, pr, to be able to select parent activity, pa
        required_parent_cost = {
            (self._rev_pr[pr_name], self._rev_pa[pa_name]): amt for (pr_name, pa_name), amt in data["req_parent_amt"].items()
        }

        # the required cost (amount of budget) from child resource, cr, to be able to select child activity, ca
        required_child_cost = {
            (self._rev_cr[cr_name], self._rev_ca[ca_name]): amt for (cr_name, ca_name), amt in data["req_child_amt"].items()
        }

        # the value rewarded when a child activity is selected
        child_score = {self._rev_ca[ca_name]: score for (ca_name, score) in data["child_score"].items()}

        # now put all these in pyomo model
        self._model.avail_parent_amt = Param(self._model.pr, initialize=avail_parent_amt, within=Any)
        self._model.avail_child_amt = Param(self._model.cr, initialize=avail_child_amt, within=Any)
        self._model.req_parent_amt = Param(self._model.pr_pa_arcs, initialize=required_parent_cost, within=Any)
        self._model.req_child_amt = Param(self._model.cr_ca_arcs, initialize=required_child_cost, within=Any)
        self._model.child_score = Param(self._model.ca, initialize=child_score, within=Any)

        # Variables that will be set while the model is being solved:
        # the amount of budget from parent resource, pr, that is allocated to the parent activity, pa
        self._model.PARENT_AMT = Var(self._model.pr_pa_arcs, domain=NonNegativeReals, initialize=0)

        # the amount of budget from child resource, cr, that is allocated to child activity, ca, in coordination with
        #  parent resource, pr
        self._model.CHILD_AMT = Var(self._model.cr_ca_arcs, domain=NonNegativeReals, initialize=0)

        # indicates if parent resource, pr, is allocated to parent activity, pa
        self._model.PARENT_ALLOCATED = Var(self._model.pr_pa_arcs, domain=Binary, initialize=0)

        # indicates if child resource, cr, is allocated to child activity in coordination with parent resource, pr
        self._model.CHILD_ALLOCATED = Var(self._model.cr_ca_arcs, domain=Binary, initialize=0)

    def __create_constraints(self):
        log.info("Creating constraints...")
        self._model.required_parent_amount = Constraint(self._model.pr_pa_arcs, rule=required_parent_amount_rule)
        self._model.required_child_amount = Constraint(self._model.cr_ca_arcs, rule=required_child_amount_rule)
        self._model.available_parent_amount = Constraint(self._model.pr, rule=available_parent_amount_rule)
        self._model.available_child_amount = Constraint(self._model.cr, rule=available_child_amount_rule)
        self._model.link_parent_to_child = Constraint(self._model.cr_ca_arcs, rule=link_parent_to_child_rule)
        self._model.child_allocated_limit = Constraint(self._model.ca, rule=child_allocated_limit_rule)
        self._model.force_limit = Constraint(self._model.force, rule=force_child_rule)
        self._model.forbid_limit = Constraint(self._model.forbid, rule=forbid_child_rule)

        log.info("Creating objective function...")
        self._model.objective = Objective(rule=objective_rule, sense=maximize)

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
        # output class needs 3 things
        #  1) an objective value
        output.set_objective_value(self._model.objective.expr())

        #  2) a result - a dictionary of scores
        result = {
            "full_trace": {"resource": [], "activity": [], "budget_used": [], "value": [], "selected": [], "picked": [], "allocated": []},
            "allocated_amt": {},
            "per_resource_score": {},
            "per_resource_budget_used": {},
        }
        allocations = {}
        
        picked_parent_combos = []
        picked_child_combos = []
        not_picked_parent_combos = []
        not_picked_child_combos = []

        for container_name, data in self._data["resource_families"].items():
            for parent_resource in data["parent_resources"]:
                pr = self._rev_pr[parent_resource]  # initials are for index
                for child_resource in data["child_resources"]:
                    cr = self._rev_cr[child_resource]
                    for child_activity in self._data["child_possible_allocations"][child_resource]:
                        ca = self._rev_ca[child_activity]
                        parent_activities = self._model.list_pa_that_link_pr_cr_ca[(pr, cr, ca)]
                        child_picked = self._model.CHILD_ALLOCATED[(cr, ca)].value
                        du_val = self._model.child_score[ca]
                        for pa in parent_activities:
                            parent_picked = self._model.PARENT_ALLOCATED[(pr, pa)].value
                            picked = parent_picked * child_picked
                            parent_activity = self._data["parent_activities"][pa]  # get name

                            if picked:
                                if (parent_resource, parent_activity) not in picked_parent_combos:
                                    picked_parent_combos.append((parent_resource, parent_activity))
                                
                                if (child_resource, child_activity) not in picked_child_combos:
                                    picked_child_combos.append((child_resource, child_activity))
                            else:
                                if (parent_resource, parent_activity) not in not_picked_parent_combos:
                                    if (parent_resource, parent_activity) not in picked_parent_combos:
                                        not_picked_parent_combos.append((parent_resource, parent_activity))
                                
                                if (child_resource, child_activity) not in not_picked_child_combos:
                                    if (child_resource, child_activity) not in picked_child_combos:
                                        not_picked_child_combos.append((child_resource, child_activity))

        # sometimes items in picked get into non-picked
        for (re, ac) in picked_parent_combos:
            if (re, ac) in not_picked_parent_combos:
                not_picked_parent_combos.remove((re, ac))

        for (re, ac) in picked_child_combos:
            if (re, ac) in not_picked_child_combos:
                not_picked_child_combos.remove((re, ac))

        # handle all parent metrics
        budget_name1 = self._data["parent_budget_name"]
        for (res_name1, act_name1) in picked_parent_combos:
            pr = self._rev_pr[res_name1]  # initials are for index
            pa = self._rev_pa[act_name1]
            # allocated amount
            if res_name1 in result["allocated_amt"]:
                if act_name1 in result["allocated_amt"][res_name1]:
                    if budget_name1 in result["allocated_amt"][res_name1][act_name1]:
                        log.warning("Attempt to overwrite a budget that already existed")
                    else:
                        result["allocated_amt"][res_name1][act_name1][budget_name1] = self._model.PARENT_AMT[(pr, pa)].value
                else:
                    result["allocated_amt"][res_name1][act_name1] = {}
                    result["allocated_amt"][res_name1][act_name1][budget_name1] = self._model.PARENT_AMT[(pr, pa)].value
            else:
                result["allocated_amt"][res_name1] = {}
                result["allocated_amt"][res_name1][act_name1] = {}
                result["allocated_amt"][res_name1][act_name1][budget_name1] = self._model.PARENT_AMT[(pr, pa)].value

            # handle allocations
            if res_name1 in allocations:
                allocations[res_name1].append(act_name1)
            else:
                allocations[res_name1] = [act_name1]

            # handle budget used...only 1 budget
            if res_name1 in result["per_resource_budget_used"]:
                result["per_resource_budget_used"][res_name1][budget_name1] += self._model.PARENT_AMT[(pr, pa)].value
            else:
                result["per_resource_budget_used"][res_name1] = {}
                result["per_resource_budget_used"][res_name1][budget_name1] = self._model.PARENT_AMT[(pr, pa)].value

            # Full trace
            act1_value = 0   # parent activities have no value
            result["full_trace"]["resource"].append(res_name1)
            result["full_trace"]["activity"].append(act_name1)
            # assume there are two budgets and its oriented [parent_budget, child_budget]
            result["full_trace"]["budget_used"].append([self._model.PARENT_AMT[(pr, pa)].value, 0.0])
            result["full_trace"]["value"].append(act1_value)
            result["full_trace"]["selected"].append(1.0)
            result["full_trace"]["picked"].append(1.0)
            result["full_trace"]["allocated"].append(1.0)

        # handle all child metrics
        budget_name2 = self._data["child_budget_name"]
        for (res_name2, act_name2) in picked_child_combos:  
            cr = self._rev_cr[res_name2]
            ca = self._rev_ca[act_name2]

            # allocated amount
            if res_name2 in result["allocated_amt"]:
                if act_name2 in result["allocated_amt"][res_name2]:
                    if budget_name2 in result["allocated_amt"][res_name2][act_name2]:
                        log.warning("Attempt to overwrite a budget that already existed")
                    else:
                        result["allocated_amt"][res_name2][act_name2][budget_name2] = self._model.CHILD_AMT[(cr, ca)].value
                else:
                    result["allocated_amt"][res_name2][act_name2] = {}
                    result["allocated_amt"][res_name2][act_name2][budget_name2] = self._model.CHILD_AMT[(cr, ca)].value
            else:
                result["allocated_amt"][res_name2] = {}
                result["allocated_amt"][res_name2][act_name2] = {}
                result["allocated_amt"][res_name2][act_name2][budget_name2] = self._model.CHILD_AMT[(cr, ca)].value

            # handle allocations
            if res_name2 in allocations:
                allocations[res_name2].append(act_name2)
            else:
                allocations[res_name2] = [act_name2]

            # handle resource score, parent activities have no value
            ca = self._rev_ca[act_name2]
            act2_value = self._model.child_score[ca]
            if res_name2 in result["per_resource_score"]:
                result["per_resource_score"][res_name2] += act2_value
            else:
                result["per_resource_score"][res_name2] = act2_value

            # handle budget used...only 1 budget
            if res_name2 in result["per_resource_budget_used"]:
                result["per_resource_budget_used"][res_name2][budget_name2] += self._model.CHILD_AMT[(cr, ca)].value
            else:
                result["per_resource_budget_used"][res_name2] = {}
                result["per_resource_budget_used"][res_name2][budget_name2] = self._model.CHILD_AMT[(cr, ca)].value

            # full trace
            result["full_trace"]["resource"].append(res_name2)
            result["full_trace"]["activity"].append(act_name2)
            # assume there are two budgets and its oriented [parent_budget, child_budget]
            result["full_trace"]["budget_used"].append([0.0, self._model.CHILD_AMT[(cr, ca)].value])
            result["full_trace"]["value"].append(act2_value)
            result["full_trace"]["selected"].append(1.0)
            result["full_trace"]["picked"].append(1.0)
            result["full_trace"]["allocated"].append(1.0)
                            
                            
        # do non picked full_trace
        act1_value = 0 
        for (res_name1, act_name1) in not_picked_parent_combos:
            result["full_trace"]["resource"].append(res_name1)
            result["full_trace"]["activity"].append(act_name1)
            result["full_trace"]["budget_used"].append([0.0, 0.0])
            result["full_trace"]["value"].append(act1_value)
            result["full_trace"]["selected"].append(0.0)
            result["full_trace"]["picked"].append(0.0)
            result["full_trace"]["allocated"].append(0.0)

        for (res_name2, act_name2) in not_picked_child_combos:
            ca = self._rev_ca[act_name2]
            act2_value = self._model.child_score[ca] 
            result["full_trace"]["resource"].append(res_name2)
            result["full_trace"]["activity"].append(act_name2)
            result["full_trace"]["budget_used"].append([0.0, 0.0])
            result["full_trace"]["value"].append(act2_value)
            result["full_trace"]["selected"].append(0.0)
            result["full_trace"]["picked"].append(0.0)
            result["full_trace"]["allocated"].append(0.0)
        
        # fill class and return
        output.set_results(result)
        output.set_allocations(allocations)

        return output
