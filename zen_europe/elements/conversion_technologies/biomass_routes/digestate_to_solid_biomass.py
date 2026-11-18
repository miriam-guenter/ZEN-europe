from .biomass_route import BiomassRoute


class DigestateToSolidBiomass(BiomassRoute):
    """Dummy route of digestate into solid_biomass."""

    name: str = "digestate_to_solid_biomass"
    feedstock = "digestate"
    pool = "solid_biomass"
