from .biomass_feedstock import BiomassFeedstock


# shares of ENSPRESO codes split across two feedstocks (based on MOPO data)
MUN1_BIOWASTE_SHARE = 0.7  # MINBIOMUN1 -> biowaste vs. wood waste

class WoodWaste(BiomassFeedstock):
    """Waste wood."""

    name: str = "wood_waste"
    _biomass_types = ["MINBIOMUN1"]
    _biomass_shares = {"MINBIOMUN1": 1 - MUN1_BIOWASTE_SHARE}
