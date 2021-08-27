"""
Extension of optimizer base...just need to do the init to localize it
"""

from optimizer.knapsack.knapsack_input_viz import KnapsackInputViz
from optimizer.knapsack.knapsack_model import KnapsackModel
from optimizer.slim_optimizer_base import OptimizerBase, OutputBase


class KnapsackOptimizerViz(OptimizerBase):
    def __init__(self):
        super().__init__(KnapsackInputViz, KnapsackModel, OutputBase)
