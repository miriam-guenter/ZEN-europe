from __future__ import annotations

from typing import TYPE_CHECKING

from zen_europe.datasets.datasets.technology.pyrolysis_upgrading_jones import (
    PyrolysisUpgradingJones,
)
from zen_europe.datasets.datasets.technology.technology_diffusion_mannhardt import (
    TechnologyDiffusionMannhardt,
)

if TYPE_CHECKING:
    from zen_creator.model import Model

from zen_creator import AssumptionInformation, Attribute, ConversionTechnology


class PyrolysisOilUpgrading(ConversionTechnology):
    """Class containing all data and assumptions for the upgrading of raw
    pyrolysis oil (bio-crude) to hydrocarbon fuel by stabilization, two-stage
    hydrotreating and hydrocracking. The gasoline and diesel range product is
    modelled as oil. Replaces the former 1:1 dummy route pyrolysis_oil_to_oil."""

    name: str = "pyrolysis_oil_upgrading"

    def __init__(self, model: Model, power_unit: str = "MW"):
        super().__init__(model=model, power_unit=power_unit)

    # ---------- Required methods that are called during object construction ----------

    def _set_reference_carrier(self) -> Attribute:
        """
        Sets the reference carrier of pyrolysis oil upgrading to oil.
        """
        return Attribute(name="reference_carrier", default_value=["oil"], element=self)

    def _set_input_carrier(self) -> Attribute:
        """
        Sets the input carrier of pyrolysis oil upgrading to pyrolysis oil,
        hydrogen (hydrotreating) and electricity.
        """
        return Attribute(
            name="input_carrier",
            default_value=["pyrolysis_oil", "hydrogen", "electricity"],
            element=self,
        )

    def _set_output_carrier(self) -> Attribute:
        """
        Set the output carrier of pyrolysis oil upgrading to oil.
        """
        return Attribute(name="output_carrier", default_value=["oil"], element=self)

    # ---------- Required methods that are called during object build ----------

    def _set_lifetime(self) -> Attribute:
        """
        Sets the lifetime of pyrolysis oil upgrading.

        """
        dataset = PyrolysisUpgradingJones(source_path=self.source_path)
        return dataset.get_lifetime(self)

    def _set_conversion_factor(self) -> Attribute:
        """
        Return the conversion factor of pyrolysis oil upgrading.

        """
        dataset = PyrolysisUpgradingJones(source_path=self.source_path)
        return dataset.get_conversion_factor(self)

    def _set_construction_time(self) -> Attribute:
        """
        Sets the construction time of pyrolysis oil upgrading.

        """
        if self.settings.investment.use_construction_times:
            dataset = PyrolysisUpgradingJones(source_path=self.source_path)
            return dataset.get_construction_time(self)
        else:
            return self.construction_time

    def _set_capex_specific_conversion(self) -> Attribute:
        """
        Sets the specific capital expenditure (capex) for pyrolysis oil upgrading.

        """
        dataset = PyrolysisUpgradingJones(source_path=self.source_path)
        return dataset.get_capex_specific_conversion(self)

    def _set_opex_specific_fixed(self) -> Attribute:
        """
        Sets the specific fixed operational expenditure (opex) for pyrolysis oil
        upgrading.

        """
        dataset = PyrolysisUpgradingJones(source_path=self.source_path)
        return dataset.get_opex_specific_fixed(self)

    def _set_opex_specific_variable(self) -> Attribute:
        """
        Sets the specific variable operational expenditure (opex) for pyrolysis
        oil upgrading.

        """
        dataset = PyrolysisUpgradingJones(source_path=self.source_path)
        return dataset.get_opex_specific_variable(self)

    def _set_capacity_existing(self) -> Attribute:
        """
        Sets the existing capacity of pyrolysis oil upgrading.

        """
        attr = self.capacity_existing
        attr.set_data(
            default_value=0,
            df=None,
            source=AssumptionInformation(
                description=("We do not consider existing capacities."),
            ),
        )
        return attr

    def _set_max_diffusion_rate(self) -> Attribute:
        """
        Sets the maximum diffusion rate of pyrolysis oil upgrading.
        """
        if not self.settings.investment.use_diffusion_rates:
            return self.max_diffusion_rate
        diffusion_rates = TechnologyDiffusionMannhardt(source_path=self.source_path)
        return diffusion_rates.get_max_diffusion_rate(self)
