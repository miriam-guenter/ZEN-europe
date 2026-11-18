from .biomass_pool import BiomassPool


class CellulosicBiomass(BiomassPool):
    """Lignocellulosic biomass for cellulosic ethanol."""

    name: str = "cellulosic_biomass"
