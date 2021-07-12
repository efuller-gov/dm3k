"""
Extension of optimizer base...just need to do the init to localize it
"""
from optimizer.knapsack.knapsack_input_viz import KnapsackInputViz
from optimizer.knapsack.knapsack_model_component import KnapsackComponentModel
from optimizer.slim_optimizer_base import OptimizerBase, OutputBase

# TODO - add in commands
COMMAND_CLASS_MAP = {}  # empty for now


class KnapsackOptimizerViz(OptimizerBase):
    def __init__(self):
        super().__init__(KnapsackInputViz, [KnapsackComponentModel], OutputBase, COMMAND_CLASS_MAP)