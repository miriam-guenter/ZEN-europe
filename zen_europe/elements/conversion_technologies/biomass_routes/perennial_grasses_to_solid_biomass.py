from .biomass_route import BiomassRoute


class PerennialGrassesToSolidBiomass(BiomassRoute):
    """Dummy route of perennial_grasses into solid_biomass."""

    name: str = "perennial_grasses_to_solid_biomass"
    feedstock = "perennial_grasses"
    pool = "solid_biomass"
