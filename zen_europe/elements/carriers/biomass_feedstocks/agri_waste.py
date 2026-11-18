from .biomass_feedstock import BiomassFeedstock


class AgriWaste(BiomassFeedstock):
    """ Agricultural waste and residues from landscape care."""

    name: str = "agri_waste"
    _biomass_types = ["MINBIOAGRW1", "MINBIOFRSR1a"]
 