from .biomass_pool import BiomassPool


class WetBiomassBiogas(BiomassPool):
    """Wet biomass for anaerobic digestion."""

    name: str = "wet_biomass_biogas"
