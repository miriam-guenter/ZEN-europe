from .biomass_route import BiomassRoute


class OilCropsToOilyBiomass(BiomassRoute):
    """Dummy route of oil_crops into oily_biomass."""

    name: str = "oil_crops_to_oily_biomass"
    feedstock = "oil_crops"
    pool = "oily_biomass"
