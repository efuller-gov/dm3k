"""
Extension of optimizer base...just need to do the init to localize it
"""
from dm3k.slim_optimizer.facility_loc.facility_loc_input_viz import FacilityLocInputViz
from dm3k.slim_optimizer.facility_loc.facility_loc_capacitated import FacilityLocCapacitatedModel
from dm3k.slim_optimizer.slim_optimizer_base import OptimizerBase, OutputBase

# TODO - add in commands
COMMAND_CLASS_MAP = {}  #  empty for now


class FacilityLocOptimizerViz(OptimizerBase):
    def __init__(self):
        super().__init__(
            FacilityLocInputViz, [FacilityLocCapacitatedModel], OutputBase, COMMAND_CLASS_MAP
        )