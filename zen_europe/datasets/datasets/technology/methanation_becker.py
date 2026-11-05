from __future__ import annotations

from pathlib import Path

import pandas as pd
from zen_creator import Attribute, ConversionTechnology
from zen_creator.datasets.datasets.dataset import Dataset
from zen_creator.datasets.datasets.metadata import MetaData, SourceInformation


class MethanationBecker(Dataset[pd.Series]):
    """
    Dataset class for the catalytic methanation of hydrogen and carbon dioxide,
    based on the plant design of Becker et al. (2018).

    The hydrogen and carbon demand are derived from the plant mass balance (Table 1
    of the paper) on a lower heating value basis, the basis used in the model.
    """

    name = "methanation_becker"

    # Plant mass balance (Table 1) [kg/s]
    HYDROGEN_INPUT = 0.463
    CARBON_INPUT = 2.522
    SNG_OUTPUT = 0.939
    # SNG molar composition
    SNG_SHARE_CH4 = 0.927
    SNG_SHARE_H2 = 0.063
    SNG_SHARE_CO2 = 0.010
    # Molar masses [g/mol] and lower heating values [kJ/mol]
    MOLAR_MASS_CH4 = 16.043
    MOLAR_MASS_H2 = 2.016
    MOLAR_MASS_CO2 = 44.01
    LHV_CH4 = 802.3
    LHV_H2 = 241.8

    def __init__(self, source_path: Path | str | None = None):
        super().__init__(source_path=source_path)

    def _set_metadata(self) -> MetaData:
        return MetaData(
            name=self.name,
            title=(
                "Production of Synthetic Natural Gas From Carbon Dioxide and "
                "Renewably Generated Hydrogen: A Techno-Economic Analysis of a "
                "Power-to-Gas Strategy"
            ),
            author=["William L. Becker", "Michael Penev", "Robert J. Braun"],
            publication="Journal of Energy Resources Technology",
            publication_year=2019,
            url="https://doi.org/10.1115/1.4041381",
            doi="https://doi.org/10.1115/1.4041381",
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

    # -------- methods ------------------------
    def get_conversion_factor_methanation(
        self, element: ConversionTechnology
    ) -> Attribute:
        """
        Get the conversion factor for methanation technologies.

        The net electricity output of the plant (82 kW, 0.2% of the SNG output) is
        not modelled. The reaction heat is used internally to generate the plant's
        power, so there is no heat output either.

        Returns:
            Attribute: The conversion factor attribute of the element.
        """
        attr = element.conversion_factor
        sng_molar_mass = (
            self.SNG_SHARE_CH4 * self.MOLAR_MASS_CH4
            + self.SNG_SHARE_H2 * self.MOLAR_MASS_H2
            + self.SNG_SHARE_CO2 * self.MOLAR_MASS_CO2
        )
        sng_mol_per_s = self.SNG_OUTPUT * 1000 / sng_molar_mass
        # mol/s * kJ/mol = kW; divided by 1000 -> MW
        sng_power = (
            sng_mol_per_s
            * (self.SNG_SHARE_CH4 * self.LHV_CH4 + self.SNG_SHARE_H2 * self.LHV_H2)
            / 1000
        )
        hydrogen_power = (
            self.HYDROGEN_INPUT * 1000 / self.MOLAR_MASS_H2 * self.LHV_H2 / 1000
        )
        carbon_flow = self.CARBON_INPUT * 3.6  # kg/s -> t/h
        cf = [
            {
                "hydrogen": {
                    "default_value": hydrogen_power / sng_power,
                    "unit": "GWh/GWh",
                }
            },
            {
                "carbon": {
                    "default_value": carbon_flow / sng_power,
                    "unit": "ktCO2/GWh",
                }
            },
        ]
        source = SourceInformation(
            description=(
                "The conversion factor of methanation is derived from the plant mass "
                "balance of Becker et al. (2018), 'Production of Synthetic Natural Gas "
                "From Carbon Dioxide and Renewably Generated Hydrogen', Table 1, on a "
                "lower heating value basis. The plant covers its own power demand "
                "from the reaction heat."
            ),
            metadata=self.metadata,
        )
        attr.set_data(default_value=cf, source=source)
        return attr