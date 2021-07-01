
"""
This is the main model for facility location problems.  It turns constraints data into a pyomo model that can be solved.

j = facility loc site
i = customers/demand points



"""
import logging
from collections import defaultdict

from dm3k.slim_optimizer.facility_loc.facility_loc_input_viz import FacilityLocInputViz
from dm3k.slim_optimizer.slim_optimizer_base import ModelBase
from pyomo.environ import Any, Binary, ConcreteModel, Constraint, NonNegativeReals, NonNegativeIntegers, Objective, Param, Set, Var, maximize,minimize, summation

log = logging.getLogger(__name__)


# -------------------------------------------------------------------------------
# OBJECTIVES
# -------------------------------------------------------------------------------
def objective_rule(model):
    """
    Minimize cost/distance between facilities and demand points plus startup costs
    for each facility at a location
    """
    return summation(model.resource_activated_cost, model.y) + summation(model.allocation_penalty, model.x)

# -------------------------------------------------------------------------------
# CONSTRAINTS
# -------------------------------------------------------------------------------

def required_supply_rule(model,i):
    """
    Each demand point requires a certain amount of supply from all facilities

    :param ConcreteModel model:
    :param int i: demand point
    :return: boolean indicating whether that demand point is receiving enough supply
    """
    return sum(model.x[j,i] for j in model.res_id_index) == model.required_amount[i]

def available_supply_rule(model, j):
    """
    The available supply at an activated facility location is greater than or equal to the sum of supply it is providing to all demand points.
    (In short: facility cannot allocate more supplies than it has.)
    
    :param ConcreteModel model:
    :param int j: facility location
    :return: boolean indicating if that facility is not giving out more supplies than it has
    """
    return sum(model.x[j,i] for i in model.act_id_index) <= model.available_amount[j]*model.y[j]

def indicated_need_limit_rule(model,i,j):
    """
    Redundant constraint allowing a demand points' indicated demand/need to be the maximum
     of the amount allocated to a that demand point from an activated facility
    
    :param ConcreteModel model
    :param int i: demand point
    :param int j: facility location
    :return: boolean indicating if the allocated resources from that facility are less than or equal to the demand points' resource needs
    """
    return model.x[j,i] <= model.required_amount[i] * model.y[j]

def available_facility_rule(model):
    """
    The number of facililties allocated is less than or equal to some maximum k
    
    :param ConcreteModel model:
    :return: boolean indicating if that facility is not giving out more supplies than it has
    """
    return summation(model.y) <= model.res_max_activated #or == k 


