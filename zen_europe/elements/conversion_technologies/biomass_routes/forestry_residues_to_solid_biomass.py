from .biomass_route import BiomassRoute


class ForestryResiduesToSolidBiomass(BiomassRoute):
    """Dummy route of forestry_residues into solid_biomass."""

    name: str = "forestry_residues_to_solid_biomass"
    feedstock = "forestry_residues"
    pool = "solid_biomass"
