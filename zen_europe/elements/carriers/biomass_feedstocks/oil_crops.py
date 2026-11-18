from .biomass_feedstock import BiomassFeedstock


class OilCrops(BiomassFeedstock):
    """Oilseeds (sunflower, soya, rape seed)."""

    name: str = "oil_crops"
    _biomass_types = ["MINBIOLIQ1", "MINBIORPS1"]
