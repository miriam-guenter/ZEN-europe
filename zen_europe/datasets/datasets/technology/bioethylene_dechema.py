from __future__ import annotations

from pathlib import Path

import pandas as pd
from zen_creator import Attribute, ConversionTechnology
from zen_creator.datasets.datasets.dataset import Dataset
from zen_creator.datasets.datasets.metadata import MetaData, SourceInformation


class BioethyleneDECHEMA(Dataset[pd.Series]):
    """
    Dataset class for the dehydration of (bio)ethanol to ethylene, based on the
    DECHEMA technology study on low carbon energy and feedstock for the European
    chemical industry (Bazzanella and Ausfelder, 2017, chapter 6.3).

    Ethanol is dehydrated over an alumina or silica-alumina catalyst at about
    300 degC. One tonne of ethylene requires 1.74 t of (hydrated) ethanol, with 99%
    conversion and 97% selectivity (chapter 6.3.1). DECHEMA reports the energy
    demand of the whole chain (85.5 GJ/t ethylene, Table 23), which includes the
    production of the 1.74 t ethanol (47.7 GJ/t ethanol, Table 23). The remainder,
    2.5 GJ/t ethylene, is the process energy of the dehydration step. It lies
    above the theoretical minimum of 1.68 GJ/t for the endothermic reaction
    (chapter 6.3.1).
    """

    name = "bioethylene_dechema"

    ETHANOL_PER_ETHYLENE = 1.74  # t ethanol / t ethylene (chapter 6.3.1)
    ENERGY_DEMAND_CHAIN = 85.5  # GJ / t ethylene, incl. ethanol production (Table 23)
    ENERGY_DEMAND_ETHANOL = 47.7  # GJ / t ethanol (Table 23)
    LHV_ETHANOL = 26.81  # MJ/kg, same value as in the ethanol-to-jet dataset

    def __init__(self, source_path: Path | str | None = None):
        super().__init__(source_path=source_path)

    def _set_metadata(self) -> MetaData:
        return MetaData(
            name=self.name,
            title=(
                "Low carbon energy and feedstock for the European chemical "
                "industry"
            ),
            author=["Alexis Bazzanella", "Florian Ausfelder"],
            publication="DECHEMA Technology Study",
            publication_year=2017,
            url=(
                "https://dechema.de/dechema_media/Downloads/Positionspapiere/"
                "Technology_study_Low_carbon_energy_and_feedstock_for_the_"
                "European_chemical_industry-p-20002750.pdf"
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
    def get_process_energy(self) -> float:
        """Process energy of the dehydration step [GJ/t ethylene]."""
        return (
            self.ENERGY_DEMAND_CHAIN
            - self.ETHANOL_PER_ETHYLENE * self.ENERGY_DEMAND_ETHANOL
        )

    def get_conversion_factor(self, element: ConversionTechnology) -> Attribute:
        """
        Get the conversion factor of ethanol to ethylene, per tonne of ethylene.

        The ethanol is counted with the LHV of anhydrous ethanol. DECHEMA refers
        to hydrated ethanol, so this is a slight upper bound of the ethanol demand.
        The process energy is supplied as natural gas, as a placeholder for
        industrial heat.
        """
        ethanol = self.ETHANOL_PER_ETHYLENE * self.LHV_ETHANOL / 3.6 / 1000  # GWh/t
        natural_gas = self.get_process_energy() / 3.6 / 1000  # GWh/t
        cf = [
            {"ethanol": {"default_value": ethanol, "unit": "GWh/tproduct"}},
            {"natural_gas": {"default_value": natural_gas, "unit": "GWh/tproduct"}},
        ]
        attr = element.conversion_factor
        attr.set_data(
            default_value=cf,
            source=SourceInformation(
                description=(
                    "The conversion factor of olefin from ethanol (ethanol "
                    "dehydration to ethylene) is based on DECHEMA (2017, chapter "
                    "6.3): 1.74 t ethanol per t ethylene, counted with an LHV of "
                    "26.81 MJ/kg. The process energy of 2.5 GJ/t ethylene is the "
                    "energy demand of the whole chain (85.5 GJ/t, Table 23) minus "
                    "the energy demand of producing 1.74 t ethanol (47.7 GJ/t "
                    "ethanol, Table 23). It is supplied as natural gas, as a "
                    "placeholder for industrial heat."
                ),
                metadata=self.metadata,
            ),
        )
        return attr
