from .biomass_route import BiomassRoute


class BiowasteToWetBiomassBiogas(BiomassRoute):
    """Dummy route of biowaste into wet_biomass_biogas."""

    name: str = "biowaste_to_wet_biomass_biogas"
    feedstock = "biowaste"
    pool = "wet_biomass_biogas"
