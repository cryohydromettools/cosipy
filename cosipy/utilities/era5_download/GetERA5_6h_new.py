import cdsapi
import os

client = cdsapi.Client()
dataset = "reanalysis-era5-single-levels"

# Create output directory
output_dir = "ERA5"
os.makedirs(output_dir, exist_ok=True)

# Define years, fixed date (Jan 1), and times
years = [str(y) for y in range(1979, 1981)]  # From 1979 to 1990 inclusive
month = ["01"]
day = ["01"]
times = ["00:00", "06:00", "12:00", "18:00"]
area = [-8, -74, -9, -73],  # North, West, South, East
# Loop through each year and download
for year in years:
    request = {
        "product_type": "reanalysis",
	"data_format": "netcdf",
	"download_format": "unarchived",
        "variable": [
            "10m_u_component_of_wind",
            "10m_v_component_of_wind",
            "2m_dewpoint_temperature",
            "2m_temperature",
            "surface_pressure",
            "geopotential"
        ],
        "year": year,
        "month": month,
        "day": day,
        "time": times,
        "area": area
    }

    target = os.path.join(output_dir, f"ERA5_{year}_ins.nc")
    print(f"Downloading {target}...")
    client.retrieve(dataset, request, target)

    request = {
        "product_type": "reanalysis",
	"data_format": "netcdf",
	"download_format": "unarchived",
        "variable": [
            "total_precipitation",
            "surface_solar_radiation_downwards",
            "surface_thermal_radiation_downwards",
            "snowfall"
        ],
        "year": year,
        "month": month,
        "day": day,
        "time": times,
        "area": area
    }

    target = os.path.join(output_dir, f"ERA5_{year}_accum.nc")
    print(f"Downloading {target}...")
    client.retrieve(dataset, request, target)


