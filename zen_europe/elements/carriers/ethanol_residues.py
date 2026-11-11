from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
from zen_creator import AssumptionInformation

from zen_europe.datasets.datasets.financial.ECB import ECBDollar2Euro, ECBInflation

if TYPE_CHECKING:
    from zen_creator.model import Model

from zen_creator.elements import Carrier
from zen_creator.utils.attribute import Attribute


class EthanolResidues(Carrier):
    """Wet by-products of first generation ethanol, in terms of their energy
    content: whole stillage from grain (the distillers' grains before drying) and
    pressed pulp from sugar beet.

    They are not dried. They can either be sold as wet animal feed (export at the
    feed price) or be used in anaerobic digestion (route into the wet biogas
    pool)."""

    name: str = "ethanol_residues"

    # Feed value, from the 2024 EU trade value of beet pulp (IndexBox, Europe's
    # beet-pulp and bagasse market overview 2024): midpoint of the average
    # intra-EU export price (148 USD/t) and import price (192 USD/t)
    PRICE_PER_TONNE_USD = 170.0  # USD/t of dried pulp
    PRICE_MONEY_YEAR = 2024
    # LHV of dried pulp at 9% water (JRC, Edwards et al., 2019, Table 134)
    LHV = 14.4  # GJ/t

    def __init__(self, model: Model, power_unit: str = "MW"):
        super().__init__(model=model, power_unit=power_unit)
        self.get_inflation_rate = ECBInflation(
            source_path=self.source_path
        ).get_inflation_rate
        self.get_dollar2euro = ECBDollar2Euro(
            source_path=self.source_path
        ).get_dollar2euro

    def _set_availability_import(self) -> Attribute:
        """
        Return the import availability of ethanol residues. They are only
        produced by first generation ethanol.
        """
        return Attribute(
            "availability_import",
            default_value=0,
            element=self,
            unit=self.power_unit,
        )

    def _set_availability_export(self) -> Attribute:
        """
        Return the export availability of ethanol residues. Unlimited, so all
        residues that are not digested can be sold as animal feed.
        """
        return Attribute(
            "availability_export",
            default_value=np.inf,
            element=self,
            unit=self.power_unit,
        )

    def _set_availability_export_yearly(self) -> Attribute:
        """
        Return the yearly export availability of ethanol residues (unlimited).
        """
        return Attribute(
            "availability_export_yearly",
            default_value=np.inf,
            element=self,
            unit=self.energy_unit,
        )

    def _set_price_export(self) -> Attribute:
        """
        Return the export price of ethanol residues, i.e. their value as animal
        feed.

        Wet and dried distillers' grains sell at about the same price per tonne of
        dry matter, so the feed value per unit of energy is taken from the dried
        product. The beet pulp price per tonne is converted to euro, to an energy
        basis with the LHV of dried pulp (14.4 GJ/t = 4.0 MWh/t), and inflated to
        the price year. The same price is used for the residues of grain.
        """
        attr = self.price_export
        euro_per_tonne = self.PRICE_PER_TONNE_USD * self.get_dollar2euro(
            self.PRICE_MONEY_YEAR
        )
        inflation = self.get_inflation_rate(
            base_year=self.PRICE_MONEY_YEAR, target_year=self.settings.time.price_year
        )
        price = euro_per_tonne / (self.LHV / 3.6) * inflation  # Euro/MWh
        return attr.set_data(
            default_value=price,
            unit="Euro/MWh",
            source=AssumptionInformation(
                description=(
                    "The export price of ethanol residues is their value as animal "
                    "feed. It is based on the 2024 EU trade value of beet pulp "
                    "(IndexBox: midpoint of the intra-EU export price of 148 USD/t "
                    "and import price of 192 USD/t), converted with the LHV of "
                    "dried pulp of 14.4 GJ/t (JRC, Edwards et al., 2019) and "
                    "inflated to the price year. Wet and dried distillers' grains "
                    "sell at about the same price per tonne of dry matter "
                    "(University of Nebraska-Lincoln), so the same price per unit "
                    "of energy is used for the wet residues of grain and sugar beet."
                ),
            ),
        )