from .biomass_feedstock import BiomassFeedstock


class PerennialGrasses(BiomassFeedstock):
    """Lignocellulosic-herbaceous energy crops (miscanthus, switchgrass, RCG)."""

    name: str = "perennial_grasses"
    _biomass_types = ["MINBIOCRP31"]
