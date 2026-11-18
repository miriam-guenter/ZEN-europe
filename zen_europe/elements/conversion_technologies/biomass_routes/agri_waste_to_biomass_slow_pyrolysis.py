from .biomass_route import BiomassRoute


class AgriWasteToBiomassSlowPyrolysis(BiomassRoute):
    """Dummy route of agri_waste into biomass_slow_pyrolysis."""

    name: str = "agri_waste_to_biomass_slow_pyrolysis"
    feedstock = "agri_waste"
    pool = "biomass_slow_pyrolysis"
