from .biomass_route import BiomassRoute


class StemwoodToSolidBiomass(BiomassRoute):
    """Dummy route of stemwood into solid_biomass."""

    name: str = "stemwood_to_solid_biomass"
    feedstock = "stemwood"
    pool = "solid_biomass"
