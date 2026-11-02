from zen_creator import Sector

from zen_europe.elements.carriers.biomass_feedstocks import BIOMASS_FEEDSTOCKS
from zen_europe.elements.carriers.biomass_pools import BIOMASS_POOLS
from zen_europe.elements.conversion_technologies.biomass_routes import (
    BIOMASS_ROUTE_TECHNOLOGIES,
)


class BiomassSector(Sector):
    """Biomass supply: primary feedstocks with ENSPRESO potentials, the pooled
    (dummy) carriers per use pathway, and the dummy technologies routing each
    feedstock into its pools."""

    name = "biomass"
    required_sectors = []

    def __init__(self) -> None:
        super().__init__()
        self.elements = [
            *BIOMASS_FEEDSTOCKS,
            *BIOMASS_POOLS,
            *BIOMASS_ROUTE_TECHNOLOGIES,
        ]