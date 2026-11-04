from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from zen_creator.model import Model

from zen_creator.elements import Carrier
from zen_creator.utils.attribute import Attribute


class Ethanol(Carrier):
    """Ethanol from first generation and cellulosic ethanol production."""

    name: str = "ethanol"

    def __init__(self, model: Model, power_unit: str = "MW"):
        super().__init__(model=model, power_unit=power_unit)

    def _set_availability_import(self) -> Attribute:
        """
        Return the import availability of ethanol. Ethanol is only produced
        domestically for now.
        """
        return Attribute(
            "availability_import",
            default_value=0,
            element=self,
            unit=self.power_unit,
        )