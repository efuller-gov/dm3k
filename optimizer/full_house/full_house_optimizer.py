"""
Extension of optimizer base...just need to do the init to localize it
"""
from dm3k.slim_optimizer.full_house.full_house_awd_lasers_model import FullHouseAWDLasersModel
from dm3k.slim_optimizer.full_house.full_house_awd_missiles_model import FullHouseAWDMissilesModel
from dm3k.slim_optimizer.full_house.full_house_commands import COMMAND_CLASS_MAP
from dm3k.slim_optimizer.full_house.full_house_input import FullHouseInput
from dm3k.slim_optimizer.full_house.full_house_input_json import FullHouseInputJson
from dm3k.slim_optimizer.full_house.full_house_input_viz import FullHouseInputViz
from dm3k.slim_optimizer.full_house.full_house_model import FullHouseModel
from dm3k.slim_optimizer.full_house.full_house_model_greedy import FullHouseModelGreedy, GreedyOutput
from dm3k.slim_optimizer.slim_optimizer_base import OptimizerBase, OutputBase


class FullHouseOptimizer(OptimizerBase):
    def __init__(self):
        super().__init__(
            FullHouseInput, [FullHouseAWDMissilesModel, FullHouseAWDLasersModel, FullHouseModel], OutputBase, COMMAND_CLASS_MAP
        )


class FullHouseOptimizerJson(OptimizerBase):
    def __init__(self):
        super().__init__(
            FullHouseInputJson, [FullHouseAWDMissilesModel, FullHouseAWDLasersModel, FullHouseModel], OutputBase, COMMAND_CLASS_MAP
        )


class FullHouseOptimizerViz(OptimizerBase):
    def __init__(self):
        super().__init__(
            FullHouseInputViz, [FullHouseAWDMissilesModel, FullHouseAWDLasersModel, FullHouseModel], OutputBase, COMMAND_CLASS_MAP
        )


# Optimizers specific for an individual Model (For Testing purposes)
class FHFull(OptimizerBase):
    def __init__(self):
        super().__init__(FullHouseInput, FullHouseModel, OutputBase, COMMAND_CLASS_MAP)


class FHFullJson(OptimizerBase):
    def __init__(self):
        super().__init__(FullHouseInputJson, FullHouseModel, OutputBase, COMMAND_CLASS_MAP)


class FHMissilesJson(OptimizerBase):
    def __init__(self):
        super().__init__(FullHouseInputJson, FullHouseAWDMissilesModel, OutputBase, COMMAND_CLASS_MAP)


class FHLasersJson(OptimizerBase):
    def __init__(self):
        super().__init__(FullHouseInputJson, FullHouseAWDLasersModel, OutputBase, COMMAND_CLASS_MAP)


class FullHouseOptimizerGreedy(OptimizerBase):
    def __init__(self):
        super().__init__(FullHouseInput, FullHouseModelGreedy, GreedyOutput, COMMAND_CLASS_MAP)


class FHGreedyJson(OptimizerBase):
    def __init__(self):
        super().__init__(FullHouseInputJson, FullHouseModelGreedy, GreedyOutput, COMMAND_CLASS_MAP)
