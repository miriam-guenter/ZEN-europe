from zen_creator import Sector

from zen_europe.elements.carriers.methanol import Methanol
from zen_europe.elements.carriers.olefin import Olefin
from zen_europe.elements.conversion_technologies.methanol_from_biogas import (
    MethanolFromBiogas,
)
from zen_europe.elements.conversion_technologies.methanol_from_biomass import (
    MethanolFromBiomass,
)
from zen_europe.elements.conversion_technologies.methanol_from_hydrogen import (
    MethanolFromHydrogen,
)
from zen_europe.elements.conversion_technologies.methanol_from_natural_gas import (
    MethanolFromNaturalGas,
)
from zen_europe.elements.conversion_technologies.methanol_ICE_ship import (
    MethanolICEShip,
)
from zen_europe.elements.conversion_technologies.olefin_from_methanol import (
    OlefinFromMethanol,
)
from zen_europe.elements.conversion_technologies.olefin_from_naphtha import (
    OlefinFromNaphtha,
)
from zen_europe.elements.transport_technologies.methanol_pipeline import (
    MethanolPipeline,
)
from zen_europe.elements.transport_technologies.olefin_pipeline import OlefinPipeline

from zen_europe.elements.conversion_technologies.FAME import FAME
from zen_europe.elements.conversion_technologies.methanol_to_kerosene import MethanolToKerosene
from zen_europe.elements.conversion_technologies.methanol_to_gasoline import MethanolToGasoline


class MethanolSector(Sector):
    """Methanol and olefin production and transport."""

    name = "methanol"
    required_sectors = [
        "electricity",
        "district_heating",
        "hydrogen",
        "refining",
        "gas",
        "biomass",
    ]

    def __init__(self) -> None:
        super().__init__()
        self.elements = [
            MethanolFromNaturalGas,
            MethanolFromBiomass,
            MethanolFromBiogas,
            OlefinFromMethanol,
            MethanolPipeline,
            OlefinPipeline,
            MethanolFromHydrogen,
            OlefinFromNaphtha,
            MethanolICEShip,
            Methanol,
            Olefin,
            FAME,
            MethanolToKerosene,
            MethanolToGasoline,
        ]
