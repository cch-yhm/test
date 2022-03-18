import pandas as pd
import numpy as np
from geopy.geocoders import BaiduV3
import glob

def location_transfer():
    """geolocation transfer have some limitations: the 'api_key'_id can transfer 300,000 items everyday"""
    #read applied api_key(personal)
    d_geo = open('geolocation.txt')
    geolocator = BaiduV3(d_geo.readline().strip(), )##
    #read files
    d_geo = pd.read_
    d = pd.concat(pd.read_excel(f,usecols=[0]+list(range(5,12))) for f in glob.glob('工业企业数据2008/工业企业数据（2008）*-*行.xls')
    d.iloc[:,1:] = d.iloc[:,1:].fillna('')
    
    n1=0
    #get the number of row
    n2=len(t)
    #transfer address to geolocation
    for i in range(n1,n2):
        # extract location information from Baidu api
        location = geolocator.geocode(d.iloc[i,1:8].sum())
        d.loc[i,'latitude']=location.latitude
        d.loc[i,'longitude']=location.longitude
        d.loc[i,'precise']=location.raw['precise']
        d.loc[i,'confidence']=location.raw['confidence']
        d.loc[i,'comprehension']=location.raw['comprehension']
        d.loc[i,'level']=location.raw['level']
    
    # save the merged data
    d.to_excel('工业企业数据2013/工业企业数据（2008）/China_factory_location_2008.xls',index= False)
    print('transfer data saved')


def make_combined_data():
    # columns to be extracted
    cols=['企业匹配唯一标识码','行业门类代码', '行业门类名称', '行业大类代码', '行业大类名称', '行业中类代码',
           '行业中类名称', '行业小类代码', '行业小类名称', '主要业务活动（或主要产品）1', '主要业务活动（或主要产品）2',
           '主要业务活动（或主要产品）3','工业总产值_当年价格(千元)']
    
    # Read all excel files
    df_raw = pd.concat([pd.read_excel(f,usecols=cols) for f in glob.glob('工业企业数据2008/工业企业数据（2008）*-*行.xls')],
                       ignore_index=True)
    
    # Read all csv files with geolocation information
    df = pd.read_excel('工业企业数据2008/工业企业数据2008/China_factory_location_2008.xls')
    
    # Merge two data frames using unique id
    df_final=df.merge(df_raw,on='企业匹配唯一标识码')
    
    # Correct error for line 314475: 天津市武清区武清区南蔡村镇	 found an error, need check others
    df_final.loc[254475,'longitude']=117.02540723599012 
    df_final.loc[254475,'latitude']=39.49337517224572 
    
    # save the merged data
    df_final.to_csv('工业企业数据2008/工业企业数据2008/China_industry_geo_output_2008.csv',index = False)
    print('Combined data saved')



if __name__=="__main__":
####    location_transfer()
####    make_combined_data()
    

