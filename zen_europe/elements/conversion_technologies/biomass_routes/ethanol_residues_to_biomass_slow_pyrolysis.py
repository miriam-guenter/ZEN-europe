from .biomass_route import BiomassRoute


class EthanolResiduesToBiomassSlowPyrolysis(BiomassRoute):
    """Dummy route of ethanol_residues into biomass_slow_pyrolysis."""

    name: str = "ethanol_residues_to_biomass_slow_pyrolysis"
    feedstock = "ethanol_residues"
    pool = "biomass_slow_pyrolysis"
