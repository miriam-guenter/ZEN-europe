from .biomass_route import BiomassRoute


class OilseedMealToBiomassSlowPyrolysis(BiomassRoute):
    """Dummy route of oilseed_meal into biomass_slow_pyrolysis."""

    name: str = "oilseed_meal_to_biomass_slow_pyrolysis"
    feedstock = "oilseed_meal"
    pool = "biomass_slow_pyrolysis"
