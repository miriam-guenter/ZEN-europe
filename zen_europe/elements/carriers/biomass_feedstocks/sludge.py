from .biomass_feedstock import BiomassFeedstock


class Sludge(BiomassFeedstock):
    """Sewage sludge."""

    name: str = "sludge"
    _biomass_types = ["MINBIOSLU1"]
