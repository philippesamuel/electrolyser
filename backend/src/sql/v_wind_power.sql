-- View: v_wind_power
-- Description: Calculates theoretical wind power and air density based on weather data.
-- Logic matches: backend/src/models/air.py and wind.py

CREATE VIEW v_wind_power AS
WITH constants AS (
  SELECT
    287.05  AS R_dry_air,         -- J/(kg·K)
    461.495 AS R_water_vapor,     -- J/(kg·K)
      3.0   AS cut_in_speed_m_s,  -- Min speed to start generating power
     25.0   AS cut_out_speed_m_s  -- Max speed to stop generating power
),
step1_conversions AS (
  SELECT
    id,
    timestamp,
    updated_at,
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
    d.*,
    c.R_dry_air, 
    c.R_water_vapor, 
    -- Densities from ideal gas law ( rho_i = (p_i * MM_i) / (R * T) )
    (d.dry_air_pressure_pa / (c.R_dry_air  * d.temperature_k)) AS dry_air_density_kg_m3,
    (  d.vapor_pressure_pa / (c.R_water_vapor * d.temperature_k)) AS   vapor_density_kg_m3
  FROM step3_partial_pressures d 
  CROSS JOIN constants c
),
step5_total_density AS (
  SELECT
    *,
    (dry_air_density_kg_m3 + vapor_density_kg_m3) AS moist_air_density_kg_m3
  FROM step4_densities
),
step6_status AS (
  SELECT
    d.*,
    c.cut_in_speed_m_s,
    c.cut_out_speed_m_s,
    CASE 
      WHEN d.wind_speed_m_s 
        BETWEEN c.cut_in_speed_m_s AND c.cut_out_speed_m_s 
        THEN 1
      ELSE 0
     END AS turbine_is_on
  FROM step5_total_density d
  CROSS JOIN constants c
)
SELECT
    id AS weather_id,
    timestamp,
    updated_at,
    temperature_k,
    pressure_pa,
    humidity_frac AS humidity,
    wind_speed_m_s,
    temperature_c,
    moist_air_density_kg_m3,
    turbine_is_on,
    -- Theoretical specific wind power (Watts / m^2)
    -- (P/A) = 0.5 * rho * Cp * v^3
    -- Cp_max = 16/27 (Betz limit)
    -- multiply by efficiency (0 - 100%) to get actual wind power
    (
      turbine_is_on * (0.5 * (16.0/27.0) * moist_air_density_kg_m3 * POWER(wind_speed_m_s, 3))
    ) AS max_specific_wind_power_watts_m2
FROM step6_status;
