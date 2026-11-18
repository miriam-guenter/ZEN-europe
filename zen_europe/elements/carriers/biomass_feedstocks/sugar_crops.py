from .biomass_feedstock import BiomassFeedstock


class SugarCrops(BiomassFeedstock):
    """Sugar from sugar beet."""

    name: str = "sugar_crops"
    _biomass_types = ["MINBIOCRP21"]
