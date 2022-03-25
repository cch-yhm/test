import xarray as xr
import numpy as np
from affine import Affine
import matplotlib.pyplot as plt

#ds = xr.open_dataset('/home/liyan/Downloads/gsipL3_g13_GENHEM_2014121_0045.nc')
ds2 = xr.open_dataset('/home/liyan/Downloads/gsipL2_goes13_GENHEM_2014121_0045.nc')

lon2=np.unique(ds2['pixel_longitude'].data)
lon2=lon2[~np.isnan(lon2)]

lat2=np.unique(ds2['pixel_latitude'].data)
lat2=lat2[~np.isnan(lat2)]

df = ds2[['pixel_latitude','pixel_longitude','cloud_mask']].to_dataframe().dropna() #.to_csv('/media/liyan/HDD/Project/Cloud/data/gsipv3_test.csv')

# Define Affine of 0.5 degree
a = Affine(0.05,0,-180,0,-0.05,90)
# get col and row number
df['col'], df['row'] = ~a * (df['pixel_longitude'], df['pixel_latitude'])
# need to floor to get integer col and row

df['col'] = df['col'].apply(np.floor).astype(int)
df['row'] = df['row'].apply(np.floor).astype(int)

temp = df.groupby(['row','col']).max().reset_index()

c=np.zeros([3600,7200])

c[temp['row'],temp['col']]=temp['cloud_mask']

plt.imshow(c==0)
plt.show()

print('OK')
# plt.colorbar()

