with source as (
    select * from {{ source('weather_system', 'weather') }}
),

calculated as (
    select
        id,
        timestamp,
        temperature_k,
        pressure_pa,
        wind_speed_m_s,
        (humidity_percent / 100.0) as relative_humidity,
        -- Air Density Calculation (Tetens Formula approximation in SQL)
        (100 * 6.112 * exp((17.67 * (temperature_k - 273.15)) / (temperature_k - 29.65))) as saturation_vapor_pressure_pa,
        (relative_humidity * saturation_vapor_pressure_pa) as vapor_pressure_pa,
        (pressure_pa - vapor_pressure_pa) as dry_air_pressure_pa,
        (dry_air_pressure_pa / (287.05 * temperature_k)) as density_dry_air,
        (vapor_pressure_pa / (461.495 * temperature_k)) as density_water_vapor,
        density_dry_air + density_water_vapor as air_density_kg_m3,

    from source
)

select * from calculated