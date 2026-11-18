from .biomass_route import BiomassRoute


class PerennialGrassesToDryBiomassBiogas(BiomassRoute):
    """Dummy route of perennial_grasses into dry_biomass_biogas."""

    name: str = "perennial_grasses_to_dry_biomass_biogas"
    feedstock = "perennial_grasses"
    pool = "dry_biomass_biogas"
