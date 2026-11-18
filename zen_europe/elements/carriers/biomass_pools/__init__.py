"""Aggregated (dummy) biomass carriers per use pathway, one carrier per file."""

from .biogas_feedstock import BiogasFeedstock
from .biomass_pool import BiomassPool
from .biomass_slow_pyrolysis import BiomassSlowPyrolysis
from .cellulosic_biomass import CellulosicBiomass
from .dry_biomass_biogas import DryBiomassBiogas
from .oily_biomass import OilyBiomass
from .solid_biomass import SolidBiomass
from .wet_biomass_biogas import WetBiomassBiogas
from .woody_biomass import WoodyBiomass

BIOMASS_POOLS = [
    SolidBiomass,
    WoodyBiomass,
    BiogasFeedstock,
    WetBiomassBiogas,
    DryBiomassBiogas,
    CellulosicBiomass,
    OilyBiomass,
    BiomassSlowPyrolysis,
]

__all__ = ["BiomassPool", "BIOMASS_POOLS"]
