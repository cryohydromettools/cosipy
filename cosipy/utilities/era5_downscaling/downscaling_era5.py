import numpy as np
import xarray as xr
import pandas as pd
import glob
import os
import warnings
warnings.filterwarnings("ignore")

## AWS Coordinates and Constants
hgt_aws = 3000
lon_aws = -73.5
lat_aws = -8.5

lapse_rate_T2 = -(1/100) # 1K/100m
lapse_rate_TD = -(0.9/100) # 1K/100m

g = 9.80665

# Constants for humidity calculation
T0 = 273.16
a1 = 611.21
a3 = 17.502
a4 = 32.19
R_dry = 287.0597
R_vap = 461.5250

# Define years to process
years_to_process = list(range(1979, 1981))  # From 1979 to 1981

# Paths
input_path = '../era5_download/ERA5/'
output_path = './csv_files/'


#breakpoint()

for year in years_to_process:
    filename1 = os.path.join(input_path, f'ERA5_{year}_ins.nc')
    filename2 = os.path.join(input_path, f'ERA5_{year}_accum.nc')
        
    print(f"Processing year {year}...")

    ds1 = xr.open_dataset(filename1)
    ds2 = xr.open_dataset(filename2)

    df_nc  = ds1.sel(longitude=lon_aws, latitude=lat_aws, method="nearest")#.mean(['longitude', 'latitude'])
    df_nc2 = ds2.sel(longitude=lon_aws, latitude=lat_aws, method="nearest")#.mean(['longitude', 'latitude'])
    
    print(df_nc)
    print(df_nc2)
    
    #breakpoint()

    hgt_era = df_nc['z'][0].values / g

    t2m = df_nc['t2m'].values + (hgt_aws - hgt_era) * lapse_rate_T2
    d2m = df_nc['d2m'].values + (hgt_aws - hgt_era) * lapse_rate_TD

    press = df_nc['sp'] / 100
    SLP = press / np.power((1 - (0.0065 * hgt_era) / 288.15), 5.255)
    press = SLP * np.power((1 - (0.0065 * hgt_aws) / 288.15), 5.22)

    T = t2m
    Td = d2m
    P = press.values
    T_e_sat = a1 * np.exp(a3 * ((T - T0) / (T - a4)))
    Td_e_sat = a1 * np.exp(a3 * ((Td - T0) / (Td - a4)))
    RH = 100 * Td_e_sat / T_e_sat
    RH[RH > 100] = 100.0
    RH[RH < 0] = 0.0

    U10 = np.sqrt(df_nc['u10']**2 + df_nc['v10']**2)
    U2 = U10 * (np.log(2 / (2.12 * 1000)) / np.log(10 / (2.12 * 1000)))

    SWin = df_nc2['ssrd'] / 3600
    SWin = SWin.where(SWin > 0, 0)

    LWin = df_nc2['strd'] / 3600
    LWin = LWin.where(LWin > 0, 0)


    tp = df_nc2['tp'] * 1000
    tp = tp.where(tp > 0, 0)

    sf = df_nc2['sf']
    sf = sf.where(sf > 0, 0)

    df_sim = pd.DataFrame({
        'SWin': SWin.values,
        'LWin': LWin.values,
        't2m': t2m,
        'rh': RH,
        'u2': U2.values,
        'tp': tp.values,
        'sf': sf.values,
        'press': press.values,
    }, index=df_nc.valid_time.values)

    df_sim.index.name = 'time'

    # Save to CSV
    output_file = os.path.join(output_path, f'ERA5_{year}_glac.csv')
    df_sim.to_csv(output_file, sep='\t')
    print(f"Saved: {output_file}")

