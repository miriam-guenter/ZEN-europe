from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from zen_creator.model import Model

from zen_creator.elements import Carrier
from zen_creator.utils.attribute import Attribute


class Digestate(Carrier):
    """Digestate from anaerobic digestion, in terms of its energy content.

    It can be used by other technologies (e.g. slow pyrolysis) or disposed of
    at no cost, which represents its use as fertilizer on fields."""

    name: str = "digestate"

    def __init__(self, model: Model, power_unit: str = "MW"):
        super().__init__(model=model, power_unit=power_unit)

    def _set_availability_import(self) -> Attribute:
        """
        Return the import availability of digestate. Digestate is only
        produced by anaerobic digestion.
        """
        return Attribute(
            "availability_import",
            default_value=0,
            element=self,
            unit=self.power_unit,
        )

    def _set_availability_export(self) -> Attribute:
        """
        Return the export availability of digestate. Unlimited, so surplus
        digestate can always leave the system (spread on fields).
        """
        return Attribute(
            "availability_export",
            default_value=np.inf,
            element=self,
            unit=self.power_unit,
        )

    def _set_availability_export_yearly(self) -> Attribute:
        """
        Return the yearly export availability of digestate (unlimited).
        """
        return Attribute(
            "availability_export_yearly",
            default_value=np.inf,
            element=self,
            unit=self.energy_unit,
        )