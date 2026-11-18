from .biomass_route import BiomassRoute


class PerennialGrassesToCellulosicBiomass(BiomassRoute):
    """Dummy route of perennial_grasses into cellulosic_biomass."""

    name: str = "perennial_grasses_to_cellulosic_biomass"
    feedstock = "perennial_grasses"
    pool = "cellulosic_biomass"
