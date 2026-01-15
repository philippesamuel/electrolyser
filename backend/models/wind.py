"""Model for wind turbine power"""

import numpy as np
from pydantic import BaseModel, Field

BETZ_LIMIT = 16 / 27  # Maximum theoretical efficiency of a wind turbine


# we assume a constant power coefficient for simplicity
# in practice Cp is a function of tip-speed ratio and blade pitch angle
class WindTurbineModel(BaseModel):
    rotor_diameter_m: float = Field(
        ..., ge=0, description="Diameter of the wind turbine rotor in meters"
    )
    power_coefficient: float = Field(
        ...,
        ge=0,
        le=BETZ_LIMIT,
        description="Power coefficient (Cp) of the wind turbine",
    )

    @property
    def rotor_area_m2(self) -> float:
        """Calculate the rotor swept area."""
        return np.pi * (self.rotor_diameter_m / 2) ** 2

    def power_output_watts(
        self, wind_speed_m_s: float, air_density_kg_m3: float = 1.225
    ) -> float:
        """Calculate the power output of the wind turbine."""
        pho = air_density_kg_m3
        A = self.rotor_area_m2
        Cp = self.power_coefficient
        v = wind_speed_m_s
        return (pho * A * Cp * v**3) / 2
