from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
from zen_creator import SourceInformation
from zen_creator.datasets.datasets.metadata import MetaData

from zen_europe.datasets.datasets.financial.ECB import ECBInflation

if TYPE_CHECKING:
    from zen_creator.model import Model

from zen_creator.elements import Carrier
from zen_creator.utils.attribute import Attribute


class Glycerine(Carrier):
    """Crude glycerol (glycerine), the by-product of biodiesel production by
    transesterification (FAME), in terms of the energy of the glycerol it
    contains.

    It can either be sold to the chemical industry (export at the market price
    of crude glycerine, which is refined there into pharmaceutical and cosmetic
    grade glycerine or converted into e.g. propylene glycol and epichlorohydrin)
    or be used as a co-substrate in anaerobic digestion (route into the wet
    biogas pool)."""

    name: str = "glycerine"

    # Market price of crude glycerine, Argus Glycerine, 1 October 2025:
    # "Veg. crude glycerine (80%) fca Europe bulk", 550-570 EUR/t
    PRICE_PER_TONNE_CRUDE = 560.0  # EUR/t crude glycerine, midpoint
    PRICE_MONEY_YEAR = 2025
    GLYCEROL_CONTENT = 0.80  # t glycerol / t crude glycerine (grade of the quote)
    # LHV of pure glycerol: HHV of 17.96 MJ/kg minus the condensation heat of the
    # 4 mol of water formed per mol of glycerol. Matches the glycerine output of
    # the DEA FAME data sheet (0.039 MWh per 0.903 MWh biodiesel, i.e. about
    # 0.1 t glycerol per t biodiesel).
    LHV = 16.06  # MJ/kg

    def __init__(self, model: Model, power_unit: str = "MW"):
        super().__init__(model=model, power_unit=power_unit)
        self.get_inflation_rate = ECBInflation(
            source_path=self.source_path
        ).get_inflation_rate

    def _set_availability_import(self) -> Attribute:
        """
        Return the import availability of glycerol. It is only produced as a
        by-product of FAME.
        """
        return Attribute(
            "availability_import",
            default_value=0,
            element=self,
            unit=self.power_unit,
        )

    def _set_availability_export(self) -> Attribute:
        """
        Return the export availability of glycerol. Unlimited, so all glycerol
        that is not digested can be sold to the chemical industry.
        """
        return Attribute(
            "availability_export",
            default_value=np.inf,
            element=self,
            unit=self.power_unit,
        )

    def _set_availability_export_yearly(self) -> Attribute:
        """
        Return the yearly export availability of glycerol (unlimited).
        """
        return Attribute(
            "availability_export_yearly",
            default_value=np.inf,
            element=self,
            unit=self.energy_unit,
        )

    def _set_price_export(self) -> Attribute:
        """
        Return the export price of glycerol, i.e. its value for the chemical
        industry.

        The price of crude glycerine (80% glycerol) is converted to the glycerol
        it contains, to an energy basis with the LHV of glycerol
        (16.06 MJ/kg = 4.46 MWh/t), and inflated to the price year.
        """
        attr = self.price_export
        euro_per_tonne_glycerol = self.PRICE_PER_TONNE_CRUDE / self.GLYCEROL_CONTENT
        inflation = self.get_inflation_rate(
            base_year=self.PRICE_MONEY_YEAR, target_year=self.settings.time.price_year
        )
        price = euro_per_tonne_glycerol / (self.LHV / 3.6) * inflation  # Euro/MWh
        return attr.set_data(
            default_value=price,
            unit="Euro/MWh",
            source=SourceInformation(
                description=(
                    "The export price of glycerol is its value for the chemical "
                    "industry. It is the Argus assessment of 1 October 2025 for "
                    "veg. crude glycerine (80%) fca Europe bulk (550-570 EUR/t, "
                    "midpoint 560 EUR/t), converted to the contained glycerol "
                    "(80%) and to an energy basis with the LHV of glycerol of "
                    "16.06 MJ/kg, and inflated to the price year. The price of "
                    "crude glycerine is volatile: it follows the biodiesel output "
                    "and was markedly lower in 2024."
                ),
                metadata=MetaData(
                    name="argus_glycerine",
                    title="Argus Glycerine, 1 October 2025 (sample report)",
                    author=["Argus Media"],
                    publication="Argus Glycerine",
                    publication_year=2025,
                    url=(
                        "https://view.argusmedia.com/rs/584-BUW-606/images/"
                        "CHE-Sample-Report-Argus%20Glycerine%20%282025-10-01%29.pdf"
                    ),
                ),
            ),
        )