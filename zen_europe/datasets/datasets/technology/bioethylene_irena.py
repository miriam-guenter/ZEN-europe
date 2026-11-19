from __future__ import annotations

from pathlib import Path

import pandas as pd
from zen_creator import Attribute, ConversionTechnology
from zen_creator.datasets.datasets.dataset import Dataset
from zen_creator.datasets.datasets.metadata import MetaData, SourceInformation

from zen_europe.datasets.datasets.financial.ECB import ECBDollar2Euro, ECBInflation


class BioethyleneIRENA(Dataset[pd.Series]):
    """
    Dataset class for the capital cost of bio-ethylene production by ethanol
    dehydration, based on the IEA-ETSAP and IRENA Technology Brief I13 (2013).

    The brief reports capital costs of USD 1,100-1,400 per tonne of annual
    bio-ethylene capacity, from recent investments (Braskem, 200 kt/yr, USD 278
    million; Mitsui/Dow, 350 kt/yr, USD 400 million). 
    """

    name = "bioethylene_irena"

    CAPEX_LOW = 1100.0  # USD / (t/yr)
    CAPEX_HIGH = 1400.0  # USD / (t/yr)
    MONEY_YEAR = 2011  # year of the Braskem and Mitsui/Dow investments
    HOURS_PER_YEAR = 8760  # annual capacity at nameplate hourly capacity

    def __init__(self, source_path: Path | str | None = None):
        super().__init__(source_path=source_path)

    def _set_metadata(self) -> MetaData:
        return MetaData(
            name=self.name,
            title="Production of Bio-ethylene: Technology Brief I13",
            author=["IEA-ETSAP", "IRENA"],
            publication="IEA-ETSAP and IRENA Technology Brief",
            publication_year=2013,
            url=(
                "https://www.irena.org/-/media/Files/IRENA/Agency/Publication/2013/"
                "IRENA-ETSAP-Tech-Brief-I13-Production_of_Bio-ethylene.pdf"
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

    # -------- methods ------------------------
    def get_capex_specific_conversion(self, element: ConversionTechnology) -> Attribute:
        """
        Get the specific capex of ethanol dehydration [Euro/(tproduct/h)].

        The midpoint of the reported range per tonne of annual capacity is
        multiplied with the hours per year to obtain the capex per tonne per hour
        of capacity, converted to euro and inflated to the price year.
        """
        capex = (self.CAPEX_LOW + self.CAPEX_HIGH) / 2 * self.HOURS_PER_YEAR
        dollar2euro = ECBDollar2Euro(source_path=self.source_path).get_dollar2euro(
            self.MONEY_YEAR
        )
        inflation = ECBInflation(source_path=self.source_path).get_inflation_rate(
            base_year=self.MONEY_YEAR, target_year=element.settings.time.price_year
        )
        capex *= dollar2euro * inflation
        attr = element.capex_specific_conversion
        attr.set_data(
            default_value=capex,
            unit="Euro/(tproduct/h)",
            source=SourceInformation(
                description=(
                    "The specific capex of olefin from ethanol is the midpoint of "
                    "the capital cost range of bio-ethylene plants (USD 1,100-1,400 "
                    "per t/yr of capacity) from the IEA-ETSAP and IRENA Technology "
                    "Brief I13 (2013), converted to a capacity per hour with 8760 "
                    "h/yr, converted to euro (2011) and inflated to the price year."
                ),
                metadata=self.metadata,
            ),
        )
        return attr
