"""
Extension of optimizer base...just need to do the init to localize it
"""
from optimizer.full_house.full_house_awd_lasers_model import FullHouseAWDLasersModel
from optimizer.full_house.full_house_awd_missiles_model import FullHouseAWDMissilesModel
from optimizer.full_house.full_house_input_viz import FullHouseInputViz
from optimizer.full_house.full_house_model import FullHouseModel
from optimizer.full_house.full_house_model_greedy import FullHouseModelGreedy, GreedyOutput
from optimizer.slim_optimizer_base import OptimizerBase, OutputBase

# TODO - add in commands
COMMAND_CLASS_MAP = {}  # empty for now

class FullHouseOptimizerViz(OptimizerBase):
    def __init__(self):
        super().__init__(
            FullHouseInputViz, FullHouseModel, OutputBase, COMMAND_CLASS_MAP
        )


# Optimizers specific for an individual Model (For Testing purposes)
class FHFull(OptimizerBase):
    def __init__(self):
        super().__init__(FullHouseInputViz, FullHouseModel, OutputBase, COMMAND_CLASS_MAP)


class FHFullJson(OptimizerBase):
    def __init__(self):
        super().__init__(FullHouseInputViz, FullHouseModel, OutputBase, COMMAND_CLASS_MAP)


class FHMissilesJson(OptimizerBase):
    def __init__(self):
        super().__init__(FullHouseInputViz, FullHouseAWDMissilesModel, OutputBase, COMMAND_CLASS_MAP)


class FHLasersJson(OptimizerBase):
    def __init__(self):
        super().__init__(FullHouseInputViz, FullHouseAWDLasersModel, OutputBase, COMMAND_CLASS_MAP)


class FullHouseOptimizerGreedy(OptimizerBase):
    def __init__(self):
        super().__init__(FullHouseInputViz, FullHouseModelGreedy, GreedyOutput, COMMAND_CLASS_MAP)


class FHGreedyJson(OptimizerBase):
    def __init__(self):
        super().__init__(FullHouseInputViz, FullHouseModelGreedy, GreedyOutput, COMMAND_CLASS_MAP)
