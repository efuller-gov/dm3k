"""
This file helps to manage the different optimizers available within DM3K.  It should
be updated as new optimizers are added.
"""

import glob
import logging
import os

import dm3k.slim_optimizer.full_house.full_house_optimizer as fh_optimizer
import dm3k.slim_optimizer.knapsack.knapsack_optimizer as ks_optimizer
import dm3k.slim_optimizer.facility_loc.facility_loc_optimizer as fl_optimizer

log = logging.getLogger(__name__)

algorithm_dict = {
    # Make sure that any optimizer classes that use FullHouseInputJson as input have 'Json' in the keys below
    "default": fh_optimizer.FullHouseOptimizer,
    "default_json": fh_optimizer.FullHouseOptimizerJson,
    "FullHouse": fh_optimizer.FullHouseOptimizer,
    "FullHouseOptimizer": fh_optimizer.FullHouseOptimizer,
    "FullHouseJson": fh_optimizer.FullHouseOptimizerJson,
    "FullHouseViz": fh_optimizer.FullHouseOptimizerViz,
    "FullHouseOptimizerJson": fh_optimizer.FullHouseOptimizerJson,
    "FHFull": fh_optimizer.FHFull,
    "FHFullJson": fh_optimizer.FHFullJson,
    "FHMissilesJson": fh_optimizer.FHMissilesJson,
    "FHLasersJson": fh_optimizer.FHLasersJson,
    "FHGreedyJson": fh_optimizer.FHGreedyJson,
    "KnapsackViz": ks_optimizer.KnapsackOptimizerViz,
    "FacilityLocViz": fl_optimizer.FacilityLocOptimizerViz
}


def create_opt(constraints_path, activity_scores_names, config):
    """
    Create an optimizer that has already been loaded, model built, and solved

    :param str constraints_path: path to the constraints folder in a dataset
    :param list activity_scores_names: a list of activities that will have associated scores
    :param dict config: a dict containing the parameters that are needed to create the optimizer.  At least this must be..
                        'optimizer':  name of opt algorithm; see algorithm_dict above (e.g. 'default'}
    :return optimizer: an optimizer class; subclass of dm3k.slim_optimizer.slim_optimizer_base.OptimizerBase
    :return list validation_errors: a list of errors where each error is a dict with the following attributes...
                    "err_code" : <a int where int is key in VALIDATE_ERROR_CODE>,
                    "err_txt" : <human readable text that describes the error>,
                    "offender" : <string or list of name(s) (of DU, resource, or resource group) that is causing error>,
                    "fix" : <string of fix applied, initially is none>
    """
    if "optimizer" not in config:
        log.warning("Could not find optimizer in config, using FullHouseOptimizer")
        optimizer = fh_optimizer.FullHouseOptimizer()
    else:
        if config["optimizer"] not in algorithm_dict:
            raise TypeError(
                "Optimizer named: {0} not found\n"
                "Following optimizers are available {1}".format(config["optimizer"], list(algorithm_dict.keys()))
            )
        optimizer = algorithm_dict[config["optimizer"]]()

    # This might not be the right place for this kind of check, but looking for a cleaner way to specify not using
    # a correct optimizer for a given dataset
    if "Json" not in optimizer.__class__.__name__:
        constraints_file = constraints_path + "/constraints.json"
        if os.path.exists(constraints_file):
            raise ValueError(
                "A {} was found.\nPlease use a optimizer that can parse this type of file: {}".format(
                    constraints_file, [x for x in list(algorithm_dict.keys()) if "Json" in x]
                )
            )
        else:
            log.info("%s can be used to optimize this dataset", optimizer.__class__.__name__)

    else:
        csv_files = glob.glob(constraints_path + "/constraints/*.csv")
        if len(csv_files) > 0:
            raise ValueError(
                "Following files were found:\n{}\nPlease use a optimizer that can parse this type of file: {}".format(
                    csv_files, [x for x in list(algorithm_dict.keys()) if "Json" not in x and "Viz" not in x]
                )
            )
        else:
            log.info("%s can be used to optimize this dataset", optimizer.__class__.__name__)

    validation_errors = optimizer.ingest(constraints_path, activity_scores_names=activity_scores_names)

    return optimizer, validation_errors


def get_optimizers():
    """
    :return:  the list of string names of available optimizers
    """
    return list(algorithm_dict.keys())
