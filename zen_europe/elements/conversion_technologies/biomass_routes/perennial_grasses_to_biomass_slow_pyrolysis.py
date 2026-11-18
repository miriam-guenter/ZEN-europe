from .biomass_route import BiomassRoute


class PerennialGrassesToBiomassSlowPyrolysis(BiomassRoute):
    """Dummy route of perennial_grasses into biomass_slow_pyrolysis."""

    name: str = "perennial_grasses_to_biomass_slow_pyrolysis"
    feedstock = "perennial_grasses"
    pool = "biomass_slow_pyrolysis"
