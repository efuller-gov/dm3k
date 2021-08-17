"""
This file helps to manage the different optimizers available within DM3K.  It should
be updated as new optimizers are added.
"""

import logging

import optimizer.full_house.full_house_optimizer as fh_optimizer
import optimizer.knapsack.knapsack_optimizer as ks_optimizer

log = logging.getLogger(__name__)

algorithm_dict = {
    "default": ks_optimizer.KnapsackOptimizerViz,
    "FullHouseViz": fh_optimizer.FullHouseOptimizerViz,
    "KnapsackViz": ks_optimizer.KnapsackOptimizerViz,
}


def create_opt(input_dict, config=None):
    """
    Create an optimizer that has already been loaded, model built, and solved

    :param dict input_dict: a dict containing the name of the input and the data from files associated with this input
    :param dict config: a dict containing the parameters that are needed to create the optimizer.  At least this must be..
                        'optimizer':  name of opt algorithm; see algorithm_dict above (e.g. 'default'}
    :return optimizer: an optimizer class; subclass of optimizer.slim_optimizer_base.OptimizerBase
    :return list validation_errors: a list of errors where each error is a dict with the following attributes...
                    "err_code" : <a int where int is key in VALIDATE_ERROR_CODE>,
                    "err_txt" : <human readable text that describes the error>,
                    "offender" : <string or list of name(s) (of DU, resource, or resource group) that is causing error>,
                    "fix" : <string of fix applied, initially is none>
    """
    if config is None:
        config = {}
    if "optimizer" not in config:
        log.warning("Could not find optimizer in config, using Default ({})".format(algorithm_dict["default"]))
        optimizer = algorithm_dict["default"]()
    else:
        if config["optimizer"] not in algorithm_dict:
            raise TypeError(
                "Optimizer named: {0} not found\n"
                "Following optimizers are available {1}".format(config["optimizer"], list(algorithm_dict.keys()))
            )
        else:
            optimizer = algorithm_dict[config["optimizer"]]()

    validation_errors = optimizer.ingest(input_dict)

    return optimizer, validation_errors


def get_optimizers():
    """
    :return:  the list of string names of available optimizers
    """
    return list(algorithm_dict.keys())
