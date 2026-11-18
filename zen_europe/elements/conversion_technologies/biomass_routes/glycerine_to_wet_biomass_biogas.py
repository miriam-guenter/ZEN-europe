from .biomass_route import BiomassRoute


class GlycerineToWetBiomassBiogas(BiomassRoute):
    """Dummy route of glycerine into wet_biomass_biogas."""

    name: str = "glycerine_to_wet_biomass_biogas"
    feedstock = "glycerine"
    pool = "wet_biomass_biogas"
