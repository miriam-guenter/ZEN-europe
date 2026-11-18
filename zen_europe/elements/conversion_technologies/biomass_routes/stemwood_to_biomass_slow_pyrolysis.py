from .biomass_route import BiomassRoute


class StemwoodToBiomassSlowPyrolysis(BiomassRoute):
    """Dummy route of stemwood into biomass_slow_pyrolysis."""

    name: str = "stemwood_to_biomass_slow_pyrolysis"
    feedstock = "stemwood"
    pool = "biomass_slow_pyrolysis"
