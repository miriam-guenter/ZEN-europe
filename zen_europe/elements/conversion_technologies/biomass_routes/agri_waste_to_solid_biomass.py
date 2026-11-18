from .biomass_route import BiomassRoute


class AgriWasteToSolidBiomass(BiomassRoute):
    """Dummy route of agri_waste into solid_biomass."""

    name: str = "agri_waste_to_solid_biomass"
    feedstock = "agri_waste"
    pool = "solid_biomass"
