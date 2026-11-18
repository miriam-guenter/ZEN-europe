from .biomass_route import BiomassRoute


class StemwoodToWoodyBiomass(BiomassRoute):
    """Dummy route of stemwood into woody_biomass."""

    name: str = "stemwood_to_woody_biomass"
    feedstock = "stemwood"
    pool = "woody_biomass"
