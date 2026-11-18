from .biomass_feedstock import BiomassFeedstock


class Manure(BiomassFeedstock):
    """Manure, solid and liquid."""

    name: str = "manure"
    _biomass_types = ["MINBIOGAS1"]
