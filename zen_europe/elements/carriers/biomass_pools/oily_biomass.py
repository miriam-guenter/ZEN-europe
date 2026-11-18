from .biomass_pool import BiomassPool


class OilyBiomass(BiomassPool):
    """Oily biomass for FAME and HVO."""

    name: str = "oily_biomass"
