from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from zen_creator.model import Model

from zen_creator import AssumptionInformation, Attribute, ConversionTechnology

# Maximum share of dry biomass in the feedstock of anaerobic digestion,
# on an energy basis (all biomass carriers are in GWh).
MAX_DRY_SHARE_BIOGAS = 0.13


class CoDigestionMix(ConversionTechnology):
    """Dummy technology that mixes wet and dry biomass into the anaerobic
    digestion feedstock at the maximum dry share.

    Together with the 1:1 route `wet_biomass_biogas_to_biogas_feedstock`, the
    dry share of the feedstock can take any value between 0 and
    `MAX_DRY_SHARE_BIOGAS`."""

    name: str = "codigestion_mix"

    def __init__(self, model: Model, power_unit: str = "MW"):
        super().__init__(model=model, power_unit=power_unit)

    def _set_reference_carrier(self) -> Attribute:
        return Attribute(
            name="reference_carrier", default_value=["biogas_feedstock"], element=self
        )

    def _set_input_carrier(self) -> Attribute:
        return Attribute(
            name="input_carrier",
            default_value=["wet_biomass_biogas", "dry_biomass_biogas"],
            element=self,
        )

    def _set_output_carrier(self) -> Attribute:
        return Attribute(
            name="output_carrier", default_value=["biogas_feedstock"], element=self
        )

    def _set_conversion_factor(self) -> Attribute:
        attr = self.conversion_factor
        attr.set_data(
            default_value=[
                {
                    "wet_biomass_biogas": {
                        "default_value": 1 - MAX_DRY_SHARE_BIOGAS,
                        "unit": "GWh/GWh",
                    }
                },
                {
                    "dry_biomass_biogas": {
                        "default_value": MAX_DRY_SHARE_BIOGAS,
                        "unit": "GWh/GWh",
                    }
                },
            ],
            source=AssumptionInformation(
                description=(
                    "Wet and dry biomass are mixed at the maximum dry share of "
                    f"{MAX_DRY_SHARE_BIOGAS:.0%} (energy basis) for co-digestion."
                )
            ),
        )
        return attr

    def _set_lifetime(self) -> Attribute:
        attr = self.lifetime
        attr.set_data(
            default_value=50,
            source=AssumptionInformation(
                description="Dummy technology; lifetime has no economic effect."
            ),
        )
        return attr
