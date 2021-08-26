""""
This ingests the format from the DM3K-Viz tool
"""

import logging

from optimizer.slim_optimizer_base import InputBase

log = logging.getLogger(__name__)


class KnapsackInputViz(InputBase):
    """
        The structure of the json input is:
    "datasetName": "fanInKnapsack",
        "files": [
            {
                    "fileName": "fanInKnapsack.json",
                    "fileContents": {
                            "resourceClasses": [
                                    {"className": "Funding",
                                     "locX": 100,
                                     "locY": 0,
                                     "typeName": "resource",
                                     "budgets": ["money"],
                                     "containsClasses": [],
                                     "canBeAllocatedToClasses": ["Startups"]},
                                     ...],
                            "activityClasses": [
                                    {"className": "Startups",
                                     "locX": 550,
                                     "locY": 0,
                                     "typeName": "person/place/thing",
                                     "rewards": ["value"],
                                     "costs": ["money", "people"],
                                     "containsClasses": [],
                                     "allocatedWhen": {}
                                     },
                                     ...],
                            "resourceInstances": [
                                    {"className": "Funding",
                                     "instanceTable": [
                                            {"instanceName": "funding_Resource_instance_0",
                                             "budget": {
                                                             "money": 3.2}}
                                                    ]},
                                    ...],

                            "activityInstances": [
                                    {"className": "Startups",
                                     "instanceTable": [
                                            {"instanceName": "startup_Activity_instance_0",
                                             "cost": {
                                                             "money": 1.2,
                                 "people": 3
                                                     },
                                             ]}},
                    ...],

                            "allocationInstances": [
                                    {"resourceClassName": "Funding",
                                     "activityClassName": "Startups",
                                     "instanceTable": [
                                            {"resourceInstanceName": "ALL",
                                             "activityInstanceName": "ALL"
                                            }
                                      ]},
                            ...],

                            "containsInstances": [],
                            "allocationConstraints": []
                        }
                     }]

        **Note:** some fields are to support the UI (e.g. locX, locY) and others are to allow for functionality to be extended in the future.
    """

    def __init__(self):
        super().__init__()

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
        if "datasetName" in input_dict:
            log.debug("Opening Dataset: " + input_dict["datasetName"])
        else:
            log.warning("'datasetName' is not in input_dict")

        # determine if correct files exist
        # fileName / fileContents support having other cases with multiple files, but the viz input currently needs to be in one file

        if "files" not in input_dict:
            return (
                True,
                [
                    {
                        "err_code": 2,
                        "err_txt": "'files' attribute is not in input_dict...the format of the input is not correct!",
                        "offender": "**YOU**",
                        "fix": "can't fix this!",
                        "is_fatal_error": True,
                    }
                ],
            )

        file_data = input_dict["files"]
        if len(file_data) != 1:
            return (
                True,
                [
                    {
                        "err_code": 1,
                        "err_txt": "system requires 'files' attribute to contain data from 1 file...you have submitted {} files...the necessary files do not exist!".format(
                            len(file_data)
                        ),
                        "offender": "**YOU**",
                        "fix": "can't fix this!",
                        "is_fatal_error": True,
                    }
                ],
            )

        # --- INGEST ---

        # assuming only 1 file is required
        if "fileContents" not in file_data[0]:
            return (
                True,
                [
                    {
                        "err_code": 2,
                        "err_txt": "'fileContents' attribute is not in input_dict['files'][0]...the format of the input is not correct!",
                        "offender": "**YOU**",
                        "fix": "can't fix this!",
                        "is_fatal_error": True,
                    }
                ],
            )

        json_data = file_data[0]["fileContents"]  # this type of input only has one file type
        log.debug("Incoming constraints keys: " + str(list(json_data.keys())))
        self._data = json_data

        # --- VALIDATE ---
        # TODO - need to add validation here
        #    1) needs to check for duplicate instance names
        #    2) there is a single reward for activities
        #    3) should not have more than one instance of ALL:ALL
        #    4) names for budgets and costs should be consistent across all allocations

        return False, []
