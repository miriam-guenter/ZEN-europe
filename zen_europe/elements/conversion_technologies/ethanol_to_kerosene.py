from __future__ import annotations

from typing import TYPE_CHECKING

from zen_europe.datasets.datasets.technology.ethanol_to_jet_geleynse import (
    EthanolToJetGeleynse,
)
from zen_europe.datasets.datasets.technology.technology_diffusion_mannhardt import (
    TechnologyDiffusionMannhardt,
)

if TYPE_CHECKING:
    from zen_creator.model import Model

from zen_creator import AssumptionInformation, Attribute, ConversionTechnology


class EthanolToKerosene(ConversionTechnology):
    """Class containing all data and assumptions for the upgrading of ethanol to
    jet fuel (alcohol-to-jet: dehydration, oligomerization, hydrogenation). The jet
    fuel is modelled as kerosene."""

    name: str = "ethanol_to_kerosene"

    def __init__(self, model: Model, power_unit: str = "MW"):
        super().__init__(model=model, power_unit=power_unit)

    # ---------- Required methods that are called during object construction ----------

    def _set_reference_carrier(self) -> Attribute:
        """
        Sets the reference carrier of ethanol to jet to kerosene.
        """
        return Attribute(
            name="reference_carrier", default_value=["kerosene"], element=self
        )

    def _set_input_carrier(self) -> Attribute:
        """
        Sets the input carrier of ethanol to jet to ethanol, hydrogen (for the
        hydrogenation), electricity and natural gas (steam and fired heaters).
        """
        return Attribute(
            name="input_carrier",
            default_value=["ethanol", "hydrogen", "electricity", "natural_gas"],
            element=self,
        )

    def _set_output_carrier(self) -> Attribute:
        """
        Set the output carrier of ethanol to jet to kerosene and the diesel and
        gasoline cuts.
        """
        return Attribute(
            name="output_carrier",
            default_value=["kerosene", "diesel", "gasoline"],
            element=self,
        )

    # ---------- Required methods that are called during object build ----------

    def _set_lifetime(self) -> Attribute:
        """
        Sets the lifetime of ethanol to jet.

        """
        dataset = EthanolToJetGeleynse(source_path=self.source_path)
        return dataset.get_lifetime(self)

    def _set_conversion_factor(self) -> Attribute:
        """
        Return the conversion factor of ethanol to jet.

        """
        dataset = EthanolToJetGeleynse(source_path=self.source_path)
        return dataset.get_conversion_factor(self)

    def _set_construction_time(self) -> Attribute:
        """
        Sets the construction time of ethanol to jet.

        """
        if self.settings.investment.use_construction_times:
            dataset = EthanolToJetGeleynse(source_path=self.source_path)
            return dataset.get_construction_time(self)
        else:
            return self.construction_time

    def _set_capex_specific_conversion(self) -> Attribute:
        """
        Sets the specific capital expenditure (capex) for ethanol to jet.

        Returns:
            Attribute: An Attribute object containing the specific capex data.
        """
        dataset = EthanolToJetGeleynse(source_path=self.source_path)
        return dataset.get_capex_specific_conversion(self)

    def _set_opex_specific_fixed(self) -> Attribute:
        """
        Sets the specific fixed operational expenditure (opex) for ethanol to jet.

        Returns:
            Attribute: An Attribute object containing the specific fixed opex data.
        """
        dataset = EthanolToJetGeleynse(source_path=self.source_path)
        return dataset.get_opex_specific_fixed(self)

    def _set_opex_specific_variable(self) -> Attribute:
        """
        Sets the specific variable operational expenditure (opex) for ethanol to
        jet.

        Returns:
            Attribute: An Attribute object containing the specific variable opex data.
        """
        dataset = EthanolToJetGeleynse(source_path=self.source_path)
        return dataset.get_opex_specific_variable(self)

    def _set_capacity_existing(self) -> Attribute:
        """
        Sets the existing capacity of ethanol to jet.

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
        Sets the maximum diffusion rate of ethanol to jet.
        """
        if not self.settings.investment.use_diffusion_rates:
            return self.max_diffusion_rate
        diffusion_rates = TechnologyDiffusionMannhardt(source_path=self.source_path)
        return diffusion_rates.get_max_diffusion_rate(self)