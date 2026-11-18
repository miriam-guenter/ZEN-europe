from .biomass_route import BiomassRoute


class WoodWasteToBiomassSlowPyrolysis(BiomassRoute):
    """Dummy route of wood_waste into biomass_slow_pyrolysis."""

    name: str = "wood_waste_to_biomass_slow_pyrolysis"
    feedstock = "wood_waste"
    pool = "biomass_slow_pyrolysis"
