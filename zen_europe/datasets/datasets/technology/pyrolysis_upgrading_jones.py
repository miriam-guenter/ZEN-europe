from __future__ import annotations

from pathlib import Path

import pandas as pd
from zen_creator import Attribute, ConversionTechnology
from zen_creator.datasets.datasets.dataset import Dataset
from zen_creator.datasets.datasets.metadata import MetaData, SourceInformation

from zen_europe.datasets.datasets.financial.ECB import ECBDollar2Euro, ECBInflation


class PyrolysisUpgradingJones(Dataset[pd.Series]):
    """
    Dataset class for the upgrading of fast pyrolysis oil to hydrocarbon fuel
    (stabilization, two-stage hydrotreating, hydrocracking and product
    separation), based on the PNNL/NREL design case of Jones et al. (2013) for
    2000 dry t/day of wood.

    Only the upgrading areas are kept: area 200 (hydrotreating) and areas 300-500
    (hydrocracking and product finishing), plus their share of the balance of
    plant. Fast pyrolysis (area 100) is a separate technology in the model, and
    the hydrogen generation (area 600) is replaced by hydrogen as input carrier,
    so that the hydrogen demand is supplied by the hydrogen sector. All values are
    converted to the hydrocarbon fuel output (gasoline and diesel blendstock),
    which is modelled as oil.
    """

    name = "pyrolysis_upgrading_jones"

    # Unit conversions
    LB_TO_KG = 0.45359237
    BBL_TO_M3 = 0.158987
    BTU_TO_GJ = 1.05506e-6
    # Plant performance
    BIOMASS_FEED = 2205  # dry US tons/day (2000 t/day)
    FUEL_YIELD = 10.1e6  # BTU (LHV) fuel per dry US ton (Figure ES-1)
    FUEL_PRODUCTION = (28.9 + 31.6) * 1e6  # gal/yr gasoline + diesel (Figure ES-1)
    STREAM_HOURS = 7884  # h/yr, 90% on-stream factor (Table 1)
    # Pyrolysis oil feed to the stabilizer: 8,800 bbl/day wet oil (Table 8) at a
    # density of 1.2 t/m3 (Table 5)
    PYROLYSIS_OIL_FEED = 8800  # bbl/day
    PYROLYSIS_OIL_DENSITY = 1.2  # t/m3
    # LHV of fast pyrolysis oil from wood, from the DEA catalogue that defines the
    # pyrolysis_oil carrier of the fast pyrolysis technology
    LHV_PYROLYSIS_OIL = 16.0  # GJ/t
    # Hydrogen supplied to the hydrotreaters: 9,841 lb/h of pure hydrogen
    # (section 5.1), at an LHV of 120 MJ/kg
    HYDROGEN_SUPPLY = 9841  # lb/h
    LHV_HYDROGEN = 120.0  # MJ/kg
    ELECTRICITY = 1.27  # kWh purchased / gal blendstock (Figure ES-1)
    # Costs, 2011 USD (Tables 15 and 16, Figure ES-1)
    MONEY_YEAR = 2011
    FCI_UPGRADING = 198 + 32  # MUSD, hydrotreating + product finishing
    FCI_BALANCE_OF_PLANT = 16  # MUSD
    FCI_TOTAL = 665  # MUSD
    MAINTENANCE_INSURANCE = 0.03 + 0.007  # share of fixed capital investment/yr
    LABOUR_AND_OVERHEAD = 4.055 + 3.649  # MUSD/yr, whole plant
    CATALYSTS_AND_CHEMICALS = 20.4  # MUSD/yr
    LIFETIME = 30  # years (Table 1)
    CONSTRUCTION_TIME = 3  # years (Table 1)

    def __init__(self, source_path: Path | str | None = None):
        super().__init__(source_path=source_path)

    def _set_metadata(self) -> MetaData:
        return MetaData(
            name=self.name,
            title=(
                "Process Design and Economics for the Conversion of "
                "Lignocellulosic Biomass to Hydrocarbon Fuels: Fast Pyrolysis and "
                "Hydrotreating Bio-oil Pathway"
            ),
            author=[
                "Susanne Jones",
                "Pimphan Meyer",
                "Lesley Snowden-Swan",
                "Asanga Padmaperuma",
                "Eric Tan",
                "Abhijit Dutta",
                "Jacob Jacobson",
                "Kara Cafferty",
            ],
            publication="PNNL-23053, NREL/TP-5100-61178",
            publication_year=2013,
            url=(
                "https://www.pnnl.gov/main/publications/external/technical_reports/"
                "PNNL-23053.pdf"
            ),
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
    def _fuel_output(self) -> float:
        """Hydrocarbon fuel output (LHV) of the design plant [MW]."""
        gj_per_day = self.BIOMASS_FEED * self.FUEL_YIELD * self.BTU_TO_GJ
        return gj_per_day / 24 / 3.6

    def _pyrolysis_oil_input(self) -> float:
        """Pyrolysis oil feed of the design plant [MW]."""
        t_per_day = (
            self.PYROLYSIS_OIL_FEED * self.BBL_TO_M3 * self.PYROLYSIS_OIL_DENSITY
        )
        return t_per_day * self.LHV_PYROLYSIS_OIL / 24 / 3.6

    def _hydrogen_input(self) -> float:
        """Hydrogen supply of the design plant [MW]."""
        return self.HYDROGEN_SUPPLY * self.LB_TO_KG * self.LHV_HYDROGEN / 3600

    def _electricity_input(self) -> float:
        """Purchased electricity of the design plant [MW]."""
        return self.ELECTRICITY * self.FUEL_PRODUCTION / self.STREAM_HOURS / 1000

    def _fci_upgrading(self) -> float:
        """Fixed capital investment of the upgrading areas incl. their share of
        the balance of plant [USD]."""
        share = self.FCI_UPGRADING / (self.FCI_TOTAL - self.FCI_BALANCE_OF_PLANT)
        return (self.FCI_UPGRADING + share * self.FCI_BALANCE_OF_PLANT) * 1e6

    def _to_price_year(self, element: ConversionTechnology) -> float:
        """Factor from 2011 USD to euro in the price year."""
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
        Get the conversion factor of pyrolysis oil upgrading, per unit of fuel.
        """
        fuel = self._fuel_output()
        cf = [
            {
                "pyrolysis_oil": {
                    "default_value": self._pyrolysis_oil_input() / fuel,
                    "unit": "GWh/GWh",
                }
            },
            {
                "hydrogen": {
                    "default_value": self._hydrogen_input() / fuel,
                    "unit": "GWh/GWh",
                }
            },
            {
                "electricity": {
                    "default_value": self._electricity_input() / fuel,
                    "unit": "GWh/GWh",
                }
            },
        ]
        attr = element.conversion_factor
        attr.set_data(
            default_value=cf,
            source=self._source(
                "The conversion factor of pyrolysis oil upgrading is derived from "
                "the fast pyrolysis and hydrotreating design case of Jones et al. "
                "(2013) for 2000 dry t/day of wood. Fuel output: 10.1 MMBtu (LHV) "
                "per dry US ton of wood (Figure ES-1). Pyrolysis oil: 8,800 bbl/day "
                "of wet oil fed to the stabilizer (Table 8) at 1.2 t/m3 (Table 5), "
                "counted with 16 GJ/t as in the DEA fast pyrolysis data that "
                "defines the pyrolysis oil carrier. Hydrogen: 9,841 lb/h supplied "
                "to the hydrotreaters (section 5.1); the on-site hydrogen plant is "
                "replaced by hydrogen from the hydrogen sector. Electricity: 1.27 "
                "kWh per gallon of blendstock purchased from the grid (Figure "
                "ES-1), fully allocated to the upgrading."
            ),
        )
        return attr

    def get_capex_specific_conversion(self, element: ConversionTechnology) -> Attribute:
        """
        Get the specific capex of pyrolysis oil upgrading [Euro/kW fuel].
        """
        capex = (
            self._fci_upgrading()
            / (self._fuel_output() * 1000)
            * self._to_price_year(element)
        )
        attr = element.capex_specific_conversion
        attr.set_data(
            default_value=capex,
            unit="Euro/kW",
            source=self._source(
                "The specific capex of pyrolysis oil upgrading is the fixed capital "
                "investment of hydrotreating (198 MUSD2011) and product finishing "
                "(32 MUSD2011) plus their pro-rata share of the balance of plant "
                "(Jones et al., 2013, Table 16), per kW of fuel output, converted "
                "to euro and inflated to the price year. Fast pyrolysis and "
                "hydrogen generation are excluded."
            ),
        )
        return attr

    def get_opex_specific_fixed(self, element: ConversionTechnology) -> Attribute:
        """
        Get the specific fixed opex of pyrolysis oil upgrading [Euro/kW fuel/year].

        Maintenance (3%) and insurance and taxes (0.7%) of the fixed capital
        investment, plus the share of labour and overhead of the upgrading areas.
        """
        fci = self._fci_upgrading()
        labour_share = fci / (self.FCI_TOTAL * 1e6)
        opex = (
            self.MAINTENANCE_INSURANCE * fci
            + labour_share * self.LABOUR_AND_OVERHEAD * 1e6
        )
        opex = opex / (self._fuel_output() * 1000) * self._to_price_year(element)
        attr = element.opex_specific_fixed
        attr.set_data(
            default_value=opex,
            unit="Euro/kW",
            source=self._source(
                "The specific fixed opex of pyrolysis oil upgrading is 3% "
                "maintenance plus 0.7% insurance and taxes of the fixed capital "
                "investment, plus the share of salaries and overhead of the "
                "upgrading areas in the fixed capital investment (Jones et al., "
                "2013, Table 15), per kW of fuel output, converted to euro and "
                "inflated to the price year."
            ),
        )
        return attr

    def get_opex_specific_variable(self, element: ConversionTechnology) -> Attribute:
        """
        Get the specific variable opex of pyrolysis oil upgrading [Euro/MWh fuel].

        Only catalysts and chemicals are included; hydrogen and electricity are
        input carriers.
        """
        fuel_per_year = self._fuel_output() * self.STREAM_HOURS  # MWh/yr
        opex = (
            self.CATALYSTS_AND_CHEMICALS
            * 1e6
            / fuel_per_year
            * self._to_price_year(element)
        )
        attr = element.opex_specific_variable
        attr.set_data(
            default_value=opex,
            unit="Euro/MWh",
            source=self._source(
                "The specific variable opex of pyrolysis oil upgrading is the cost "
                "of catalysts and chemicals (20.4 MUSD2011 per year, Jones et al., "
                "2013, Figure ES-1) per MWh of fuel at 7884 h/yr, converted to "
                "euro and inflated to the price year. Hydrogen and electricity are "
                "modelled as input carriers."
            ),
        )
        return attr

    def get_lifetime(self, element: ConversionTechnology) -> Attribute:
        """
        Get the lifetime of pyrolysis oil upgrading.
        """
        attr = element.lifetime
        attr.set_data(
            default_value=self.LIFETIME,
            unit="1",
            source=self._source(
                "The lifetime of pyrolysis oil upgrading is the plant life of "
                "Jones et al. (2013, Table 1)."
            ),
        )
        return attr

    def get_construction_time(self, element: ConversionTechnology) -> Attribute:
        """
        Get the construction time of pyrolysis oil upgrading.
        """
        attr = element.construction_time
        attr.set_data(
            default_value=self.CONSTRUCTION_TIME,
            unit="1",
            source=self._source(
                "The construction time of pyrolysis oil upgrading is the "
                "construction period of Jones et al. (2013, Table 1)."
            ),
        )
        return attr
