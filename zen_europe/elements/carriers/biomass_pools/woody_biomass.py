from .biomass_pool import BiomassPool


class WoodyBiomass(BiomassPool):
    """Clean woody biomass (logs, chips, pellets) for decentralized heating
    boilers and fast pyrolysis."""

    name: str = "woody_biomass"
