-- View: v_wind_power
-- Description: Calculates theoretical wind power and air density based on weather data.
-- Logic matches: backend/src/models/air.py and wind.py

CREATE VIEW v_wind_power AS
WITH step1_conversions AS (
  SELECT
    id,
    timestamp,
    temperature_k,
    pressure_pa,
    wind_speed_m_s,
    (humidity_percent / 100.0) AS humidity_frac,
    (temperature_k - 273.15) AS temperature_c
  FROM weather
),
step2_saturation AS (
  SELECT
    *,
    -- Saturation vapor. Tetens formula (es)
    CASE 
      WHEN temperature_c >= 0 THEN 
          610.78 * EXP((17.27  * temperature_c)/(temperature_c + 237.3))
      ELSE
          610.78 * EXP((21.875 * temperature_c)/(temperature_c + 265.5))
    END AS saturation_vapor_pressure_pa
  FROM step1_conversions
),
step3_partial_pressures AS (
  SELECT
    *,
    -- Vapor pressure (e = humidity * es)
    (humidity_frac * saturation_vapor_pressure_pa) AS vapor_pressure_pa,
    -- Dry air pressure (pd = p_total - e)
    (pressure_pa - humidity_frac * saturation_vapor_pressure_pa) AS dry_air_pressure_pa
  FROM step2_saturation
),
step4_densities AS (
  SELECT
    *,  
    -- Densities from ideal gas law ( rho_i = (p_i * MM_i) / (R * T) )
    (dry_air_pressure_pa / (287.05  * temperature_k)) AS dry_air_density_kg_m3,
    (  vapor_pressure_pa / (461.495 * temperature_k)) AS   vapor_density_kg_m3
  FROM step3_partial_pressures
),
step5_total_density AS (
  SELECT
    *,
    (dry_air_density_kg_m3 + vapor_density_kg_m3) AS moist_air_density_kg_m3
  FROM step4_densities
)
SELECT
    timestamp,
    temperature_k,
    pressure_pa,
    humidity_frac AS humidity,
    wind_speed_m_s,
    temperature_c,
    moist_air_density_kg_m3,
    -- Theoretical specific wind power (Watts / m^2)
    -- (P/A) = 0.5 * rho * Cp * v^3
    -- Cp_max = 16/27 (Betz limit)
    -- multiply by efficiency (0 - 100%) to get actual wind power
    (
      (0.5 * (16.0/27.0) * moist_air_density_kg_m3 * POWER(wind_speed_m_s, 3))
    ) AS max_specific_wind_power_watts_m2
FROM step5_total_density