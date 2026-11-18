from .biomass_pool import BiomassPool


class BiogasFeedstock(BiomassPool):
    """Mixed feedstock for anaerobic digestion (wet biomass with at most the
    maximum share of dry biomass)."""

    name: str = "biogas_feedstock"
