from .biomass_feedstock import BiomassFeedstock


class StarchCrops(BiomassFeedstock):
    """Starch-based energy crops (barley, wheat, grain maize, oats, rye)."""

    name: str = "starch_crops"
    _biomass_types = ["MINBIOCRP11"]
