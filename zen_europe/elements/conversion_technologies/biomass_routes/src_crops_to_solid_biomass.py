from .biomass_route import BiomassRoute


class SrcCropsToSolidBiomass(BiomassRoute):
    """Dummy route of src_crops into solid_biomass."""

    name: str = "src_crops_to_solid_biomass"
    feedstock = "src_crops"
    pool = "solid_biomass"
