from .biomass_route import BiomassRoute


class BiowasteToBiomassSlowPyrolysis(BiomassRoute):
    """Dummy route of biowaste into biomass_slow_pyrolysis."""

    name: str = "biowaste_to_biomass_slow_pyrolysis"
    feedstock = "biowaste"
    pool = "biomass_slow_pyrolysis"
