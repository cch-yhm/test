#!/usr/bin/env python
# coding: utf-8


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from affine import Affine
import xarray as xr


def calcul_water_withdrawal():
    #read the file (d_w --Industrial water intake efficiency | d ---china industry factories)
    d_w = pd.read_csv('../工业企业用水效率/规模以上工业用水和工业产值汇总2008.csv')
    d = pd.read_csv('工业企业数据2008/工业企业数据2008/China_industry_2008_geolocation2.csv')
    # select useful columns
    d_ind = d[['企业匹配唯一标识码', '省（自治区、直辖市）', '地（区、市、州、盟）', '县（区、市、旗）','latitude', 'longitude',
               '行业门类代码','行业门类名称', '行业大类代码','行业大类名称', '工业总产值_当年价格(千元)']]
    # make sure two files' name(the province and the sector) consistent
    # combine the two files
    d_merge = pd.merge(d_ind,d_w,on =['省（自治区、直辖市）','行业大类名称'],how = 'left')
    # calculate every factory's water withdrawal
    d_merge['工厂取水量(单位：立方米)']=d_merge['工业总产值_当年价格(千元)'].mul(d_merge['用水效率2（单位：立方米/千元）'])
    #adjust the file 
    d_merge.drop(d_merge.columns[12:17],axis=1,inplace=True)
    d_merge.rename(columns={'取水总量（单位：万立方米）':'省取水总量（单位：万立方米）',
                            '工业总产值(当年价格，单位：亿元)':'省工业总产值(当年价格，单位：亿元)',
                            '用水效率1（单位：千元/立方米）':'省用水效率1（单位：千元/立方米）',
                            '用水效率2（单位：立方米/千元）':'省用水效率2（单位：立方米/千元）'},inplace=True)
    d_merge2 = d_merge.loc[~d_merge['行业大类名称'].isin(['水的生产和供应业'])]
    #save the data
    d_merge2.to_csv('data/China_industry_water_withdrawal.csv',index=False)
    print('water_withdrawal_calculate OK')
    return


def mapping_water_withdrawal_just(r, sector, save_netcdf):
    """transfer water withdrawal(table) to netcdf.
       r -- the resolution of netcdf [0.01,0.05,0.1,0.25,0.5];
       sector -- weather or not get the sector water withdrawal [True or False]
       save_netcdf -- weather or not save the format [True or False]"""
    # read the file d -- the industry water withdrawal(table);
    d=pd.read_csv('data/China_industry_water_withdrawal.csv')
    df = d
    print('Combined data loaded')
    # Affine transformation, global scale
    res = r # degree
    a = Affine(res,0,-180,0,-res,90)
    
    # get col and row number at the global scale
    df['col_g'], df['row_g'] = ~a * (df['longitude'], df['latitude'])
    
    # China range: lon 74: 135; lat 18: 54 # detemined based on max() min()
    lat_max=np.ceil(df.latitude.max())  #np.ceil   1.3→2，4.1→5，-1.2→-1
    lat_min=np.floor(df.latitude.min())  #np.floor  1.3→1，4.1→4，-1.2→-2
    lon_min=np.floor(df.longitude.min())
    lon_max=np.ceil(df.longitude.max())   
    ll = ~a * (np.floor(df.longitude.min()), np.floor(df.latitude.min())) # lower left pixel
    rr = ~a * (np.ceil(df.longitude.max()), np.ceil(df.latitude.max())) # upper right pixel
    print('China range defined as lat: %d to %d, and lon: %d to %d'%(lat_min, lat_max,lon_min, lon_max))
    
    # Get China range in cols and rows
    col_n = rr[0]-ll[0]+1
    row_n = ll[1]-rr[1]+1
    
    # Get regonal col/row within the China range
    df['row_r']=df['row_g']-rr[1]
    df['col_r']=df['col_g']-ll[0]

    # convert to int type 
    df['col_r'] = df['col_r'].apply(np.floor).astype(int)
    df['row_r'] = df['row_r'].apply(np.floor).astype(int)
    
    if sector: 
        # The first sector classification should be enough
        sector_list = np.sort(df['行业大类代码'].unique())     # '行业门类代码'just 'C/D/E'，‘行业大类代码'-sector :36
        # create a var to save mapping results in China for industiral value of different sectors
        map_value=np.zeros([sector_list.shape[0],int(row_n),int(col_n)])  
        # aggregate values to pixel
        row_col_value = df.groupby(['row_r','col_r','行业大类代码']).sum().reset_index()
        # Do mapping
        for i, s in enumerate(sector_list):
            temp_v= np.zeros([int(row_n),int(col_n)]) # temporary 2d value  
            temp_v[row_col_value.loc[row_col_value['行业大类代码']==s,'row_r'],
                         row_col_value.loc[row_col_value['行业大类代码']==s,'col_r']] = row_col_value.loc[row_col_value['行业大类代码']==s, 
                                                                                                  '工厂取水量(单位：立方米)']
           
            map_value[i,:,:]=temp_v
    else:
        # create a var to save mapping results in China for totol industiral value
        map_value=np.zeros([int(row_n),int(col_n)])
        # aggregate values to pixel
        row_col_value = df.groupby(['row_r','col_r']).sum().reset_index()
        map_value[row_col_value['row_r'],row_col_value['col_r']]=row_col_value['工厂取水量(单位：立方米)']

    if save_netcdf:
        # Add half res for center lat/lon of the grid cell
        lat_values = np.arange(lat_max, lat_min -res/2,-res)-res/2
        lon_values = np.arange(lon_min, lon_max+res/2, res)+res/2
        if sector: 
            map_value_net = xr.DataArray(map_value,
                                 coords=[sector_list,lat_values,lon_values],
                                 dims=["sector","lat","lon"], name='ww')
            fn='data/industrial_water_withdrawal_sector_res%.2f.nc'%res
            
        else:    
            map_value_net = xr.DataArray(map_value,
                                 coords=[lat_values, lon_values],
                                 dims=["lat","lon"], name='ww')
            fn='data/industrial_water_withdrawal_res%.2f.nc'%res
            
        d_out = map_value_net.to_dataset()
        d_out.attrs = {'long name': 'industrial water withdrawal','units':'cubic meters (m³)'}
        #这里也有
        d_out.to_netcdf(fn)
        print('netcdf file saved')
    return map_value


