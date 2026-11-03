from __future__ import annotations

from typing import TYPE_CHECKING

from zen_europe.datasets.dataset_collections.technology_cost_database import (
    TechnologyCostDatabase,
)
from zen_europe.datasets.datasets.financial.dea import DEA
from zen_europe.datasets.datasets.technology.technology_diffusion_mannhardt import (
    TechnologyDiffusionMannhardt,
)

if TYPE_CHECKING:
    from zen_creator.model import Model

from zen_creator import (
    AssumptionInformation,
    Attribute,
    ConversionTechnology,
    SourceInformation,
)


class FastPyrolysis(ConversionTechnology):
    """Class containing all data and assumptions for fast pyrolysis of woody
    biomass (to pyrolysis oil; the pyrolysis gas is burned on site and its
    surplus heat supplied as district heat)."""

    name: str = "pyrolysis_fast"

    def __init__(self, model: Model, power_unit: str = "MW"):
        super().__init__(model=model, power_unit=power_unit)

    # ---------- Required methods that are called during object construction ----------

    def _set_reference_carrier(self) -> Attribute:
        """
        Sets the reference carrier of fast pyrolysis to pyrolysis oil.
        """
        return Attribute(
            name="reference_carrier", default_value=["pyrolysis_oil"], element=self
        )

    def _set_input_carrier(self) -> Attribute:
        """
        Sets the input carrier of fast pyrolysis to biomass for fast pyrolysis
        and electricity.
        """
        return Attribute(
            name="input_carrier",
            default_value=["biomass_fast_pyrolysis", "electricity"],
            element=self,
        )

    def _set_output_carrier(self) -> Attribute:
        """
        Set the output carrier of fast pyrolysis to pyrolysis oil and district
        heat.
        """
        return Attribute(
            name="output_carrier",
            default_value=["pyrolysis_oil", "district_heat"],
            element=self,
        )

    # ---------- Required methods that are called during object build ----------

    def _set_lifetime(self) -> Attribute:
        """
        Sets the lifetime of fast pyrolysis.

        """
        tech_db = TechnologyCostDatabase(
            settings=self.settings, source_path=self.source_path
        )
        return tech_db.get_lifetime(self)

    def _set_conversion_factor(self) -> Attribute:
        """
        Return the conversion factor of fast pyrolysis.

        """
        attr = self.conversion_factor
        dea_dataset = DEA(source_path=self.source_path)
        cf = dea_dataset.get_conversion_factor_pyrolysis_fast()
        source = SourceInformation(
            description=(
                "The conversion factor of fast pyrolysis is based on the DEA "
                "technology catalogue for renewable fuels (86 Fast pyrolysis (25 "
                "MW), wood feedstock), normalized to the pyrolysis oil output. The "
                "pyrolysis gas is assumed to be burned on site with 90% efficiency "
                "to cover the heat demand; the surplus is supplied as district heat."
            ),
            metadata=dea_dataset.metadata,
        )
        attr.set_data(default_value=cf, source=source)
        return attr

    def _set_construction_time(self) -> Attribute:
        """
        Sets the construction time of fast pyrolysis.

        """
        if self.settings.investment.use_construction_times:
            tech_db = TechnologyCostDatabase(
                settings=self.settings, source_path=self.source_path
            )
            return tech_db.get_construction_time(self)
        else:
            return self.construction_time

    def _set_capex_specific_conversion(self) -> Attribute:
        """
        Sets the specific capital expenditure (capex) for fast pyrolysis.

        DEA reports the specific investment per MW of output from the pyrolysis
        process (oil and gas), so it is rebased onto the pyrolysis oil output.

        Returns:
            Attribute: An Attribute object containing the specific capex data.
        """
        tech_db = TechnologyCostDatabase(
            settings=self.settings, source_path=self.source_path
        )
        multiplier = DEA(source_path=self.source_path).get_cost_multiplier_pyrolysis_fast()
        return tech_db.get_capex_specific_conversion(self, multiplier=multiplier)

    def _set_opex_specific_fixed(self) -> Attribute:
        """
        Sets the specific fixed operational expenditure (opex) for fast
        pyrolysis.

        DEA reports a combined fixed and variable O&M per MW of output from the
        pyrolysis process, so it is mapped to fixed opex and rebased onto the
        pyrolysis oil output.

        Returns:
            Attribute: An Attribute object containing the specific fixed opex data.
        """
        tech_db = TechnologyCostDatabase(
            settings=self.settings, source_path=self.source_path
        )
        multiplier = DEA(source_path=self.source_path).get_cost_multiplier_pyrolysis_fast()
        return tech_db.get_opex_specific_fixed(self, multiplier=multiplier)

    def _set_opex_specific_variable(self) -> Attribute:
        """
        Sets the specific variable operational expenditure (opex) for fast
        pyrolysis.

        DEA merged fixed and variable O&M into one figure, which is mapped to
        fixed opex, so the variable opex keeps its default.

        Returns:
            Attribute: An Attribute object containing the specific variable opex data.
        """
        return self.opex_specific_variable

    def _set_capacity_existing(self) -> Attribute:
        """
        Sets the existing capacity of fast pyrolysis.

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
        Sets the maximum diffusion rate of fast pyrolysis.
        """
        if not self.settings.investment.use_diffusion_rates:
            return self.max_diffusion_rate
        diffusion_rates = TechnologyDiffusionMannhardt(source_path=self.source_path)
        return diffusion_rates.get_max_diffusion_rate(self)