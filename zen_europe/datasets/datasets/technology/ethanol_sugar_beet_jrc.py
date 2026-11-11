from __future__ import annotations

from pathlib import Path

import pandas as pd
from zen_creator import Attribute, ConversionTechnology
from zen_creator.datasets.datasets.dataset import Dataset
from zen_creator.datasets.datasets.metadata import MetaData, SourceInformation


class EthanolSugarBeetJRC(Dataset[pd.Series]):
    """
    Dataset class for first generation ethanol from sugar beet, based on the JRC
    input data for the GHG default values of the Renewable Energy Directive
    (Edwards et al., 2019, Section 6.6).

    The conversion step without biogas from slops (Table 133) is used, with the
    steam supplied by a natural gas boiler (Table 63). All values are per MJ of
    ethanol (LHV). The sugar beet is counted with the LHV of its dry matter
    (16.3 MJ/kg), as in the JRC data.

    The beet pulp is modelled as a wet by-product (pressed pulp), counted with the
    energy of the pulp the JRC reports (Tables 133 and 134). Its dry matter, and so
    its energy, is the same whether it is dried or not.
    """

    name = "ethanol_sugar_beet_jrc"

    # Conversion to ethanol, no biogas from slops (Table 133) [MJ/MJ ethanol]
    SUGAR_BEET_INPUT = 1.8388
    ELECTRICITY_INPUT = 0.0345
    STEAM_INPUT = 0.2806
    # NG boiler, 10 MW (Table 63) [MJ/MJ steam], thermal efficiency 90% (LHV)
    BOILER_NATURAL_GAS_INPUT = 1.111
    BOILER_ELECTRICITY_INPUT = 0.020
    # Beet pulp co-product (Tables 133 and 134)
    PULP_PER_BEET = 0.058  # t pulp (9% water) / t sugar beet (76.5% water)
    PULP_LHV = 14.4  # MJ/kg of pulp at 9% water
    # Ethanol yield (Table 133)
    ETHANOL_PER_BEET = 0.0777  # t ethanol / t sugar beet (76.5% water)
    ETHANOL_LHV = 26.81  # MJ/kg

    def __init__(self, source_path: Path | str | None = None):
        super().__init__(source_path=source_path)

    def _set_metadata(self) -> MetaData:
        return MetaData(
            name=self.name,
            title=(
                "Definition of input data to assess GHG default emissions from "
                "biofuels in EU legislation, Version 1d - 2019"
            ),
            author=[
                "Robert Edwards",
                "Adrian O'Connell",
                "Matteo Padella",
                "Jacopo Giuntoli",
                "Renate Koeble",
                "Claudia Bulgheroni",
                "Luisa Marelli",
                "Laura Lonza",
            ],
            publication="JRC Science for Policy Report, EUR 28349 EN",
            publication_year=2019,
            url="https://publications.jrc.ec.europa.eu/repository/handle/JRC115952",
            doi="https://doi.org/10.2760/69179",
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
    def get_conversion_factor_ethanol_1G_sugar(
        self, element: ConversionTechnology
    ) -> Attribute:
        """
        Get the conversion factor for first generation ethanol from sugar beet.

        The steam is supplied by a natural gas boiler, whose natural gas and
        electricity demand is added to the plant's own electricity demand. The
        pressed beet pulp is an output (ethanol residues), about 0.4 MJ per MJ of
        ethanol.

        The JRC steam is kept unchanged for wet pulp. 0.22 of the 0.28 MJ steam per
        MJ ethanol is distillation; the rest (0.06) is too little to contain the
        drying of the pulp, which sugar factories usually do in direct-fired dryers.

        Returns:
            Attribute: The conversion factor attribute of the element.
        """
        attr = element.conversion_factor
        natural_gas = self.STEAM_INPUT * self.BOILER_NATURAL_GAS_INPUT
        electricity = (
            self.ELECTRICITY_INPUT + self.STEAM_INPUT * self.BOILER_ELECTRICITY_INPUT
        )
        residues = (self.PULP_PER_BEET * self.PULP_LHV) / (
            self.ETHANOL_PER_BEET * self.ETHANOL_LHV
        )
        cf = [
            {"sugar_crops": {"default_value": self.SUGAR_BEET_INPUT, "unit": "GWh/GWh"}},
            {"natural_gas": {"default_value": natural_gas, "unit": "GWh/GWh"}},
            {"electricity": {"default_value": electricity, "unit": "GWh/GWh"}},
            {"ethanol_residues": {"default_value": residues, "unit": "GWh/GWh"}},
        ]
        source = SourceInformation(
            description=(
                "The conversion factor of first generation ethanol from sugar beet is "
                "taken from the JRC input data for the RED default values (Edwards et "
                "al., 2019, Table 133, no biogas from slops), with the steam from a "
                "natural gas boiler (Table 63). The sugar beet is counted with the LHV "
                "of its dry matter. The beet pulp is an output as a wet ethanol "
                "residue, counted with the energy of the pulp the JRC reports "
                "(0.058 t/t beet at 14.4 MJ/kg, Table 134)."
            ),
            metadata=self.metadata,
        )
        attr.set_data(default_value=cf, source=source)
        return attr