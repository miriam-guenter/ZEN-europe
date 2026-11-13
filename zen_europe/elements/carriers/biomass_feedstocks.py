from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from zen_creator import Model

from zen_creator.elements import Carrier
from zen_creator.utils.attribute import Attribute

from zen_europe.datasets.datasets.carrier.enspreso_biomass import (
    EnspresoBiomassAvailability,
    EnspresoBiomassPrice,
)
from zen_europe.datasets.datasets.financial.ECB import ECBInflation

AGRW1_WOODY_SHARE = 0.1  # MINBIOAGRW1 -> woody (prunings) vs. herbaceous (straw) (based on MOPO data)
MUN1_BIOWASTE_SHARE = 0.7  # MINBIOMUN1 -> biowaste vs. wood waste (based on MOPO data)


class BiomassFeedstock(Carrier):
    """Base class for primary biomass feedstocks with ENSPRESO potentials and
    prices. Subclasses only set `name`, `_biomass_types` and, if needed,
    `_biomass_shares` / `_price_types`."""

    name: str = "biomass_feedstock"
    subpath: ClassVar[str] = "" # intermediate base class: adds no folder level to the output path

    # ENSPRESO energy-commodity codes belonging to this feedstock
    _biomass_types: ClassVar[list[str]] = []
    # share of a code assigned to this feedstock, for codes split across carriers
    _biomass_shares: ClassVar[dict[str, float]] = {}
    # codes used for the price; defaults to `_biomass_types`
    _price_types: ClassVar[list[str] | None] = None

    def __init__(self, model: Model, power_unit: str = "MW"):
        super().__init__(model=model, power_unit=power_unit)
        ecb = ECBInflation(source_path=self.source_path)
        self.get_inflation_rate = ecb.get_inflation_rate

    def _set_availability_import(self) -> Attribute:
        """Return the import availability from ENSPRESO potentials."""
        if self.settings.availability.annual_cap_biomass_import:
            return self.availability_import

        enspreso = EnspresoBiomassAvailability(self.source_path)
        attr = enspreso.get_availability_import(
            element=self, biomass_types=self._biomass_types, shares=self._biomass_shares
        )
        if self.settings.scenario.sensitivity_biomass:
            attr.add_scenarios(
                [
                    enspreso.get_availability_import_scenario(
                        element=self,
                        biomass_types=self._biomass_types,
                        shares=self._biomass_shares,
                        name="biomass_low",
                        ens_scenario="ENS_Low",
                        suffix="low",
                    ),
                    enspreso.get_availability_import_scenario(
                        element=self,
                        biomass_types=self._biomass_types,
                        shares=self._biomass_shares,
                        name="biomass_high",
                        ens_scenario="ENS_High",
                        suffix="high",
                    ),
                ]
            )
        return attr

    def _set_availability_import_yearly(self) -> Attribute:
        """Return the yearly import availability from ENSPRESO potentials."""
        if not self.settings.availability.annual_cap_biomass_import:
            return self.availability_import_yearly
        enspreso = EnspresoBiomassAvailability(self.source_path)
        return enspreso.get_availability_import_yearly(
            element=self, biomass_types=self._biomass_types, shares=self._biomass_shares
        )

    def _set_price_import(self) -> Attribute:
        """Return the import price from ENSPRESO prices."""
        enspreso = EnspresoBiomassPrice(self.source_path)
        return enspreso.get_price_import(
            element=self,
            biomass_types=self._price_types or self._biomass_types,
            regional_prices=self.settings.cost.use_nodal_biomass_prices,
        )


# ---------- Agriculture ----------
class StarchCrops(BiomassFeedstock):
    """Starch-based energy crops (barley, wheat, grain maize, oats, rye)."""

    name: str = "starch_crops"
    _biomass_types = ["MINBIOCRP11"]


class SugarCrops(BiomassFeedstock):
    """Sugar from sugar beet."""

    name: str = "sugar_crops"
    _biomass_types = ["MINBIOCRP21"]


class OilCrops(BiomassFeedstock):
    """Oilseeds (sunflower, soya, rape seed)."""

    name: str = "oil_crops"
    _biomass_types = ["MINBIOLIQ1", "MINBIORPS1"]


class PerennialGrasses(BiomassFeedstock):
    """Lignocellulosic-herbaceous energy crops (miscanthus, switchgrass, RCG)."""

    name: str = "perennial_grasses"
    _biomass_types = ["MINBIOCRP31"]


class SRCCrops(BiomassFeedstock):
    """Lignocellulosic-woody energy crops, short rotation coppice (willow, poplar)."""

    name: str = "src_crops"
    _biomass_types = ["MINBIOCRP41", "MINBIOCRP41a"]


class Manure(BiomassFeedstock):
    """Manure, solid and liquid."""

    name: str = "manure"
    _biomass_types = ["MINBIOGAS1"]


class AgriResiduesWoody(BiomassFeedstock):
    """Woody agricultural residues (prunings, olive stones)."""

    name: str = "agri_residues_woody"
    _biomass_types = ["MINBIOAGRW1"]
    _biomass_shares = {"MINBIOAGRW1": AGRW1_WOODY_SHARE}


class AgriResiduesHerb(BiomassFeedstock):
    """Herbaceous agricultural residues (straw, stubble) and landscape care."""

    name: str = "agri_residues_herb"
    _biomass_types = ["MINBIOAGRW1", "MINBIOFRSR1a"]
    _biomass_shares = {"MINBIOAGRW1": 1 - AGRW1_WOODY_SHARE}


# ---------- Forestry ----------
class Stemwood(BiomassFeedstock):
    """Fuelwood, chips and pellets from roundwood."""

    name: str = "stemwood"
    _biomass_types = ["MINBIOWOO", "MINBIOWOOa"]


class ForestryResidues(BiomassFeedstock):
    """Primary and secondary forestry residues (woodchips, sawdust)."""

    name: str = "forestry_residues"
    _biomass_types = ["MINBIOFRSR1", "MINBIOWOOW1", "MINBIOWOOW1a"]


# ---------- Waste ----------
class Biowaste(BiomassFeedstock):
    """Biodegradable municipal and industrial waste."""

    name: str = "biowaste"
    _biomass_types = ["MINBIOMUN1"]
    _biomass_shares = {"MINBIOMUN1": MUN1_BIOWASTE_SHARE}


class WoodWaste(BiomassFeedstock):
    """Waste wood."""

    name: str = "wood_waste"
    _biomass_types = ["MINBIOMUN1"]
    _biomass_shares = {"MINBIOMUN1": 1 - MUN1_BIOWASTE_SHARE}


class Sludge(BiomassFeedstock):
    """Sewage sludge."""

    name: str = "sludge"
    _biomass_types = ["MINBIOSLU1"]


BIOMASS_FEEDSTOCKS = [
    StarchCrops, SugarCrops, OilCrops, PerennialGrasses, SRCCrops, Manure,
    AgriResiduesWoody, AgriResiduesHerb, Stemwood, ForestryResidues,
    Biowaste, WoodWaste, Sludge,
]