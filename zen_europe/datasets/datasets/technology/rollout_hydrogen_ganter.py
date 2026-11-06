from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
from zen_creator.datasets.datasets.dataset import Dataset
from zen_creator.datasets.datasets.metadata import MetaData

from zen_europe.datasets.datasets.financial._cost_schema import (
    INDEX_NAMES,
    VALUE_COLUMNS,
)
from zen_europe.utils.constants import Constants
from zen_europe.utils.utils import convert_country_names

# Biomass gasification data from the Supporting Information of Ganter et al. (2024)
# (https://zenodo.org/records/10568836), Table S1. Only these technologies are
# reported to the cost database. The values are flat because the source gives one 
# value for its 2025-2035 horizon Capex: Euro/kW of hydrogen (LHV).
_CAPEX: dict[str, float] = {
    "gasification_to_hydrogen": 1543.0,
    "gasification_to_hydrogen_CCS": 2263.0,
}
# Fixed O&M as a share of the capex per year.
_FOPEX_SHARE_OF_CAPEX = 0.05
# Lifetime in years.
_LIFETIME = 20.0
# Construction time in years. Not reported in this Supporting Information; taken from
# Table S2 of the same group's follow-up work (https://arxiv.org/abs/2407.05988).
_CONSTRUCTION_TIME = 2.0
# The source does not name its currency year, so 2020 is assumed.
_MONEY_YEAR_SRC = 2020
_YEARS = (2020, 2030, 2050)


class HydrogenRolloutGanter(Dataset[pd.DataFrame]):
    """
    Dataset class for the near-term infrastructure rollout and investment strategies
    for net-zero hydrogen supply chains, based on the work of Alissa Ganter et al.
    (2024).

    """

    name = "hydrogen_rollout_ganter"

    def __init__(self, source_path: Path | str | None = None):
        super().__init__(source_path=source_path)

    def _set_metadata(self) -> MetaData:
        return MetaData(
            name=self.name,
            title=(
                "Near-term infrastructure rollout and investment strategies for "
                "net-zero hydrogen supply chains"
            ),
            author=["Alissa Ganter", "Paolo Gabrielli", "Giovanni Sansavini"],
            publication="Renewable and Sustainable Energy Reviews",
            publication_year=2024,
            url="https://www.sciencedirect.com/science/article/pii/S1364032124000376",
            doi="https://doi.org/10.1016/j.rser.2024.114314",
        )

    def _set_path(self) -> Path | None:
        if self.source_path is None:
            raise ValueError("source_path must be set to load the dataset.")
        return self.source_path

    def _set_data(self) -> pd.DataFrame:
        """
        Sets the standardized cost data of biomass gasification (see `_cost_schema`).
        The values are transcribed from the Supporting Information, so there is no
        raw file.
        """
        rows: list[tuple] = []
        for technology, capex in _CAPEX.items():
            for year in _YEARS:
                for variable, value, unit, money_year in (
                    ("capex", capex, "Euro/kW", _MONEY_YEAR_SRC),
                    (
                        "fopex",
                        capex * _FOPEX_SHARE_OF_CAPEX,
                        "Euro/kW",
                        _MONEY_YEAR_SRC,
                    ),
                    ("lifetime", _LIFETIME, "1", None),
                    ("construction_time", _CONSTRUCTION_TIME, "1", None),
                ):
                    rows.append(
                        (
                            technology,
                            "M",
                            "ref",
                            variable,
                            year,
                            value,
                            unit,
                            money_year,
                            value,
                            unit,
                        )
                    )
        data = pd.DataFrame(rows, columns=INDEX_NAMES + VALUE_COLUMNS)
        return data.set_index(INDEX_NAMES).sort_index()

    # -------- methods ------------------------
    
    def get_conversion_factor_SMR(self) -> list[dict[str, dict[str, Any]]]:
        """Get the conversion factor for SMR technologies.

        The data is obtained from the Supplementary Information, Table S2, p. 8.

        Returns:
            The conversion factor per input carrier.
        """
        conversion_factor = [
            {
                "natural_gas": {"default_value": 1 / 0.77, "unit": "GW/GW"},
                "electricity": {"default_value": 0.041, "unit": "GW/GW"},
            }
        ]
        return conversion_factor

    def get_capacity_existing_SMR(self) -> pd.Series:
        """
        Get the existing capacity for SMR technologies.
        We assume that all current ammonia plants and refineries use H2 from SMR.

        Returns:
            pd.Series: A pandas Series containing the existing capacity data.
        """
        path_capa_ex = self.path / "03-technology" / "capacity_existing" / "SMR"
        refineries = pd.read_excel(path_capa_ex / "Refinery_plants_OV.xlsx")
        ammonia_plants = pd.read_excel(path_capa_ex / "Ammonia_plants_OV.xlsx")
        refineries["Country"] = convert_country_names(refineries["Country"])
        ammonia_plants["Country"] = convert_country_names(ammonia_plants["Country"])
        capacity_existing_ref = (
            refineries.set_index("Country").groupby("Country").sum()
        )["H2 capacity (kg/h)"]
        capacity_existing_amm = (
            ammonia_plants.set_index("Country").groupby("Country").sum()
        )["Capacity (kg/h)"]
        # sum capacities
        capacity_existing = capacity_existing_ref.add(
            capacity_existing_amm, fill_value=0
        )
        capacity_existing = capacity_existing * Constants.HYDROGEN_KWH_PER_KG / 1e6
        return capacity_existing
    
    def get_costs(self) -> pd.DataFrame:
        """Return the standardized cost data (see `_cost_schema`)."""
        return self.data.copy()

    def get_conversion_factor_gasification_to_hydrogen(
        self,
    ) -> list[dict[str, dict[str, Any]]]:
        """Get the conversion factor for gasification to hydrogen.

        The data is obtained from the Supporting Information, Table S2, which uses
        the heat pipe reformer case of Antonini et al. (2021): an efficiency of 0.62
        per unit of dry biomass and an electricity balance of -0.093 per unit of
        hydrogen, meaning that electricity has to be provided.

        Returns:
            The conversion factor per input carrier.
        """
        return [
            {"gasif_biomass": {"default_value": 1 / 0.62, "unit": "GWh/GWh"}},
            {"electricity": {"default_value": 0.093, "unit": "GWh/GWh"}},
        ]

    def get_capture_rate_gasification_to_hydrogen(self) -> float:
        """Get the share of the biomass carbon captured by the CCS retrofit.

        Antonini et al. (2021), Table 3 (heat pipe reformer with CCS), which the
        Supporting Information of Ganter et al. (2024) rounds to 57 % in Table S2.
        The rest of the CO2 leaves with the flue gas of the reformer.
        """
        return 0.574

    def get_electricity_demand_gasification_to_hydrogen_CCS(self) -> float:
        """Get the additional electricity of the CCS retrofit [GWh/GWh hydrogen].

        The difference between the electricity balance with CCS (-0.153) and without
        CCS (-0.093) in the Supporting Information, Table S2.
        """
        return 0.153 - 0.093
