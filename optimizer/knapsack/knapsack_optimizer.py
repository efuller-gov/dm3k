"""
Extension of optimizer base...just need to do the init to localize it
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

from optimizer.knapsack.knapsack_input_viz import KnapsackInputViz
from optimizer.knapsack.knapsack_model_component import KnapsackComponentModel
from optimizer.slim_optimizer_base import OptimizerBase, OutputBase


class KnapsackOptimizerViz(OptimizerBase):
    def __init__(self):
        super().__init__(KnapsackInputViz, [KnapsackComponentModel], OutputBase)
