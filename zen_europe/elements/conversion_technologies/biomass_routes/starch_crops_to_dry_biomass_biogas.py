from .biomass_route import BiomassRoute


class StarchCropsToDryBiomassBiogas(BiomassRoute):
    """Dummy route of starch_crops into dry_biomass_biogas."""

    name: str = "starch_crops_to_dry_biomass_biogas"
    feedstock = "starch_crops"
    pool = "dry_biomass_biogas"
