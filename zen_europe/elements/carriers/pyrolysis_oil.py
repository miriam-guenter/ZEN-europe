from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from zen_creator.model import Model

from zen_creator.elements import Carrier
from zen_creator.utils.attribute import Attribute


class PyrolysisOil(Carrier):
    """Raw pyrolysis oil (bio-crude) from slow and fast pyrolysis, before
    upgrading."""

    name: str = "pyrolysis_oil"

    def __init__(self, model: Model, power_unit: str = "MW"):
        super().__init__(model=model, power_unit=power_unit)

    def _set_availability_import(self) -> Attribute:
        """
        Return the import availability of pyrolysis oil. Pyrolysis oil is only
        produced domestically by pyrolysis.
        """
        return Attribute(
            "availability_import",
            default_value=0,
            element=self,
            unit=self.power_unit,
        )