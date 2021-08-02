"""
Extension of optimizer base...just need to do the init to localize it
"""
from optimizer.full_house.full_house_input_viz import FullHouseInputViz
from optimizer.full_house.full_house_model import FullHouseModel
from optimizer.slim_optimizer_base import OptimizerBase, OutputBase

# TODO - add in commands
COMMAND_CLASS_MAP = {}  # empty for now

class FullHouseOptimizerViz(OptimizerBase):
    def __init__(self):
        super().__init__(
            FullHouseInputViz, FullHouseModel, OutputBase, COMMAND_CLASS_MAP
        )

