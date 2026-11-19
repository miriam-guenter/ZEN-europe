from .biomass_feedstock import BiomassFeedstock


class ForestryResidues(BiomassFeedstock):
    """Primary (logging residues, landscape care) and secondary (woodchips, sawdust) 
    forestry residues."""

    name: str = "forestry_residues"
    _biomass_types = ["MINBIOFRSR1", "MINBIOWOOW1", "MINBIOWOOW1a", "MINBIOFRSR1a"]
