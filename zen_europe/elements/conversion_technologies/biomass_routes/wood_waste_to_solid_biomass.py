from .biomass_route import BiomassRoute


class WoodWasteToSolidBiomass(BiomassRoute):
    """Dummy route of wood_waste into solid_biomass."""

    name: str = "wood_waste_to_solid_biomass"
    feedstock = "wood_waste"
    pool = "solid_biomass"
