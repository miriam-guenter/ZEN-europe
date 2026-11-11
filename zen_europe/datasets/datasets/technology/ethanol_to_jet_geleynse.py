from __future__ import annotations

from pathlib import Path

import pandas as pd
from zen_creator import Attribute, ConversionTechnology
from zen_creator.datasets.datasets.dataset import Dataset
from zen_creator.datasets.datasets.metadata import MetaData, SourceInformation

from zen_europe.datasets.datasets.financial.ECB import ECBDollar2Euro, ECBInflation


class EthanolToJetGeleynse(Dataset[pd.Series]):
    """
    Dataset class for the upgrading of ethanol to jet fuel (alcohol-to-jet, ATJ),
    based on the core ethanol-to-jet model of Geleynse et al. (2018): dehydration
    to ethylene, oligomerization, hydrogenation and fractionation.

    The mass and energy balance is for the reference case of 200 t/day of ethanol
    (Table 11); the costs are for the case normalized to 36.3 kt of fuel per year,
    which takes 185 t/day of ethanol (Tables 3 to 6). All values are converted to
    the jet fuel output, the reference carrier. The liquid products are counted with
    one heating value, since their LHV per kg differs by less than 2%.
    """

    name = "ethanol_to_jet_geleynse"

    # Mass balance (Tables 2, 3 and 11)
    MASS_YIELD = 0.60  # kg liquid fuel / kg ethanol
    SHARE_GASOLINE = 0.10  # fuel product distribution, by mass (Table 2)
    SHARE_JET = 0.70
    SHARE_DIESEL = 0.20
    HYDROGEN_PER_ETHANOL = 1.1 / 185  # t hydrogen / t ethanol (Table 3)
    ETHANOL_FEED_REFERENCE = 308 * 0.4536 * 60 / 1000  # t/h, 308 lb/min (Table 11)
    ETHANOL_FEED_COSTS = 185 / 24  # t/h, 185 t/day (Table 3)
    UPTIME = 0.90  # Table 9
    # Utilities of the dehydration, oligomerization and hydrogenation units [MW]
    # for the reference feed (Table 11)
    ELECTRICITY = (1337 + 208 + 20) / 1000
    REFRIGERATION = 2196 / 1000  # at -50 degC
    STEAM = (1669 + 154 + 300) / 1000
    FIRED_GAS = (2137 + 1695) / 1000
    # Assumptions for the utility supply
    REFRIGERATION_COP = 1.5  # electric chillers at -50 degC
    BOILER_NATURAL_GAS_INPUT = 1.111  # MJ gas / MJ steam (JRC NG boiler, 90% LHV)
    BOILER_ELECTRICITY_INPUT = 0.020  # MJ electricity / MJ steam (JRC NG boiler)
    # Heating values [MJ/kg]
    LHV_ETHANOL = 26.81
    LHV_FUEL = 43.2  # jet fuel, also used for the gasoline and diesel cuts
    LHV_HYDROGEN = 120.0
    # Costs, 2015 USD, nth plant (Tables 5, 6 and 9)
    MONEY_YEAR = 2015
    FIXED_CAPITAL_INVESTMENT = 23.3e6  # USD, total capital investment minus working capital
    FIXED_OPEX = 2.9e6  # USD/year
    CATALYST_COST = 0.5e6  # USD/year
    LIFETIME = 20  # years
    CONSTRUCTION_TIME = 3  # years

    def __init__(self, source_path: Path | str | None = None):
        super().__init__(source_path=source_path)

    def _set_metadata(self) -> MetaData:
        return MetaData(
            name=self.name,
            title=(
                "The Alcohol-to-Jet Conversion Pathway for Drop-In Biofuels: "
                "Techno-Economic Evaluation"
            ),
            author=[
                "Scott Geleynse",
                "Kristin Brandt",
                "Manuel Garcia-Perez",
                "Michael Wolcott",
                "Xiao Zhang",
            ],
            publication="ChemSusChem",
            publication_year=2018,
            url="https://doi.org/10.1002/cssc.201801690",
            doi="https://doi.org/10.1002/cssc.201801690",
        )

    def _set_path(self) -> Path | None:
        if self.source_path is None:
            raise ValueError("source_path must be set to load the dataset.")
        return self.source_path

    def _set_data(self) -> pd.Series:
        """
        No data to be set.
        """
        data: dict[str, float] = {}
        return pd.Series(data)

    # -------- helpers ------------------------
    def _jet_output(self, ethanol_feed: float) -> float:
        """Jet fuel output [MW] for an ethanol feed [t/h]."""
        return ethanol_feed * self.MASS_YIELD * self.SHARE_JET * self.LHV_FUEL / 3.6

    def _to_price_year(self, element: ConversionTechnology) -> float:
        """Factor from 2015 USD to euro in the price year."""
        dollar2euro = ECBDollar2Euro(source_path=self.source_path).get_dollar2euro(
            self.MONEY_YEAR
        )
        inflation = ECBInflation(source_path=self.source_path).get_inflation_rate(
            base_year=self.MONEY_YEAR, target_year=element.settings.time.price_year
        )
        return dollar2euro * inflation

    def _source(self, description: str) -> SourceInformation:
        return SourceInformation(description=description, metadata=self.metadata)

    # -------- methods ------------------------
    def get_conversion_factor(self, element: ConversionTechnology) -> Attribute:
        """
        Get the conversion factor of ethanol to jet, per unit of jet fuel.

        The steam is supplied by a natural gas boiler and the refrigeration by
        electric chillers. The gasoline and diesel cuts are outputs.
        """
        feed = self.ETHANOL_FEED_REFERENCE
        jet = self._jet_output(feed)
        ethanol = feed * self.LHV_ETHANOL / 3.6
        hydrogen = feed * self.HYDROGEN_PER_ETHANOL * self.LHV_HYDROGEN / 3.6
        electricity = (
            self.ELECTRICITY
            + self.REFRIGERATION / self.REFRIGERATION_COP
            + self.STEAM * self.BOILER_ELECTRICITY_INPUT
        )
        natural_gas = self.FIRED_GAS + self.STEAM * self.BOILER_NATURAL_GAS_INPUT
        cf = [
            {"ethanol": {"default_value": ethanol / jet, "unit": "GWh/GWh"}},
            {"hydrogen": {"default_value": hydrogen / jet, "unit": "GWh/GWh"}},
            {"electricity": {"default_value": electricity / jet, "unit": "GWh/GWh"}},
            {"natural_gas": {"default_value": natural_gas / jet, "unit": "GWh/GWh"}},
            {
                "diesel": {
                    "default_value": self.SHARE_DIESEL / self.SHARE_JET,
                    "unit": "GWh/GWh",
                }
            },
            {
                "gasoline": {
                    "default_value": self.SHARE_GASOLINE / self.SHARE_JET,
                    "unit": "GWh/GWh",
                }
            },
        ]
        attr = element.conversion_factor
        attr.set_data(
            default_value=cf,
            source=self._source(
                "The conversion factor of ethanol to jet is derived from the core "
                "ethanol-to-jet model of Geleynse et al. (2018): mass yield of 0.60 kg "
                "fuel per kg ethanol, split 70% jet, 20% diesel and 10% gasoline by "
                "mass (Table 2), 1.1 t hydrogen per 185 t ethanol (Table 3) and the "
                "utilities of the conversion units (Table 11). Steam is supplied by a "
                "natural gas boiler (JRC, 90% efficiency) and the refrigeration at "
                "-50 degC by electric chillers (COP 1.5, assumption). All liquid "
                "products are counted with an LHV of 43.2 MJ/kg."
            ),
        )
        return attr

    def get_capex_specific_conversion(self, element: ConversionTechnology) -> Attribute:
        """
        Get the specific capex of ethanol to jet [Euro/kW jet fuel].

        The fixed capital investment (total capital investment without working
        capital) is divided by the jet fuel output capacity of the plant.
        """
        jet = self._jet_output(self.ETHANOL_FEED_COSTS) * 1000  # kW
        capex = self.FIXED_CAPITAL_INVESTMENT / jet * self._to_price_year(element)
        attr = element.capex_specific_conversion
        attr.set_data(
            default_value=capex,
            unit="Euro/kW",
            source=self._source(
                "The specific capex of ethanol to jet is the fixed capital investment "
                "of the core ethanol-to-jet model of Geleynse et al. (2018, Table 5, "
                "23.3 MUSD2015, nth plant) per kW of jet fuel output, converted to "
                "euro and inflated to the price year."
            ),
        )
        return attr

    def get_opex_specific_fixed(self, element: ConversionTechnology) -> Attribute:
        """
        Get the specific fixed opex of ethanol to jet [Euro/kW jet fuel/year].
        """
        jet = self._jet_output(self.ETHANOL_FEED_COSTS) * 1000  # kW
        opex = self.FIXED_OPEX / jet * self._to_price_year(element)
        attr = element.opex_specific_fixed
        attr.set_data(
            default_value=opex,
            unit="Euro/kW",
            source=self._source(
                "The specific fixed opex of ethanol to jet is the fixed operating "
                "cost of the core ethanol-to-jet model of Geleynse et al. (2018, "
                "Table 6, 2.9 MUSD2015 per year) per kW of jet fuel output, converted "
                "to euro and inflated to the price year."
            ),
        )
        return attr

    def get_opex_specific_variable(self, element: ConversionTechnology) -> Attribute:
        """
        Get the specific variable opex of ethanol to jet [Euro/MWh jet fuel].

        Only the catalyst cost is included; hydrogen and utilities are input
        carriers.
        """
        jet = self._jet_output(self.ETHANOL_FEED_COSTS)  # MW
        jet_per_year = jet * 8760 * self.UPTIME  # MWh/year
        opex = self.CATALYST_COST / jet_per_year * self._to_price_year(element)
        attr = element.opex_specific_variable
        attr.set_data(
            default_value=opex,
            unit="Euro/MWh",
            source=self._source(
                "The specific variable opex of ethanol to jet is the catalyst cost of "
                "the core ethanol-to-jet model of Geleynse et al. (2018, Table 6, 0.5 "
                "MUSD2015 per year) per MWh of jet fuel at 90% uptime, converted to "
                "euro and inflated to the price year. Hydrogen and utilities are "
                "modelled as input carriers."
            ),
        )
        return attr

    def get_lifetime(self, element: ConversionTechnology) -> Attribute:
        """
        Get the lifetime of ethanol to jet.
        """
        attr = element.lifetime
        attr.set_data(
            default_value=self.LIFETIME,
            unit="1",
            source=self._source(
                "The lifetime of ethanol to jet is the plant life of Geleynse et al. "
                "(2018, Table 9)."
            ),
        )
        return attr

    def get_construction_time(self, element: ConversionTechnology) -> Attribute:
        """
        Get the construction time of ethanol to jet.
        """
        attr = element.construction_time
        attr.set_data(
            default_value=self.CONSTRUCTION_TIME,
            unit="1",
            source=self._source(
                "The construction time of ethanol to jet is taken from Geleynse et al. "
                "(2018, Table 9)."
            ),
        )
        return attr