"""
This ingests the format from the DM3K-Viz tool
"""

import logging

from optimizer.full_house.full_house_input import FullHouseInput

log = logging.getLogger(__name__)


class FullHouseInputViz(FullHouseInput):
    """
    The viz input format is a single json file that looks like...

    .. note:
        {
            "resourceClasses": [
                {
                    "className": "Ship",
                    "typeName": "container",
                    "budgets": [],
                    "containsClasses": ["Turret","Missile"],
                    "canBeAllocatedToClasses": []
                }, ...],
            "activityClasses": [
                {
                    "className": "City",
                    "typeName": "area",
                    "rewards": [],
                    "costs": ["Direction"],
                    "containsClasses": ["VIP"],
                    "allocatedWhen": {}
                }, ...],
            "resourceInstances": [
                {
                    "className": "Ship",
                    "instanceTable": [
                        {
                            "instanceName": "Ship_Resource_instance_0",
                            "budget": ""
                        },...],
                },...],
            "activityInstances": [
                {
                    "className": "City",
                    "instanceTable": [
                        {
                            "instanceName": "Columbia MD",
                            "cost": 1,
                            "reward": ""
                        },...],
                },...],
            "allocationInstances": [
                {
                    "resourceClassName": "Turret",
                    "activityClassName": "City",
                    "instanceTable": [
                        {
                            "resourceInstanceName": "ALL",
                            "activityInstanceName": "ALL"
                        }
                    ]
                },...],
            "containsInstances": [
                {
                    "parentClassName": "Ship",
                    "childClassName": "Turret",
                    "parentType": "resource",
                    "instanceTable": [
                        {
                            "parentInstanceName": "Ship_Resource_instance_0",
                            "childInstanceName": "Turret_Resource_instance_0"
                        },...],
                },...],
            "allocationConstraints": [
                {
                    "allocationStart": {
                        "resourceClass": "Turret",
                        "activityClass": "City"
                    },
                    "allocationEnd": {
                        "resourceClass": "Missile",
                        "activityClass": "VIP"
                    },
                    "allocationConstraintType": "Contained IF-THEN"
                },...],
        }

    """

    def __init__(self):
        super().__init__()

    def _get_all_instances(self, dm3k_viz_data, class_name, class_type="resource"):
        if class_type == "resource":
            class_type_name = "resourceInstances"
        else:
            class_type_name = "activityInstances"

        instance_list = []
        for i in dm3k_viz_data[class_type_name]:
            if i["className"] == class_name:
                for j in i["instanceTable"]:
                    instance_list.append(j["instanceName"])

        return instance_list

    def _get_instance_prop(self, dm3k_viz_data, class_name, instance_name, prop_name="cost", class_type="resource"):
        if class_type == "resource":
            class_type_name = "resourceInstances"
        else:
            class_type_name = "activityInstances"

        prop_value = None
        for i in dm3k_viz_data[class_type_name]:
            if i["className"] == class_name:
                for j in i["instanceTable"]:
                    if j["instanceName"] == instance_name:
                        prop_value = j[prop_name]

        return prop_value

    def ingest_validate(self, input_dict):
        """
        Validate the constraints and activity scores to determine if following Errors are found

        ERROR_CODE      DESCRIPTION
            1           the necessary constraints files do not exist
            2           the formats of the constraints files are incorrect
            3           the data within the constraints files are not consistent with each other
            4           the data within the constraints files and the activity names are not consistent

        And then Load the files in the constraints path into this input (capturing them in the self._data attribute)

        :param dict input_dict: a dict containing the name of the input and the data from files associated with this input
        :return bool fatal: True=a fatal error has been found, the optimizer should not continue
        :return list validation_errors: a list of errors where each error is a dict with the following attributes...
                    "err_code" : <a int where int is key in ERROR_CODE above>,
                    "err_txt" : <human readable text that describes the error>,
                    "offender" : <string name (of DU, resource, or resource group) that is causing error>,
                    "fix": <string name of process performed to fix the error  or None>,
                    "is_fatal_error": <boolean; True = error is fatal, False = error is fixable>
        """
        log.debug("Opening Dataset: " + input_dict["datasetName"])

        # determine if correct files exist
        file_data = input_dict["files"]
        if len(file_data) != 1:
            return (
                True,
                [
                    {
                        "err_code": 1,
                        "err_txt": "dm3k-viz.json file could not be found in constraints path",
                        "offender": "**YOU**",
                        "fix": "Cant fix this!",
                        "is_fatal_error": True,
                    }
                ],
            )

        dm3k_viz_data = file_data[0]["fileContents"]

        # --- INGEST ---
        log.debug("Ingesting Data")
        self._data = {
            "parent_resources": [],
            "child_resources": [],
            "parent_activities": [],
            "child_activities": [],
            "avail_parent_amt": {},
            "avail_child_amt": {},
            "req_parent_amt": {},
            "req_child_amt": {},
            "child_score": {},
            "force_list": [],
            "forbid_list": [],
            "parent_possible_allocations": {},
            "child_possible_allocations": {},
            "resource_families": {},
            "activity_children": {},
            "parent_budget_name": "",
            "child_budget_name": "",
        }

        # TODO - THIS IS VERY BRITTLE!!! IT ASSUMES THAT ONLY FULL HOUSE PROBLEMS WILL BE SPECIFIED!

        # a parent activity is an activity that contains another activity
        #   so go through all activityClasses and find the one that contains another activity
        #   when you find a contains, list all the instance names of that class
        #  FUTURE:
        #    - if no containing activity exists, and there is only 1 activity class, make a default containing activity
        activity_classes = dm3k_viz_data["activityClasses"]
        parent_activity = None

        for ac in activity_classes:
            if len(ac["containsClasses"]) >= 1:
                parent_activity = ac["className"]
                log.debug("Found Parent_activity = " + parent_activity)

        if parent_activity is None:
            self._add_to_validation_errors(
                "Cannot find parent activity, no activity contains another activity",
                is_fatal_error=True,
                err_code=3,
                offender="**YOU**",
                fix=None,
            )
            return True, self._validation_errors  # this is a fatal error, just stop now

        else:
            self._data["parent_activities"] = self._get_all_instances(dm3k_viz_data, parent_activity, "activity")
            log.debug("parent_activities")
            log.debug(self._data["parent_activities"])

        # the parent resource is a resource that can be allocated to the parent activity
        #   so go through all the resourceClasses and find the one that can be allocated to the parent activity class
        #   when you find the parent resource, list all the instance names of that class
        resource_classes = dm3k_viz_data["resourceClasses"]
        parent_resource = None

        for rc in resource_classes:
            if parent_activity in rc["canBeAllocatedToClasses"]:
                parent_resource = rc["className"]
                log.debug("Found Parent Resource = " + parent_resource)

        if parent_resource is None:
            self._add_to_validation_errors(
                "Cannot find parent resource, no resource can be allocated to the activity: " + parent_activity,
                is_fatal_error=True,
                err_code=3,
                offender="**YOU**",
                fix=None,
            )
            return True, self._validation_errors  # this is a fatal error, just stop now

        else:
            self._data["parent_resources"] = self._get_all_instances(dm3k_viz_data, parent_resource)
            log.debug("parent_resources")
            log.debug(self._data["parent_resources"])

        # avail_parent amt is a dict of the total budget for each parent resource:
        #   keys are parent resource names,
        #   values are float amounts
        parent_res_instance = None
        for ri in dm3k_viz_data["resourceInstances"]:
            if ri["className"] == parent_resource:
                parent_res_instance = ri

        for pri in parent_res_instance["instanceTable"]:

            # budget is a dictionary...full house can only take values
            budget = list(pri["budget"].values())[0]

            # need budget name for output
            self._data["parent_budget_name"] = list(pri["budget"].keys())[0]

            self._data["avail_parent_amt"][pri["instanceName"]] = budget

        log.debug("avail_parent_amt")
        log.debug(self._data["avail_parent_amt"])

        # parent possible allocations is a a dict containing the list of possible parent activity allocations for each
        # parent resource.
        #    keys are parent resource names and
        #    values are lists of parent activity names
        # Use the allocation instances between the parent resource and activity to fill this
        parent_allocation_instance = None
        for ai in dm3k_viz_data["allocationInstances"]:
            if (ai["resourceClassName"] == parent_resource) and (ai["activityClassName"] == parent_activity):
                parent_allocation_instance = ai

        for pai in parent_allocation_instance["instanceTable"]:
            if pai["resourceInstanceName"] == "ALL":
                rin = self._data["parent_resources"]
            else:
                rin = [pai["resourceInstanceName"]]

            if pai["activityInstanceName"] == "ALL":
                ain = self._data["parent_activities"]
            else:
                ain = [pai["activityInstanceName"]]

            for r in rin:
                for a in ain:
                    if r in self._data["parent_possible_allocations"]:
                        self._data["parent_possible_allocations"][r].append(a)
                    else:
                        self._data["parent_possible_allocations"][r] = [a]

        log.debug("parent possible allocations")
        log.debug(self._data["parent_possible_allocations"])

        # req_parent_amt is a dict of required cost for each parent activity instance
        #  keys are tuples (prn,pan) where prn is the parent resource name and pan is the parent activity name,
        #  values are float amounts
        # to make the tuple you need to consult the parent possible allocations above
        # to get the value you need to consult the activity instances
        for pr in self._data["parent_possible_allocations"]:
            for pa in self._data["parent_possible_allocations"][pr]:
                tu = (pr, pa)
                val = self._get_instance_prop(dm3k_viz_data, parent_activity, pa, prop_name="cost", class_type="activity")

                # val can be a dictionary...full house can only take values
                val = list(val.values())[0]

                self._data["req_parent_amt"][tu] = val

        log.debug("required parent amount")
        log.debug(self._data["req_parent_amt"])

        # a child activity is an activity that is contained by the parent activity
        #   (uses the class contained from parent activity above)
        #   list all the instance names of that class
        #  FUTURE:
        #     - if only 1 activity exists, this in the child activity
        child_activity = None

        for ac in activity_classes:
            if ac["className"] == parent_activity:
                if len(ac["containsClasses"]) > 1:
                    log.warning("Parent Activity ({}) has more than one activity it contains...we are taking the first one")
                child_activity = ac["containsClasses"][0]  # assuming the first one
                log.debug("Found child_activity = " + child_activity)

        self._data["child_activities"] = self._get_all_instances(dm3k_viz_data, child_activity, "activity")
        log.debug("child_activities")
        log.debug(self._data["child_activities"])

        # the child resource is a resource that can be allocated to the child activity
        #   so go through all the resourceClasses and find the one that can be allocated to the child activity class
        #   when you find the child resource, list all the instance names of that class
        child_resource = None

        for rc in resource_classes:
            if child_activity in rc["canBeAllocatedToClasses"]:
                child_resource = rc["className"]
                log.debug("Found Child Resource = " + child_resource)

        if child_resource is None:
            self._add_to_validation_errors(
                "Cannot find child resource, no resource can be allocated to the activity: " + child_activity,
                is_fatal_error=True,
                err_code=3,
                offender="**YOU**",
                fix=None,
            )
            return True, self._validation_errors  # this is a fatal error, just stop now

        else:
            self._data["child_resources"] = self._get_all_instances(dm3k_viz_data, child_resource)
            log.debug("child_resources")
            log.debug(self._data["child_resources"])

        # avail_child_amt is a dict of the total budget for each child resource:
        #    keys are child resource names,
        #    values are float amounts
        child_res_instance = None
        for ri in dm3k_viz_data["resourceInstances"]:
            if ri["className"] == child_resource:
                child_res_instance = ri

        for cri in child_res_instance["instanceTable"]:

            # budget is a dictionary...full house can only take values
            budget = list(cri["budget"].values())[0]

            # need budget name for output
            self._data["child_budget_name"] = list(cri["budget"].keys())[0]

            self._data["avail_child_amt"][cri["instanceName"]] = budget

        log.debug("avail_child_amt")
        log.debug(self._data["avail_child_amt"])

        # child possible allocations is a a dict containing the list of possible child activity allocations for each
        # child resource.
        #    keys are child resource names and
        #    values are lists of child activity names
        # Use the allocation instances between the child resource and activity to fill this
        child_allocation_instance = None
        for ai in dm3k_viz_data["allocationInstances"]:
            if (ai["resourceClassName"] == child_resource) and (ai["activityClassName"] == child_activity):
                child_allocation_instance = ai

        for cai in child_allocation_instance["instanceTable"]:
            if cai["resourceInstanceName"] == "ALL":
                rin = self._data["child_resources"]
            else:
                rin = [cai["resourceInstanceName"]]

            if cai["activityInstanceName"] == "ALL":
                ain = self._data["child_activities"]
            else:
                ain = [cai["activityInstanceName"]]

            for r in rin:
                for a in ain:
                    if r in self._data["child_possible_allocations"]:
                        self._data["child_possible_allocations"][r].append(a)
                    else:
                        self._data["child_possible_allocations"][r] = [a]

        log.debug("child possible allocations")
        log.debug(self._data["child_possible_allocations"])

        # req_child_amt is a dict of required cost for each parent activity instance
        #   keys are tuples (prn,pan) where prn is the parent resource name and pan is the parent activity name,
        #   values are float amounts
        # to make the tuple you need to consult the child possible allocations above
        # to get the value you need to consult the activity instances
        for cr in self._data["child_possible_allocations"]:
            for ca in self._data["child_possible_allocations"][cr]:
                tu = (cr, ca)
                val = self._get_instance_prop(dm3k_viz_data, child_activity, ca, prop_name="cost", class_type="activity")

                # val can be a dictionary...full house can only take values
                val = list(val.values())[0]

                self._data["req_child_amt"][tu] = val

        log.debug("required child amount")
        log.debug(self._data["req_child_amt"])

        # a child score is a dict of the float value of each child activity:
        #   keys are child activity names,
        #   values are float amounts
        # just go through the activity instances and grab reward
        for ca in self._data["child_activities"]:
            val = self._get_instance_prop(dm3k_viz_data, child_activity, ca, prop_name="reward", class_type="activity")
            self._data["child_score"][ca] = val

        log.debug("child scores")
        log.debug(self._data["child_score"])

        # force and forbid list  - leave blank

        # resource families is a dict containing the parent resources and child resources for each resource container.
        #    a resource container is a resource that contains both the parent and child resource
        #   FUTURE - make a default resource container if there is not one and put all parents and children in it
        #  keys are resource container names and values are dicts with 2 keys 'parent_resources'
        #  (referencing the list of parent resources under this resource container) and 'child_resources'
        #  (referencing the list of child resources under this resource container)
        # To construct this, find the resource container
        #                    examine the contains instance between the resource container and the parent_resource
        #                    examine the contains instance between the resource container and the child_resource
        resource_container = None
        for rc in dm3k_viz_data["resourceClasses"]:
            contains_classes = rc["containsClasses"]
            if child_resource in contains_classes and parent_resource in contains_classes:
                resource_container = rc["className"]

        if resource_container is None:
            self._add_to_validation_errors(
                "Cannot find resource container, no resource contains both: " + parent_resource + " and " + child_resource,
                is_fatal_error=True,
                err_code=3,
                offender="**YOU**",
                fix=None,
            )
            return True, self._validation_errors  # this is a fatal error, just stop now

        for ci in dm3k_viz_data["containsInstances"]:
            if ci["parentClassName"] == resource_container and ci["childClassName"] == parent_resource:
                for i in ci["instanceTable"]:
                    if i["parentInstanceName"] not in self._data["resource_families"]:
                        self._data["resource_families"][i["parentInstanceName"]] = {"parent_resources": [], "child_resources": []}

                    self._data["resource_families"][i["parentInstanceName"]]["parent_resources"].append(i["childInstanceName"])

        # had to do separate loops because instance container must be set first
        for ci in dm3k_viz_data["containsInstances"]:
            if ci["parentClassName"] == resource_container and ci["childClassName"] == child_resource:
                for i in ci["instanceTable"]:
                    self._data["resource_families"][i["parentInstanceName"]]["child_resources"].append(i["childInstanceName"])

        log.debug("Resource Families")
        log.debug(self._data["resource_families"])

        # activity children is a dict containing the child activities of each parent activity.
        #    keys are parent activity names,
        #    values are list of child activity names for that parent
        # To construct this, examine the contains instance between the parent activity and the child activity name
        for ci in dm3k_viz_data["containsInstances"]:
            if ci["parentClassName"] == parent_activity and ci["childClassName"] == child_activity:
                for i in ci["instanceTable"]:
                    pin = i["parentInstanceName"]
                    cin = i["childInstanceName"]
                    if pin in self._data["activity_children"]:
                        self._data["activity_children"][pin].append(cin)
                    else:
                        self._data["activity_children"][pin] = [cin]

        log.debug("Activity Children")
        log.debug(self._data["activity_children"])

        # FINISH BY VALIDATING
        log.debug("Calling validate method")
        self._validate()
        log.debug("Calling fix method")
        self._fix()
        return self._fatal_error, self._validation_errors

    def add_scores(self, activity_scores):
        """
        Add activity scores to the _data input dictionary

        NOTE - this method is not necessary for operation with UI but is kept here for when optimizers are 
                used outside of the UI

        :param dict activity_scores: Dictionary of DU scores.  Keys are child_activities
        """
        if not activity_scores:  # this should catch None and empty dict {}
            # assume this is how viz with enter scores
            # just take existing scores

            # first check that it exists
            if "child_score" not in self._data:
                raise ValueError("Activity Scores are None and no scores currently exist...cannot continue")

            # then move to use existing child_scores

        else:  # you supplied activity scores
            if set(activity_scores.keys()) == set(self._data["child_activities"]):
                self._data["child_score"] = activity_scores
            else:
                raise ValueError(
                    "Activity names do not match names in dataset:\n{}\n{}\n".format(
                        set(activity_scores.keys()), set(self._data["child_activities"])
                    )
                )
