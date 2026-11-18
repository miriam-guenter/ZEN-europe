from .biomass_route import BiomassRoute


class SrcCropsToWoodyBiomass(BiomassRoute):
    """Dummy route of src_crops into woody_biomass."""

    name: str = "src_crops_to_woody_biomass"
    feedstock = "src_crops"
    pool = "woody_biomass"
