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


class BiomassFeedstock(Carrier):
    """Base class for primary biomass feedstocks with ENSPRESO potentials and
    prices. Subclasses only set `name`, `_biomass_types` and, if needed,
    `_biomass_shares` / `_price_types`."""

    name: str = "biomass_feedstock"
    # intermediate base class: adds no folder level to the output path
    subpath: ClassVar[str] = ""

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
