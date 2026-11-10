from zen_creator import Sector

from zen_europe.elements.carriers.heat import Heat
from zen_europe.elements.conversion_technologies.biomass_boiler import BiomassBoiler
from zen_europe.elements.conversion_technologies.electrode_boiler import (
    ElectrodeBoiler,
)
from zen_europe.elements.conversion_technologies.heat_pump import HeatPump
from zen_europe.elements.conversion_technologies.natural_gas_boiler import (
    NaturalGasBoiler,
)
from zen_europe.elements.conversion_technologies.oil_boiler import OilBoiler


class HeatSector(Sector):
    """Decentralized heat generation."""

    name = "heat"
    required_sectors = ["electricity", "gas", "biomass"]

    def __init__(self) -> None:
        super().__init__()
        self.elements = [
            NaturalGasBoiler,
            HeatPump,
            OilBoiler,
            BiomassBoiler,
            ElectrodeBoiler,
            Heat,
        ]
