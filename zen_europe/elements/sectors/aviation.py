from zen_creator import Sector

from zen_europe.elements.carriers.kerosene import Kerosene
from zen_europe.elements.conversion_technologies.oil_to_kerosene_conversion import (
    OilToKeroseneConversion,
)
from zen_europe.elements.conversion_technologies.HVO_jet import HVOJet

class AviationSector(Sector):
    """Aviation fuel demand."""

    name = "aviation"
    required_sectors = ["refining"]

    def __init__(self) -> None:
        super().__init__()
        self.elements = [
            OilToKeroseneConversion,
            Kerosene,
            HVOJet,
        ]
