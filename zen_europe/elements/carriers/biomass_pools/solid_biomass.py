from .biomass_pool import BiomassPool


class SolidBiomass(BiomassPool):
    """Solid biomass for combustion (power plants, CHP, district heating
    boilers, cement kilns) and gasification (syngas, hydrogen, Fischer-Tropsch,
    methanol)."""

    name: str = "solid_biomass"
