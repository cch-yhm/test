#!/usr/bin/env python
# coding: utf-8

# In[1]:


import xarray as xr
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader
import cartopy.feature as cfeat
import matplotlib.ticker as mtick
import matplotlib as mlp
import seaborn as sns
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
get_ipython().run_line_magic('matplotlib', 'inline')


# In[ ]:


shp_path1=r'../shp_china/基本数据/中国行政区_包含沿海岛屿.shp'  
shp_path2=r'../shp_china/基本数据/省界.shp'
shp_path3=r'../shp_china/基本数据/九段线.shp'
shp_path4=r'../shp_china/基本数据/river-1j.shp'
shp1=shpreader.Reader(shp_path1)
shp2=shpreader.Reader(shp_path2)
shp3=shpreader.Reader(shp_path3)
shp4=shpreader.Reader(shp_path4)


# In[ ]:


d1 = xr.open_dataset('工业企业数据2008/industrial_water_withdrawal_res0.05.nc')
d1['water withdrawal'].values[d1['water withdrawal'].values==0]=np.nan
d1['industrial amount'].values[d1['industrial amount'].values==0]=np.nan
d1['water withdrawal'].values = d1['water withdrawal'].values/1000000


# In[ ]:


proj = ccrs.PlateCarree()
cbar_kwargs1 = {'anchor':(0.57,-0.3),'orientation': 'horizontal','label': 'Amount','pad': 0.065, 'shrink': 0.8,
                'format':'%.0f' }

fig = plt.figure(figsize=(8,8))#,projection=proj)
ax = fig.subplots(1, 1, subplot_kw={'projection': proj})

d1['industrial amount'].plot.imshow(ax=ax,robust=True,cmap='rocket_r' ,levels= 8,transform=ccrs.PlateCarree(),
                                    add_labels=False,cbar_kwargs=cbar_kwargs1)
                             #,vmin = 0,vmax =60,alpha=0.5)
ax.add_geometries(shp2.geometries(),crs=proj,facecolor='none',edgecolor='black',lw=0.5,alpha=0.8)
ax.add_geometries(shp3.geometries(),crs=proj,facecolor='none',edgecolor='black',lw=0.5,alpha=0.8)
# ax.add_geometries(shp4.geometries(),crs=proj,facecolor='lightblue',edgecolor='lightblue',lw=0.5,alpha=0.8)
#经纬度坐标的建立
ax.set_extent([70, 138, 15, 53])
ax.set_xticks([80,90,100,110,120,130],crs=ccrs.PlateCarree())
ax.set_yticks([20,30,40,50],crs=ccrs.PlateCarree())
lon_formatter = LongitudeFormatter(zero_direction_label=True)
lat_formatter = LatitudeFormatter()
ax.xaxis.set_major_formatter(lon_formatter)
ax.yaxis.set_major_formatter(lat_formatter)

ax.set_title("Distribution of all industries in China",fontsize =14,verticalalignment='bottom')
ax.text(72,55,'Number of all industries: 410160.',fontsize =12)

left, bottom, width, height = 0.76, 0.29, 0.15, 0.15
ax2 = fig.add_axes([left, bottom, width, height], projection=proj)
d1['industrial amount'].plot.imshow(ax=ax2,robust=True,cmap='rocket_r' ,levels= 8,transform=ccrs.PlateCarree(),
                                    add_labels=False,add_colorbar=False)
ax2.add_geometries(shp2.geometries(), linewidth=0.6, crs=proj,facecolor='none',edgecolor='black',lw=0.5,alpha=0.8)
ax2.add_geometries(shp3.geometries(),crs=proj,facecolor='k',edgecolor='black',lw=0.5,alpha=0.8)
ax2.set_extent([105, 125, 0, 25])

plt.savefig('08pre/fig2_number.jpg',dpi=300, bbox_inches='tight')


# In[ ]:


proj = ccrs.PlateCarree()
cbar_kwargs3 = {'orientation': 'horizontal','label': 'Water Withdrawal (million m$^{3}$)','pad': 0.065,'shrink': 0.8,
                'format':'%.0f' }
cmap5 = sns.color_palette("ch:start=.2,rot=-.3", as_cmap=True)

fig = plt.figure(figsize=(10,10))
ax = fig.subplots(1, 1, subplot_kw={'projection': proj})

d1['water withdrawal'].plot.imshow(ax=ax,robust=True,cmap=cmap5 ,levels= 8,transform=ccrs.PlateCarree(),
                                   add_labels=False,cbar_kwargs=cbar_kwargs3)
                             #,vmin = 0,vmax =60,alpha=0.5)
ax.add_geometries(shp2.geometries(),crs=proj,facecolor='none',edgecolor='black',lw=0.5,alpha=0.8)
ax.add_geometries(shp3.geometries(),crs=proj,facecolor='none',edgecolor='black',lw=0.5,alpha=0.8)
ax.set_extent([70, 138, 15, 53])
#经纬度坐标的建立
ax.set_xticks([80,90,100,110,120,130],crs=ccrs.PlateCarree())
ax.set_yticks([20,30,40,50],crs=ccrs.PlateCarree())
lon_formatter = LongitudeFormatter(zero_direction_label=True)
lat_formatter = LatitudeFormatter()
ax.xaxis.set_major_formatter(lon_formatter)
ax.yaxis.set_major_formatter(lat_formatter)

ax.set_title("Water withdrawal of all industries in China ",fontsize =16,verticalalignment='bottom')
ax.text(71,55,'Water withdrawal of all industries: 65.84817 billion m$^{3}$.',fontsize =12)

left, bottom, width, height = 0.76, 0.295, 0.15, 0.15
ax2 = fig.add_axes([left, bottom, width, height], projection=proj)
d1['water withdrawal'].plot(ax=ax2,robust=True,cmap=cmap5 ,levels= 8,transform=ccrs.PlateCarree(),
                            add_labels=False,add_colorbar=False)
ax2.add_geometries(shp2.geometries(), linewidth=0.6, crs=proj,facecolor='none',edgecolor='black',
                   lw=0.5,alpha=0.8)
ax2.add_geometries(shp3.geometries(),crs=proj,facecolor='k',edgecolor='black',lw=0.5,alpha=0.8)
ax2.set_extent([105, 125, 0, 25])

plt.savefig('08pre/fig2_withdrawal.jpg',dpi=300, bbox_inches='tight')

