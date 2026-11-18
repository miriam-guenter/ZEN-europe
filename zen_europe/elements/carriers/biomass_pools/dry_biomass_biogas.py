from .biomass_pool import BiomassPool


class DryBiomassBiogas(BiomassPool):
    """Dry biomass for anaerobic co-digestion."""

    name: str = "dry_biomass_biogas"
