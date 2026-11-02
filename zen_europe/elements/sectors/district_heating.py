from zen_creator import Sector

from zen_europe.elements.carriers.district_heat import DistrictHeat
from zen_europe.elements.conversion_technologies.biomass_boiler_DH import (
    BiomassBoilerDH,
)
from zen_europe.elements.conversion_technologies.biomass_CHP import BiomassCHP
from zen_europe.elements.conversion_technologies.district_heating_grid import (
    DistrictHeatingGrid,
)
from zen_europe.elements.conversion_technologies.electrode_boiler_DH import (
    ElectrodeBoilerDH,
)
from zen_europe.elements.conversion_technologies.hard_coal_boiler_DH import (
    HardCoalBoilerDH,
)
from zen_europe.elements.conversion_technologies.heat_pump_DH import HeatPumpDH
from zen_europe.elements.conversion_technologies.natural_gas_boiler_DH import (
    NaturalGasBoilerDH,
)
from zen_europe.elements.conversion_technologies.oil_boiler_DH import OilBoilerDH
from zen_europe.elements.conversion_technologies.waste_boiler_DH import WasteBoilerDH


class DistrictHeatingSector(Sector):
    """District heating generation and grid."""

    name = "district_heating"
    required_sectors = ["heat", "electricity", "gas"]

    def __init__(self) -> None:
        super().__init__()
        self.elements = [
            NaturalGasBoilerDH,
            HeatPumpDH,
            OilBoilerDH,
            WasteBoilerDH,
            BiomassBoilerDH,
            BiomassCHP,
            HardCoalBoilerDH,
            ElectrodeBoilerDH,
            DistrictHeatingGrid,
            DistrictHeat,
        ]