class FacilityLocCapacitatedModel(ModelBase):
    def can_solve(self, input_instance):
        """
        In the event the system can leverage multiple models, this function is used to determine if this model
        can solve the input.

        :param FullHouseInput input_instance: a instance of the InputBase class
        :return: Boolean, True = yes, this model can solve it.  False = something about input cannot be solved by model
        """
        # the _____ can solve any input in the form of the ______ class
        return isinstance(input_instance, FacilityLocInputViz)


    def __init__(self):
        super().__init__()
        self._data = {}

    def build(self, data):
        self._data = data  # store this for filling output later
        log.info("Building Pyomo model...")
        self._model = ConcreteModel()
        self.__create_indicies()
        self.__create_relationships()
        self.__create_params_variables()
        self.__create_constraints()
        self.__create_objective()

        log.info("....Pyomo model complete")
        log.debug(self._model.pprint())

    def __create_indicies(self):
        log.info("Creating indices...")

        
        
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
        self.max_res_id = max_res_id
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
        self.max_act_id = max_act_id
        self._model.act_id_index = Set(initialize=list(range(0, max_act_id)), ordered=True)

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

    def __create_relationships(self):
        r_a_arcs =[(r_id,a_id) for r_id in range(0,self.max_res_id) for a_id in range(0,self.max_act_id) ]
        self._model.r_a_arcs = Set(within=self._model.res_id_index*self._model.act_id_index, initialize=r_a_arcs) 
        # which resource to activity allocations

    def __create_params_variables(self):
        log.info("Creating variables and parameters...")

        # parameters that are needed to optimize
        act_costs = {}
        res_budgets = {}
        res_rewards = {}
        alloc_rewards = {}

        # rewards and costs
        for act_class_instance in self._data["activityInstances"]: # demand areas
            for act_instance in act_class_instance["instanceTable"]:
                a_id = self._act_name_to_id[act_instance["instanceName"]] # demandArea_Activity_instance_0
                # act_reward[a_id] = act_instance["reward"] # we don't have rewards

                for c_name in act_instance["cost"]:
                    b_id = self._budget_name_to_id[c_name] # vaccines
                    # act_costs[(a_id, b_id)] = act_instance["cost"][c_name] # vaccine cost
                    act_costs[a_id] = act_instance["cost"][c_name] 

        
        for res_class_instance in self._data["resourceInstances"]:
            for res_instance in res_class_instance["instanceTable"]:
                r_id = self._res_name_to_id[res_instance["instanceName"]]
				
				# budgets
                for b_name in res_instance["budget"]:
                    b_id = self._budget_name_to_id[b_name] #vaccine is our budget
                    # res_budgets[(r_id, b_id)] = res_instance["budget"][b_name]
                    res_budgets[r_id] = res_instance["budget"][b_name]

				# rewards (previously named "penalties")
                print(res_instance)
                for p_name in res_instance["reward"]:
                    # b_id = self._budget_name_to_id[p_name]
                    # res_rewards[(r_id, b_id)] = res_instance["rewards"][p_name]
                    res_rewards[r_id] = res_instance["reward"][p_name]

        self._reward_name = self._data["resourceClasses"][0]["rewards"][0]
        # should be activityClasses probably...

        for all_class_instance in self._data["allocationInstances"]:
            for all_instance in all_class_instance["instanceTable"]:
                r_id = self._res_name_to_id[all_instance["resourceInstanceName"]]
                a_id = self._act_name_to_id[all_instance["activityInstanceName"]]
                
                alloc_rewards[(r_id,a_id)] = all_instance['reward'][self._reward_name]

        log.debug("   required_amount Param..."+str(len(act_costs)))
        log.debug("     " + str(act_costs))
        log.debug("   available_amount Param..."+str(len(res_budgets)))
        log.debug("     " + str(res_budgets))


        log.debug("   resource instance reward Param..."+str(len(res_rewards)))
        log.debug("     " + str(res_rewards))
        log.debug("   allocation reward Param..."+str(len(alloc_rewards)))
        log.debug("     " + str(alloc_rewards))


        # total_costs = {}
        # for (a_id, b_id) in act_costs:
        #     if a_id not in total_costs:
        #         total_costs[a_id] = act_costs[(a_id, b_id)]
        #     else:
        #         total_costs[a_id] += act_costs[(a_id, b_id)]
        total_costs = act_costs


        # Volume the facility services is limited to a given maximum amount that may be handled yearly
        self._model.available_amount = Param(self._model.res_id_index, initialize=res_budgets, within=Any)
        # TODO will be r_b_arcs

        # Facility location cost (rent or startup cost)
        self._model.resource_activated_cost = Param(self._model.res_id_index, initialize=res_rewards, within=Any)

        # Transport/distance (loc -> demand) cost (this is where we draw from a distance matrix)
        self._model.allocation_penalty = Param(self._model.r_a_arcs, initialize=alloc_rewards, within=Any)
        # TODO will be r_a_b arcs

        # Demand (annual or total demand if cost is fixed)
        self._model.required_amount = Param(self._model.act_id_index, initialize=act_costs, within=Any)
        # TODO will be a_b_arcs

        # Max number of facilities
        if 'maxActiveInstances' in self._data['resourceClasses'][0]:
            self._model.res_max_activated = Param(initialize = self._data['resourceClasses'][0]["maxActiveInstances"])
        else:
            self._model.res_max_activated = Param(initialize = self.max_res_id)

        
        # Provides quantity of resources facility location j provides to demand point i
        self._model.x = Var(self._model.r_a_arcs, domain=NonNegativeIntegers, initialize=0) # will be r_a_b arcs ALLOCATED_AMT
		# Indicates if location j has active facility
        self._model.y = Var(self._model.res_id_index, domain=Binary, initialize=0) # will be r_b_arcs ALLOCATED

    def __create_constraints(self):
        log.info("Creating constraints...")

        # Create constraints
        log.info("Creating constraints ensuring demand point need is met...")
        # Each demand point requires a certain amount of supply from all facilities
        self._model.required_supply_rule       = Constraint(self._model.act_id_index, rule=required_supply_rule)
        
        log.info("Creating constraints on amount of available supplies...")
        # Facility cannot allocate more supplies than it has.
        self._model.available_supply_rule      = Constraint(self._model.res_id_index, rule=available_supply_rule)

        log.info("Creating constraints on maximum amount of allocated resources to demand points...")
        # Redundant constraint allowing a demand points' indicated demand/need to be the maximum of the 
        # amount allocated to that demand point from a facility if it is activated
        self._model.indicated_need_limit_rule  = Constraint(self._model.act_id_index, self._model.res_id_index, rule=indicated_need_limit_rule)

        log.info("Creating constraints on number of facilities...")
        # The number of facililties allocated is less than or equal to some maximum k
        self._model.available_facility_rule    = Constraint(rule=available_facility_rule)

        log.info("DONE!!")

    def __create_objective(self):
        # Create objective function
        log.info("Creating objective function...")
        self._model.objective = Objective(rule=objective_rule, sense=minimize)


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
            "full_trace": {
                "resource": [],
                "activity": [],
                "budget_used": [],
                "value": [],
                "allocated": [],
                "value_per_allocated": [],
                "value_per_facility": [],
                "selected": []
            },
            "allocated_amt": {},
            "per_resource_score": {},
            "per_resource_budget_used": {},
            "selected_facilities": {}
        }

        # calculate allocated amount
        b_id = 0
        for (r_id, a_id) in self._model.r_a_arcs:
            if self._model.x[r_id, a_id].value:
                res_name = self._res_id_to_name[r_id]
                act_name = self._act_id_to_name[a_id]
                budget_name = self._budget_id_to_name[b_id]
                if res_name in result["allocated_amt"]:
                    if act_name in result["allocated_amt"][res_name]:
                        if budget_name in result["allocated_amt"][res_name]:
                            log.warning("Attempt to overwrite a budget that already existed")
                        else:
                            result["allocated_amt"][res_name][act_name][budget_name] = self._model.x[
                                r_id, a_id].value
                    else:
                        result["allocated_amt"][res_name][act_name] = {}
                        result["allocated_amt"][res_name][act_name][budget_name] = self._model.x[
                            r_id, a_id].value
                else:
                    result["allocated_amt"][res_name] = {}
                    result["allocated_amt"][res_name][act_name] = {}
                    result["allocated_amt"][res_name][act_name][budget_name] = self._model.x[
                        r_id, a_id].value

        # calculate per_resource amount - from allocated amount
        for res_name in result["allocated_amt"]:
            result["per_resource_budget_used"][res_name] = {}
            for act_name in result["allocated_amt"][res_name]:
                for budget_name in result["allocated_amt"][res_name][act_name]:
                    if budget_name not in result["per_resource_budget_used"][res_name]:
                        result["per_resource_budget_used"][res_name][budget_name] = \
                            result["allocated_amt"][res_name][act_name][budget_name]
                    else:
                        result["per_resource_budget_used"][res_name][budget_name] += \
                            result["allocated_amt"][res_name][act_name][budget_name]

        #  3) allocations - the mapping of resources to activities
        allocations = {}

        for (r_id, a_id) in self._model.r_a_arcs:
            res_name = self._res_id_to_name[r_id]
            act_name = self._act_id_to_name[a_id]
            
            alloc_reward = self._get_allocation_class_instance(act_name, res_name)["reward"][self._reward_name]
            act_value = alloc_reward * self._model.x[(r_id, a_id)].value
            
            res_value = self._get_resource_instance(self._res_name_to_class[res_name],
                                        res_name)["reward"][self._reward_name]
            act_selected = 0
            budget_used = [0] * self._max_budget_id

            if self._model.x[r_id, a_id].value > 1e-10:
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
                    if (r_id, a_id) in self._model.r_a_arcs:
                        budget_used[b_id] = self._model.x[(r_id, a_id)].value
            
            

            # handle full_trace
            result["full_trace"]["resource"].append(res_name)
            result["full_trace"]["activity"].append(act_name)
            result["full_trace"]["budget_used"].append(budget_used)
            result["full_trace"]["value"].append(act_value) # reward to each activity
            result["full_trace"]["value_per_allocated"].append(alloc_reward)#self._model.allocation_penalty[(r_id,a_id)].value)
            result["full_trace"]["selected"].append(act_selected)
            result["full_trace"]["value_per_facility"].append(res_value)
            result["full_trace"]["allocated"].append(self._model.x[(r_id, a_id)].value)
        
        for r_id in self._model.res_id_index:
            res_name = self._res_id_to_name[r_id]
            result["selected_facilities"][res_name] = self._model.y[r_id].value
            # if we activated this facility
            if self._model.y[r_id].value:

                res_value = self._get_resource_instance(self._res_name_to_class[res_name],
                                                    res_name)["reward"][self._reward_name]
                # handle resource score
                if res_name in result["per_resource_score"]:
                    result["per_resource_score"][res_name] += res_value
                else:
                    result["per_resource_score"][res_name] = res_value


        output.set_results(result)
        output.set_allocations(allocations)

        return output
    def _get_alloc_inst_name(self, alloc_inst):
        return alloc_inst["resourceClassName"]+'_'+alloc_inst["activityClassName"]

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

    def _get_resource_instance(self, class_name, instance_name):
        res_class = self._get_resource_class_instance(class_name)
        for i in res_class["instanceTable"]:
            if i["instanceName"] == instance_name:
                return i
        return None

    def _get_allocation_class_instance(self,act_name,res_name):
        for i in self._data['allocationInstances'][0]['instanceTable']:
            # print(i)
            if (i["resourceInstanceName"] == res_name) and (i["activityInstanceName" ]== act_name):
                return i