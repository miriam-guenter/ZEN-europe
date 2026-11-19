from .biomass_feedstock import BiomassFeedstock


class AgriWaste(BiomassFeedstock):
    """ Agricultural waste, including resiudes from agricultural cultivation, harvesting and maintenance activities. 
    Other solid agricultural residues (pruning, orchards residues), straw and stubbles. Also Biomass from olive pitting."""

    name: str = "agri_waste"
    _biomass_types = ["MINBIOAGRW1"]
 