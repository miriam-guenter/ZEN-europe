from .biomass_route import BiomassRoute


class ForestryResiduesToBiomassSlowPyrolysis(BiomassRoute):
    """Dummy route of forestry_residues into biomass_slow_pyrolysis."""

    name: str = "forestry_residues_to_biomass_slow_pyrolysis"
    feedstock = "forestry_residues"
    pool = "biomass_slow_pyrolysis"
