from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

import pandas as pd
from zen_creator.datasets.datasets.dataset import Dataset
from zen_creator.datasets.datasets.metadata import MetaData

from zen_europe.datasets.datasets.financial._cost_schema import (
    INDEX_NAMES,
    VALUE_COLUMNS,
)

# Techno-economic data from Concawe report 4/24, Table 116 (internal technology
# name -> values). The capex and fixed O&M go back to Zimmermann et al. (2019), a
# worked example for OME synthesis, so they are a proxy for methanol to kerosene/gasoline.
# Capex: Euro/kW of fuel (LHV), for 2020, 2030 and 2050.
_CAPEX: dict[str, dict[int, float]] = {
    "methanol_to_kerosene": {2020: 307.0, 2030: 269.0, 2050: 200.0},
    "methanol_to_gasoline": {2020: 307.0, 2030: 269.0, 2050: 200.0},
}
# Fixed O&M as a share of the capex per year.
_FOPEX_SHARE_OF_CAPEX: dict[str, float] = {
    "methanol_to_kerosene": 0.045,
    "methanol_to_gasoline": 0.045,
}
# Variable O&M: Euro/MWh of fuel (reported as 1350 Euro/GWh).
_VOPEX: dict[str, float] = {
    "methanol_to_kerosene": 1.35,
    "methanol_to_gasoline": 1.35,
}
# Lifetime in years.
_LIFETIME: dict[str, float] = {
    "methanol_to_kerosene": 30.0,
    "methanol_to_gasoline": 30.0,
}
# The report gives costs "in today's purchasing power" without naming a year and
# converts US$ at about 0.9 Euro/US$; 2020 is assumed.
_MONEY_YEAR_SRC = 2020


class Concawe(Dataset[pd.DataFrame]):
    """Concawe report 4/24, 'E-Fuels: A techno-economic assessment of European
    domestic production and imports towards 2050 - Update'.

    The values are transcribed from the report's tables, so there is no raw file.
    """

    name = "concawe"

    def __init__(self, source_path: Path | str | None = None):
        super().__init__(source_path=source_path)

    def _set_metadata(self) -> MetaData:
        return MetaData(
            name=self.name,
            title=(
                "E-Fuels: A techno-economic assessment of European domestic "
                "production and imports towards 2050 - Update"
            ),
            author=[
                "Alba Soler",
                "Johan Dekeyser",
                "Abinash Ramasary",
                "Victor Gordillo",
                "William Lilley",
                "Patrick Schmidt",
                "Werner Weindorf",
            ],
            publication="Concawe, Report no. 4/24",
            publication_year=2024,
            url="https://www.concawe.eu/wp-content/uploads/Rpt_24-4-1.pdf",
        )

    def _set_path(self) -> Path | None:
        return self.source_path

    def _set_data(self) -> pd.DataFrame:
        rows: list[tuple] = []
        for technology, capex in _CAPEX.items():
            for year, capex_value in capex.items():
                fopex_value = capex_value * _FOPEX_SHARE_OF_CAPEX[technology]
                vopex_value = _VOPEX[technology]
                for variable, value, unit in (
                    ("capex", capex_value, "Euro/kW"),
                    ("fopex", fopex_value, "Euro/kW"),
                    ("vopex", vopex_value, "Euro/MWh"),
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
                            _MONEY_YEAR_SRC,
                            value,
                            unit,
                        )
                    )
                lifetime = _LIFETIME[technology]
                rows.append(
                    (
                        technology,
                        "M",
                        "ref",
                        "lifetime",
                        year,
                        lifetime,
                        "1",
                        None,
                        lifetime,
                        "years",
                    )
                )
        data = pd.DataFrame(rows, columns=INDEX_NAMES + VALUE_COLUMNS)
        return data.set_index(INDEX_NAMES).sort_index()

    # -------- methods ------------------------

    def get_costs(self) -> pd.DataFrame:
        """Return the standardized cost data (see `_cost_schema`)."""
        return self.data.copy()

    def get_conversion_factor_methanol_to_kerosene(self):
        """returns the conversion factor for methanol to kerosene.

        Values from Concawe report 4/24, Table 116, per MJ of kerosene (LHV). The
        balance is allocated to the kerosene, so no co-products are reported.
        The heat output (0.0298 MJ/MJ) is not modelled.
        """
        return [
            {"methanol": {"default_value": 1.0482, "unit": "GWh/GWh"}},
            {"hydrogen": {"default_value": 0.0240, "unit": "GWh/GWh"}},
            {"electricity": {"default_value": 0.0163, "unit": "GWh/GWh"}},
        ]
    
    def get_conversion_factor_methanol_to_gasoline(self):
        """returns the conversion factor for methanol to gasoline.

        Values from Concawe report 4/24, Table 116, per MJ of gasoline (LHV). The
        balance is allocated to the gasoline, so no co-products are reported.
        The heat output (0.0300 MJ/MJ) is not modelled.
        """
        return [
            {"methanol": {"default_value": 1.0562, "unit": "GWh/GWh"}},
            {"hydrogen": {"default_value": 0.0036, "unit": "GWh/GWh"}},
            {"electricity": {"default_value": 0.0164, "unit": "GWh/GWh"}},
        ]