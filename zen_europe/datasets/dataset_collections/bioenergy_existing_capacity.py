from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, cast

import pandas as pd
from zen_creator import Attribute, ConversionTechnology, DatasetCollection
from zen_creator.utils.attribute import SourceInformation
from zen_creator.utils.settings import Settings

from zen_europe.datasets.datasets.carrier.eurostat import Eurostat
from zen_europe.datasets.datasets.technology.bfe_renewable_energy_statistics import (
    BFERenewableEnergyStatistics,
)
from zen_europe.utils.constants import Constants
from zen_europe.utils.utils import (
    calculate_capacity_addition_from_cumulative,
    format_capacity_existing,
)

if TYPE_CHECKING:
    from pathlib import Path

    from zen_creator import Dataset


class BioenergyExistingCapacity(DatasetCollection):
    """
    Existing capacity of anaerobic digestion, first generation ethanol and FAME.

    Eurostat gives a yearly time series per country (biogas production from
    anaerobic digestion, and the production capacity for biogasoline and
    biodiesels). The series is turned into capacity [GW of the reference carrier]
    and split into construction years with the yearly increments, as for the
    photovoltaics capacity from IRENA.

    Countries Eurostat does not cover:
    - UK: Eurostat stops in 2019. The 2019 values are kept for later years.
    - CH: biogas from the Swiss statistics of renewable energy (BFE). Switzerland
      has no domestic bioethanol production and a negligible biodiesel production,
      so both are zero.
    """

    name = "bioenergy_existing_capacity"

    # Biogas plants run almost continuously, so the biogas production is converted
    # to digester capacity with 8000 full load hours (about 91% availability).
    FULL_LOAD_HOURS_ANAEROBIC_DIGESTION = 8000

    # Swiss domestic biodiesel production in 2024 (BFE, Annex B 8.2): 13.5 million
    # litres, about 0.01 GW, below the relevance threshold of this model.
    SWISS_LIQUID_BIOFUEL_CAPACITY = 0.0

    # Share of the ethanol produced in Europe in 2024 by feedstock (ePURE key figures
    # 2024): corn 49.6%, wheat 23.4% and other cereals and starch-rich crops 5.1% are
    # starch, sugars 11.9%. The remaining 10% (lignocellulosic, RED Annex IX-A and
    # other feedstocks) is left out and the shares are renormalised, since commercial
    # cellulosic ethanol capacity in Europe is negligible.
    # https://www.epure.org/wp-content/uploads/2025/09/250908-DEF-PR-European-renewable-ethanol-Key-figures-2024.pdf
    ETHANOL_FEEDSTOCK_SHARES = {
        "ethanol_1G_starch": 0.496 + 0.234 + 0.051,
        "ethanol_1G_sugar": 0.119,
    }

    def __init__(self, settings: Settings, source_path: Path | str):
        self.settings = settings
        super().__init__(source_path=source_path)

    def _get_data(self) -> Dict[str, Dataset[Any] | DatasetCollection]:
        """Load all available data sources."""
        if self.source_path is None:
            raise ValueError("source_path must be set to load the dataset collection.")
        return {
            "eurostat": Eurostat(self.settings, self.source_path),
            "bfe": BFERenewableEnergyStatistics(self.source_path),
        }

    # -------- outward facing methods ------------------
    def get_capacity_existing_anaerobic_digestion(
        self, element: ConversionTechnology
    ) -> Attribute:
        """
        Existing capacity of anaerobic digestion [GW biogas].

        The biogas production from anaerobic digestion (sewage sludge gas and other
        biogases from anaerobic fermentation, without landfill gas) divided by
        8000 full load hours. Switzerland is taken from the BFE statistics, with
        linear interpolation between the years it reports.

        Args:
            element: the anaerobic digestion technology.

        Returns:
            Attribute: the existing capacity attribute of the element.
        """
        assert element.name == "anaerobic_digestion", (
            "This method is only applicable to anaerobic digestion."
        )
        nodes = self._get_nodes(element)
        eurostat = cast(Eurostat, self.data["eurostat"])
        production = eurostat.get_biogas_production_digestion(geo=tuple(nodes))
        production = self._clean_time_series(production, element)

        if "CH" in nodes:
            bfe = cast(BFERenewableEnergyStatistics, self.data["bfe"])
            swiss = bfe.get_biogas_production_digestion()
            swiss = swiss.reindex(production.columns).interpolate(limit_area="inside")
            production.loc["CH"] = swiss.ffill().fillna(0)

        cumulative = production / self.FULL_LOAD_HOURS_ANAEROBIC_DIGESTION
        capacity_existing = self._to_capacity_existing(cumulative, nodes, element)
        source = SourceInformation(
            description=(
                "The existing capacity of anaerobic digestion is the biogas "
                "production from anaerobic digestion (Eurostat nrg_cb_rw: sewage "
                "sludge gas R5312 and other biogases from anaerobic fermentation "
                "R5319; landfill gas is excluded) divided by "
                f"{self.FULL_LOAD_HOURS_ANAEROBIC_DIGESTION} full load hours. Where "
                "Eurostat reports only the biogas total (R5300) for the latest year, "
                "the country's latest share of digestion biogas is applied to it. "
                "Construction years follow the yearly increase of the production. "
                "The UK values are held at 2019, the last year in Eurostat. "
                "Switzerland is taken from the Swiss statistics of renewable "
                "energy (BFE, Annex B: biogas used on site plus grid injection, "
                "without landfill gas)."
            ),
            metadata=self.metadata,
        )
        return element.capacity_existing.set_data(
            df=capacity_existing, source=source, unit="GW"
        )

    def get_capacity_existing_ethanol(self, element: ConversionTechnology) -> Attribute:
        """
        Existing capacity of first generation ethanol [GW ethanol].

        The Eurostat production capacity for biogasoline, split between starch and
        sugar with the 2024 ePURE production shares by feedstock.

        Args:
            element: ethanol_1G_starch or ethanol_1G_sugar.

        Returns:
            Attribute: the existing capacity attribute of the element.
        """
        shares = self.ETHANOL_FEEDSTOCK_SHARES
        assert element.name in shares, (
            f"This method is only applicable to {list(shares)}."
        )
        nodes = self._get_nodes(element)
        capacity_kt = self._get_liquid_biofuel_capacity("R5210P", nodes, element)

        share = shares[element.name] / sum(shares.values())
        # kt/year * kWh/kg = GWh/year
        energy = capacity_kt * Constants.ETHANOL_KWH_PER_KG
        cumulative = energy / Constants.HOURS_PER_YEAR * share
        capacity_existing = self._to_capacity_existing(cumulative, nodes, element)
        feedstock = "starch" if element.name == "ethanol_1G_starch" else "sugar"
        source = SourceInformation(
            description=(
                "The existing capacity of first generation ethanol is the Eurostat "
                "production capacity for biogasoline (nrg_inf_lbpc, R5210P), "
                "converted with the lower heating value of ethanol (27 MJ/kg, RED "
                f"II). The {feedstock} share ({share:.1%}) is the share of "
                f"{feedstock} based ethanol in the first generation ethanol produced "
                "in Europe in 2024 (ePURE, European renewable ethanol - Key figures "
                "2024, https://www.epure.org/wp-content/uploads/2025/09/"
                "250908-DEF-PR-European-renewable-ethanol-Key-figures-2024.pdf; "
                "lignocellulosic and other feedstocks are left out and the rest "
                "renormalised). It is applied "
                "to every country. Construction years follow the yearly increase of "
                "the capacity. The UK values are held at 2019, the last year in "
                "Eurostat. Switzerland has no domestic bioethanol production (BFE)."
            ),
            metadata=self.metadata,
        )
        return element.capacity_existing.set_data(
            df=capacity_existing, source=source, unit="GW"
        )

    def get_capacity_existing_FAME(self, element: ConversionTechnology) -> Attribute:
        """
        Existing capacity of FAME biodiesel [GW diesel].

        The Eurostat production capacity for biodiesels.

        TODO: Eurostat's biodiesels include HVO. Subtract the HVO plant capacity
        once the existing capacity of HVO_diesel is implemented.

        Args:
            element: the FAME technology.

        Returns:
            Attribute: the existing capacity attribute of the element.
        """
        assert element.name == "FAME", "This method is only applicable to FAME."
        nodes = self._get_nodes(element)
        capacity_kt = self._get_liquid_biofuel_capacity("R5220P", nodes, element)
        cumulative = (
            capacity_kt * Constants.BIODIESEL_KWH_PER_KG / Constants.HOURS_PER_YEAR
        )  # kt/year * kWh/kg = GWh/year
        capacity_existing = self._to_capacity_existing(cumulative, nodes, element)
        source = SourceInformation(
            description=(
                "The existing capacity of FAME is the Eurostat production capacity "
                "for biodiesels (nrg_inf_lbpc, R5220P), converted with the lower "
                "heating value of FAME (37 MJ/kg, RED II). Eurostat's biodiesels "
                "also include HVO, which is not yet subtracted. Construction years "
                "follow the yearly increase of the capacity. The UK values are held "
                "at 2019, the last year in Eurostat. Switzerland's domestic "
                "biodiesel production (13.5 million litres in 2024, BFE) is "
                "negligible and set to zero."
            ),
            metadata=self.metadata,
        )
        return element.capacity_existing.set_data(
            df=capacity_existing, source=source, unit="GW"
        )

    # -------- helpers ------------------
    @staticmethod
    def _get_nodes(element: ConversionTechnology) -> list[str]:
        """The nodes of the model."""
        return list(element.model.config.system.set_nodes)

    def _get_liquid_biofuel_capacity(
        self, siec: str, nodes: list[str], element: ConversionTechnology
    ) -> pd.DataFrame:
        """Eurostat liquid biofuel capacity [kt/year], cleaned, Swiss row at zero."""
        eurostat = cast(Eurostat, self.data["eurostat"])
        capacity = eurostat.get_liquid_biofuel_capacity(siec=siec, geo=tuple(nodes))
        capacity = self._clean_time_series(capacity, element)
        if "CH" in nodes:
            capacity.loc["CH"] = self.SWISS_LIQUID_BIOFUEL_CAPACITY
        return capacity

    @staticmethod
    def _clean_time_series(
        data: pd.DataFrame, element: ConversionTechnology
    ) -> pd.DataFrame:
        """
        Make a Eurostat time series continuous up to the year before the reference
        year.

        A zero in the latest reported year after a positive value is a placeholder
        for a value not yet reported (e.g. French biogas in 2024), not a closure, so
        it is treated as missing. Missing years are then filled with the previous
        value, which also holds the UK at its last Eurostat year (2019).
        """
        data = data.copy()
        data.columns = data.columns.astype(int)
        last_year = int(data.columns.max())
        if last_year - 1 in data.columns:
            provisional = (data[last_year] == 0) & (data[last_year - 1] > 0)
            data.loc[provisional, last_year] = float("nan")
        last_model_year = element.settings.time.reference_year - 1
        years = range(int(data.columns.min()), max(last_year, last_model_year) + 1)
        data = data.reindex(columns=years).ffill(axis=1).fillna(0)
        return data.loc[:, :last_model_year]

    @staticmethod
    def _to_capacity_existing(
        cumulative: pd.DataFrame, nodes: list[str], element: ConversionTechnology
    ) -> pd.Series:
        """Turn a cumulative capacity [GW] per node and year into capacity additions
        per node and construction year."""
        cumulative = cumulative.reindex(nodes).fillna(0)
        cumulative = cumulative[cumulative.sum(axis=1) > 0]
        additions = calculate_capacity_addition_from_cumulative(cumulative, element)
        capacity = cast(pd.Series, additions.stack())
        capacity.index.names = ["node", "year"]
        capacity = capacity[capacity != 0]
        reference_year = element.settings.time.reference_year
        capacity = capacity[capacity.index.get_level_values("year") < reference_year]
        return format_capacity_existing(capacity)
