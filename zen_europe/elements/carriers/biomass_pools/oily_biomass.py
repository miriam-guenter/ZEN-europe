from .biomass_pool import BiomassPool


class OilyBiomass(BiomassPool):
    """Crude vegetable oil for FAME and HVO, from crushing oilseeds
    (oil_crops_to_oily_biomass)."""

    name: str = "oily_biomass"
