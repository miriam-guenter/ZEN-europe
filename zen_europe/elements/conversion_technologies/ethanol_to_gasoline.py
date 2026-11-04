from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from zen_creator.model import Model

from zen_creator import AssumptionInformation, Attribute, ConversionTechnology


class EthanolToGasoline(ConversionTechnology):
    """Dummy technology that uses ethanol 1:1 (energy basis) as gasoline for
    petrol cars. Blending limits (e.g. E10) are not considered. No costs and no
    capacity limits."""

    name: str = "ethanol_to_gasoline"

    def __init__(self, model: Model, power_unit: str = "MW"):
        super().__init__(model=model, power_unit=power_unit)

    def _set_reference_carrier(self) -> Attribute:
        """
        Sets the reference carrier of ethanol to gasoline to gasoline.
        """
        return Attribute(
            name="reference_carrier", default_value=["gasoline"], element=self
        )

    def _set_input_carrier(self) -> Attribute:
        """
        Sets the input carrier of ethanol to gasoline to ethanol.
        """
        return Attribute(name="input_carrier", default_value=["ethanol"], element=self)

    def _set_output_carrier(self) -> Attribute:
        """
        Set the output carrier of ethanol to gasoline to gasoline.
        """
        return Attribute(name="output_carrier", default_value=["gasoline"], element=self)

    def _set_conversion_factor(self) -> Attribute:
        """
        Return the conversion factor of ethanol to gasoline: one unit of ethanol
        energy replaces one unit of gasoline energy.
        """
        attr = self.conversion_factor
        attr.set_data(
            default_value=[{"ethanol": {"default_value": 1, "unit": "GWh/GWh"}}],
            source=AssumptionInformation(
                description=(
                    "Ethanol replaces gasoline 1:1 on an energy basis. Blending "
                    "limits (e.g. E10) are not considered."
                )
            ),
        )
        return attr

    def _set_lifetime(self) -> Attribute:
        """
        Sets the lifetime of ethanol to gasoline.
        """
        attr = self.lifetime
        attr.set_data(
            default_value=50,
            source=AssumptionInformation(
                description="Dummy technology; lifetime has no economic effect."
            ),
        )
        return attr