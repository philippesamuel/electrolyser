PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS weather (
	id INTEGER NOT NULL, 
	timestamp DATETIME NOT NULL, 
	temperature_k FLOAT NOT NULL, 
	pressure_pa FLOAT NOT NULL, 
	humidity_percent FLOAT NOT NULL, 
	dew_point_k FLOAT NOT NULL, 
	wind_speed_m_s FLOAT NOT NULL, 
	wind_deg INTEGER NOT NULL, 
	wind_gust_m_s FLOAT, 
	PRIMARY KEY (id)
);
INSERT INTO weather(timestamp, temperature_k, pressure_pa, humidity_percent, dew_point_k, wind_speed_m_s, wind_deg, wind_gust_m_s) VALUES('2026-01-10 21:32:39+00:00',269.7900000000000204,101800.0,85.0,267.8799999999999955,4.919999999999999929,320,NULL);
INSERT INTO weather(timestamp, temperature_k, pressure_pa, humidity_percent, dew_point_k, wind_speed_m_s, wind_deg, wind_gust_m_s) VALUES('2026-01-10 21:33:39+00:00',269.7300000000000181,101800.0,85.0,267.8199999999999932,4.919999999999999929,320,NULL);
INSERT INTO weather(timestamp, temperature_k, pressure_pa, humidity_percent, dew_point_k, wind_speed_m_s, wind_deg, wind_gust_m_s) VALUES('2026-01-10 21:34:49+00:00',269.7300000000000181,101800.0,85.0,267.8199999999999932,4.919999999999999929,320,NULL);
COMMIT;
