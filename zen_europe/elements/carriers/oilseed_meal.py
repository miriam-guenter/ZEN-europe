from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
from zen_creator import SourceInformation
from zen_creator.datasets.datasets.metadata import MetaData

from zen_europe.datasets.datasets.financial.ECB import ECBInflation

if TYPE_CHECKING:
    from zen_creator.model import Model

from zen_creator.elements import Carrier
from zen_creator.utils.attribute import Attribute


class OilseedMeal(Carrier):
    """Oilseed meal, the protein-rich co-product of crushing oilseeds into
    vegetable oil (oil_crops_to_oily_biomass), in terms of the energy of the
    meal.

    It can either be sold to the animal feed market (export at the market price
    of rapeseed meal), be used as a co-substrate in anaerobic digestion (route
    into the dry biogas pool) or go to slow pyrolysis."""

    name: str = "oilseed_meal"

    # Market price of rapeseed meal, June 2017 (Carre et al. 2018, Table 5)
    PRICE_PER_TONNE = 215.0  # EUR/t meal
    PRICE_MONEY_YEAR = 2017
    # Dry matter of hexane-extracted rapeseed meal (Carre 2024, Table 2)
    DRY_MATTER = 0.886  # t DM / t meal
    # LHV of meal cake on a dry basis (ADEME 2010, cited in OCL 2013, Table 1)
    LHV_DM = 17.14  # MJ/kg DM

    def __init__(self, model: Model, power_unit: str = "MW"):
        super().__init__(model=model, power_unit=power_unit)
        self.get_inflation_rate = ECBInflation(
            source_path=self.source_path
        ).get_inflation_rate

    @classmethod
    def lhv(cls) -> float:
        """LHV of the meal as sold [MJ/kg meal], water not deducted."""
        return cls.LHV_DM * cls.DRY_MATTER

    def _set_availability_import(self) -> Attribute:
        """
        Return the import availability of oilseed meal. It is only produced as a
        co-product of oilseed crushing.
        """
        return Attribute(
            "availability_import",
            default_value=0,
            element=self,
            unit=self.power_unit,
        )

    def _set_availability_export(self) -> Attribute:
        """
        Return the export availability of oilseed meal. Unlimited, so all meal
        that is not digested or pyrolysed can be sold to the animal feed market.
        """
        return Attribute(
            "availability_export",
            default_value=np.inf,
            element=self,
            unit=self.power_unit,
        )

    def _set_availability_export_yearly(self) -> Attribute:
        """
        Return the yearly export availability of oilseed meal (unlimited).
        """
        return Attribute(
            "availability_export_yearly",
            default_value=np.inf,
            element=self,
            unit=self.energy_unit,
        )

    def _set_price_export(self) -> Attribute:
        """
        Return the export price of oilseed meal, i.e. its value on the animal
        feed market.

        The price of rapeseed meal is converted to an energy basis with the LHV
        of the meal (17.14 MJ/kg DM at 88.6% DM = 15.2 MJ/kg) and inflated to
        the price year.
        """
        attr = self.price_export
        inflation = self.get_inflation_rate(
            base_year=self.PRICE_MONEY_YEAR, target_year=self.settings.time.price_year
        )
        price = self.PRICE_PER_TONNE / (self.lhv() / 3.6) * inflation  # Euro/MWh
        return attr.set_data(
            default_value=price,
            unit="Euro/MWh",
            source=SourceInformation(
                description=(
                    "The export price of oilseed meal is its value on the animal "
                    "feed market. It is the rapeseed meal price of June 2017 used "
                    "by Carre et al. (2018, Table 5, 215 EUR/t), converted to an "
                    "energy basis with the LHV of meal cake (17.14 MJ/kg DM, ADEME "
                    "2010) at 88.6% dry matter (Carre 2024, Table 2), and inflated "
                    "to the price year. Meal prices follow the protein feed market "
                    "and are volatile."
                ),
                metadata=MetaData(
                    name="carre_2018_hot_ethanol_extraction",
                    title=(
                        "Hot ethanol extraction: economic feasibility of a new and "
                        "green process"
                    ),
                    author=["Patrick Carre", "Morgane Citeau", "Sylvie Dauguet"],
                    publication="OCL",
                    publication_year=2018,
                    url="https://doi.org/10.1051/ocl/2017061",
                    doi="https://doi.org/10.1051/ocl/2017061",
                ),
            ),
        )
