from .biomass_route import BiomassRoute


class DigestateToBiomassSlowPyrolysis(BiomassRoute):
    """Dummy route of digestate into biomass_slow_pyrolysis."""

    name: str = "digestate_to_biomass_slow_pyrolysis"
    feedstock = "digestate"
    pool = "biomass_slow_pyrolysis"
