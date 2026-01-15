select
    timestamp,
    density_dry_air,
    wind_speed_m_s,
    -- Power Formula: 0.5 * rho * A * Cp * v^3
    0.5 * density_dry_air * (PI() * POW(100/2, 2)) * 0.45 * POW(wind_speed_m_s, 3) as power_output_watts
from {{ ref('stg_weather_physics') }}