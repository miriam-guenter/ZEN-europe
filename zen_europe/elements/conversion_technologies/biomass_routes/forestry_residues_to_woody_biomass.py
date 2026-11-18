from .biomass_route import BiomassRoute


class ForestryResiduesToWoodyBiomass(BiomassRoute):
    """Dummy route of forestry_residues into woody_biomass."""

    name: str = "forestry_residues_to_woody_biomass"
    feedstock = "forestry_residues"
    pool = "woody_biomass"
