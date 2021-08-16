""""
This ingests the format from the DM3K-Viz tool
"""
# -------------------------------------------------------------------------
# @license JHUAPL
# Copyright (C) 2021 Johns Hopkins University Applied Physics Laboratory
#
# All Rights Reserved.
# This material may only be used, modified, or reproduced by or for the
# U.S. government pursuant to the license rights granted under FAR
# clause 52.227-14 or DFARS clauses 252.227-7013/7014.
# For any other permission, please contact the Legal Office at JHU/APL.
# --------------------------------------------------------------------------


import logging

from optimizer.slim_optimizer_base import InputBase

log = logging.getLogger(__name__)


class KnapsackInputViz(InputBase):
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

        # --- INGEST ---
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

    def add_scores(self, activity_scores):
        pass  # TODO

    def align_check_scores(self, activity_scores, dus_in_constraints_not_scores_check=False):
        pass  # TODO

    def modify(self, cmd_dict, timestamp):
        pass  # TODO
