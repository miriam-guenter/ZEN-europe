from __future__ import annotations

from pathlib import Path

import pandas as pd
from zen_creator.datasets.datasets.dataset import Dataset
from zen_creator.datasets.datasets.metadata import MetaData


class BFERenewableEnergyStatistics(Dataset[pd.DataFrame]):
    """
    Swiss statistics of renewable energy (Schweizerische Statistik der erneuerbaren
    Energien, Ausgabe 2024) of the Swiss Federal Office of Energy (BFE).

    Switzerland is not covered by the Eurostat renewables tables, so the Swiss
    biogas production is taken from the detailed data in Annex B of this statistic.
    The publication is a PDF, so the values are entered as constants on the class.

    All biogas values are in GWh (lower heating value) and refer to the years
    1990, 2000, 2010, 2015 and 2020 to 2024, the only years Annex B reports.
    """

    name = "bfe_renewable_energy_statistics"

    YEARS = [1990, 2000, 2010, 2015, 2020, 2021, 2022, 2023, 2024]

    # Annex B, biogas used on site for heat and power ("Verbrauch Biogas" /
    # "Verbrauch Klärgas") per plant category [GWh]. These exclude the gas upgraded
    # and injected into the gas grid, which is listed separately below.
    # fmt: off
    BIOGAS_USED_ON_SITE = {
        # 4.5 Biogasanlagen Landwirtschaft (B41)
        "agriculture": [
            16.46, 17.22, 138.14, 289.05, 489.31, 530.22, 540.49, 556.44, 568.04
        ],
        # 6.4 Biogasanlagen Gewerbe/Industrie (B41)
        "commercial_industrial": [
            0.0, 22.73, 109.55, 204.99, 224.04, 218.72, 217.65, 229.71, 227.33
        ],
        # 7.1.3 Kläranlagen Total, exkl. Einspeisung ins Erdgasnetz (B42)
        "sewage_treatment": [
            349.1, 443.1, 489.4, 464.0, 539.4, 539.5, 536.8, 538.5, 536.5
        ],
        # 7.2 Biogasanlagen Industrieabwässer (B41)
        "industrial_wastewater": [
            11.47, 35.04, 54.13, 71.06, 53.76, 57.33, 65.30, 57.84, 60.22
        ],
    }
    # fmt: on

    # Annex B, 8.1 "Bio- und Klärgaseinspeisung ins Erdgasnetz" [GWh Hu]: biomethane
    # injected into the gas grid from all digester categories above.
    BIOGAS_GRID_INJECTION = [0.0, 3.4, 57.6, 229.9, 369.0, 370.4, 422.9, 438.0, 471.0]

    # Annex B, 8.2 "Bioethanol Inlandproduktion": Switzerland has no domestic
    # bioethanol production in any reported year (all values 0).
    BIOETHANOL_DOMESTIC_PRODUCTION = 0.0

    # Annex B, 8.2 "Biodiesel Inlandproduktion" in 2024 [1000 litres].
    BIODIESEL_DOMESTIC_PRODUCTION_2024 = 13451

    def __init__(self, source_path: Path | str | None = None):
        super().__init__(source_path=source_path)

    def _set_metadata(self) -> MetaData:
        return MetaData(
            name=self.name,
            title="Schweizerische Statistik der erneuerbaren Energien, Ausgabe 2024",
            author=["Bundesamt für Energie (BFE)", "EBP Schweiz AG"],
            publication="Bundesamt für Energie (BFE)",
            publication_year=2025,
            url="https://pubdb.bfe.admin.ch/de/publication/download/12286",
            note="Values read from Annex B (Detaildaten), version of 16.09.2025.",
        )

    def _set_path(self) -> Path | None:
        return None

    def _set_data(self) -> pd.DataFrame:
        data = pd.DataFrame(self.BIOGAS_USED_ON_SITE, index=self.YEARS).T
        data.loc["grid_injection"] = self.BIOGAS_GRID_INJECTION
        data.columns.name = "year"
        return data

    # -------- methods ------------------------
    def get_biogas_production_digestion(self) -> pd.Series:
        """
        Swiss biogas produced by anaerobic digestion [GWh].

        The sum of the biogas used on site by agricultural, commercial/industrial,
        sewage and industrial wastewater digesters and the biomethane they inject
        into the gas grid. Landfill gas is excluded, as for the Eurostat countries.
        The biomethane is counted 1:1 as biogas, as Eurostat does.

        Returns:
            pd.Series: indexed by year, only the years reported in Annex B.
        """
        return self.data.sum(axis=0)