def mapping_water_withdrawal_year_pre(dw,dy,lat,lon):
    """ allocate the total water withdrawal to every month.
        dw -- must be a dataArray
        dy -- should be the rate of every sector's monthly water withdrawal 
        lat,lon -- dw 's resolution '"""
    month_list = np.array([1,2,3,4,5,6,7,8,9,10,11,12])
    sector_list = np.sort(dw.sector)
    t0 = xr.DataArray(np.zeros((12,len(sector_list),lat,lon)),
                      coords=[month_list,sector_list,dw.lat,dw.lon],
                      dims=["month","sector","lat","lon"],
                      name='ww')
    label=[1,2,3,4,5,6,7,8,9,10,11,12]
    sector_c = ['煤炭开采和洗选业', '石油和天然气开采业', '黑色金属矿采选业', '非金属矿采选业','China_mining',#'其他采矿业', 
                '农副食品加工业', '食品制造业', '饮料制造业', '烟草制品业','纺织业工业','纺织服装鞋帽制造业', '皮革毛皮羽毛(绒)及其制品业',
                '木材加工及木竹藤棕草制品业','家具制造业', '造纸及纸制品业', '印刷业和记录媒介的复制业', '文教体育用品制造业',
                '石油加工炼焦及核燃料加工业','化学原料及化学制品制造业', '医药制造业', '化学纤维制造业','橡胶制品业', '塑料制品业',  
                '非金属矿物制品业', '黑色金属冶炼及压延加工业', '金属制品业', '通用设备制造业', '专用设备制造业', '交通运输设备制造业',
                '电气机械及器材制造业', '通信设备计算机及其他电子设备制造业',  '仪器仪表及文化办公用机械制造业', '工艺品及其他制造业',
                'China_manufacture',#'废弃资源和废旧材料回收加工业'
                '电力、热力的生产和供应业','燃气生产和供应业']

    for j in range(36):
        dw_s = dw.isel(sector=j)
        dy_s = dy[[sector_c[j]]]  

        for i in range(12):
            label[i] = np.array(dy_s)[i]
            map_month = dw_s*label[i]
            t0[i,j,:,:] = map_month
            
    d_out = t0.to_dataset()
    d_out.attrs = {'long name': 'industrial water withdrawal','units':'cubic meters (m³)'}
    fn='data/industrial_water_withdrawal_year2008.nc'
    d_out.to_netcdf(fn)
    return  


def mapping_water_withdrawal_year():
    """prepare all the files and make the month data truely"""
    d1 = pd.read_csv('../工业年内用水变化/mining产量年内占比及各二级产业全国产量年内占比_2006-2010mean.csv')
    d2 = pd.read_csv('../工业年内用水变化/manufacture产量年内占比及各二级产业全国产量年内占比_2006-2010mean.csv')
    d3 = pd.read_csv('../工业年内用水变化/ele_heat产量年内占比及各二级产业全国产量年内占比_2006-2010mean.csv')
    f=[d1,d2,d3]
    dy = pd.concat(f,axis=1)#all the sector monthly rate 
    d_n =xr.open_dataset('data/industrial_water_withdrawal_sector_res0.10.nc')#every piexl
    mapping_water_withdrawal_year_pre(d_n['ww'],dy,len(d_n['ww'].lat),len(d_n['ww'].lon))
    print('year_variation OK')
    return               




if __name__=="__main__":
#     calcul_water_withdrawal()
#     mapping_water_withdrawal_just(0.1, sector=True, save_netcdf=True)
#     mapping_water_withdrawal_just(0.1, sector=False, save_netcdf=True)
#     mapping_water_withdrawal_year()   







