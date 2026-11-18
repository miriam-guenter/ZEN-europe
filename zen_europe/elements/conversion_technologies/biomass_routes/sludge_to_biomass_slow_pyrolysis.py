from .biomass_route import BiomassRoute


class SludgeToBiomassSlowPyrolysis(BiomassRoute):
    """Dummy route of sludge into biomass_slow_pyrolysis."""

    name: str = "sludge_to_biomass_slow_pyrolysis"
    feedstock = "sludge"
    pool = "biomass_slow_pyrolysis"
