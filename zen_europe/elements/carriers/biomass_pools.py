from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from zen_creator import Model

from zen_creator.elements import Carrier
from zen_creator.utils.attribute import Attribute


class BiomassPool(Carrier):
    """Base class for aggregated dummy biomass carriers. They cannot be
    imported and are only supplied by biomass routing technologies."""

    name: str = "biomass_pool"

    def __init__(self, model: Model, power_unit: str = "MW"):
        super().__init__(model=model, power_unit=power_unit)

    def _set_availability_import(self) -> Attribute:
        """Pools are only filled by routing technologies, never imported."""
        return Attribute(
            "availability_import", default_value=0, element=self, unit=self.power_unit
        )


class CombustionBiomass(BiomassPool):
    """Solid biomass for combustion in boilers."""

    name: str = "comb_biomass"

class GasificationBiomass(BiomassPool):
    """Solid biomass for gasification."""

    name: str = "gasif_biomass"

class WetBiomassBiogas(BiomassPool):
    """Wet biomass for anaerobic digestion."""

    name: str = "wet_biomass_biogas"


class DryBiomassBiogas(BiomassPool):
    """Dry biomass for anaerobic co-digestion."""

    name: str = "dry_biomass_biogas"


class CellulosicBiomass(BiomassPool):
    """Lignocellulosic biomass for cellulosic ethanol."""

    name: str = "cellulosic_biomass"


class OilyBiomass(BiomassPool):
    """Oily biomass for FAME and HVO."""

    name: str = "oily_biomass"


class BiomassSlowPyrolysis(BiomassPool):
    """Biomass for slow pyrolysis."""

    name: str = "biomass_slow_pyrolysis"


class BiomassFastPyrolysis(BiomassPool):
    """Biomass for fast pyrolysis."""

    name: str = "biomass_fast_pyrolysis"


BIOMASS_POOLS = [
    CombustionBiomass, GasificationBiomass,WetBiomassBiogas, DryBiomassBiogas,
    CellulosicBiomass, OilyBiomass, BiomassSlowPyrolysis, BiomassFastPyrolysis,
]