"""Model air properties"""

import numpy as np
from pydantic import BaseModel, Field


class AirState(BaseModel):
    temperature_c: float = Field(..., description="Air temperature in degrees Celsius")
    pressure_pa: float = Field(..., description="Air pressure in Pascals")
    relative_humidity: float = Field(
        ge=0, le=1, description="Relative humidity as a fraction (0 to 1)"
    )

    @property
    def density_kg_m3(self) -> float:
        """Calculate the density of humid air."""
        return calc_humid_air_density(
            temperature_c=self.temperature_c,
            pressure_pa=self.pressure_pa,
            relative_humidity=self.relative_humidity,
        )


def calc_humid_air_density(
    temperature_c: float, pressure_pa: float, relative_humidity: float
) -> float:
    """Calculate the density of humid air using the ideal gas law.

    Args:
        temperature_c (float): Temperature in degrees Celsius.
        pressure_pa (float): Atmospheric pressure in Pascals.
        relative_humidity (float): Relative humidity as a fraction (0 to 1).

    Returns:
        float: Density of humid air in kg/m^3.
    """
    # Constants
    R_dry_air = 287.05  # J/(kg·K)
    R_water_vapor = 461.495  # J/(kg·K)

    # Convert temperature to Kelvin
    temperature_k = temperature_c + 273.15

    # Calculate saturation vapor pressure using Tetens formula
    es = (
        6.112 * np.exp((17.67 * temperature_c) / (temperature_c + 243.5)) * 100
    )  # in Pa

    # Actual vapor pressure
    e = relative_humidity * es

    # Partial pressure of dry air
    pd = pressure_pa - e

    # Calculate density
    density_dry_air = pd / (R_dry_air * temperature_k)
    density_water_vapor = e / (R_water_vapor * temperature_k)

    return density_dry_air + density_water_vapor
