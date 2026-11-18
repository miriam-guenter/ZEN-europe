from .biomass_route import BiomassRoute


class AgriWasteToCellulosicBiomass(BiomassRoute):
    """Dummy route of agri_waste into cellulosic_biomass."""

    name: str = "agri_waste_to_cellulosic_biomass"
    feedstock = "agri_waste"
    pool = "cellulosic_biomass"
