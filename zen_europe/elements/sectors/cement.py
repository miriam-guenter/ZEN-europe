from zen_creator import Sector

from zen_europe.elements.carriers.clinker import Clinker
from zen_europe.elements.carriers.fuel_for_cement import FuelForCement
from zen_europe.elements.conversion_technologies.cement_kiln import CementKiln
from zen_europe.elements.retrofitting_technologies.biomass_to_cement_fuel import (
    BiomassToCementFuel,
)
from zen_europe.elements.retrofitting_technologies.cement_post_comb import (
    CementPostComb,
)
from zen_europe.elements.retrofitting_technologies.coal_to_cement_fuel import (
    CoalToCementFuel,
)
from zen_europe.elements.retrofitting_technologies.hydrogen_to_cement_fuel import (
    HydrogenToCementFuel,
)
from zen_europe.elements.retrofitting_technologies.waste_to_cement_fuel import (
    WasteToCementFuel,
)


class CementSector(Sector):
    """Cement clinker production."""

    name = "cement"
    required_sectors = ["biomass"]

    def __init__(self) -> None:
        super().__init__()
        self.elements = [
            CementKiln,
            CoalToCementFuel,
            WasteToCementFuel,
            BiomassToCementFuel,
            HydrogenToCementFuel,
            CementPostComb,
            Clinker,
            FuelForCement,
        ]
