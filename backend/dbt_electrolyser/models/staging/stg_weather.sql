select
    *
from {{ source('weather_system', 'weather') }}
-- dbt reads this from SQLite, calculates the math, 
-- and saves the result table into 'analytics.duckdb'