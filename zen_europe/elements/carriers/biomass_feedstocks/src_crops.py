from .biomass_feedstock import BiomassFeedstock


class SRCCrops(BiomassFeedstock):
    """Lignocellulosic-woody energy crops, short rotation coppice (willow, poplar)."""

    name: str = "src_crops"
    _biomass_types = ["MINBIOCRP41", "MINBIOCRP41a"]
