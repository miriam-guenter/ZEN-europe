from .biomass_feedstock import BiomassFeedstock


class ForestryResidues(BiomassFeedstock):
    """Primary and secondary forestry residues (woodchips, sawdust)."""

    name: str = "forestry_residues"
    _biomass_types = ["MINBIOFRSR1", "MINBIOWOOW1", "MINBIOWOOW1a"]
