from .biomass_feedstock import BiomassFeedstock


class Stemwood(BiomassFeedstock):
    """Fuelwood, chips and pellets from roundwood."""

    name: str = "stemwood"
    _biomass_types = ["MINBIOWOO", "MINBIOWOOa"]
