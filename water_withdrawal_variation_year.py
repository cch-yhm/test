#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

get_ipython().run_line_magic('matplotlib', 'inline')


# ### code 

# #### 产品产量→产品产量年内占比→年内占比5年平均→产业年内占比5年平均


"""先算产品的平均再算产业的平均是不是不对？
   ——在我的算法里是正确的，因为我不是直接平均的，是计数平均的考虑到了均值的问题"""
"""共有3大类产业，每种大类产业需要储存3个过程文件，以便证明正确
   3个表：1产品占比的年内平均 2.产品的5年平均 3.产业的5年平均 """

def calcu_output_rate_mean(d):   
    d1 = d[d['Unnamed: 67']!=0]#去掉5年生产总量为0的产品类型
    d1.set_index(['省', '产品'],inplace=True)
    name = str(d.iloc[0:1,1:2].values)[4:5]
    #产品单独区分和计算年内占比
    f = pd.DataFrame()
    d_o_m = pd.DataFrame()
    for i in range(5):
        ##将每一年的产品单独区分
        f= d1.iloc[:,13*i:13*(i+1)]
        ##计算每月产量占全年的比例
        f[['01','02','03','04','05','06','07','08','09','10','11','12']] = f[f.columns[:-1]].div(f[2006+i].values,axis=0)
        f2= f.iloc[:,13:].T
        f2['year']=2006+i
        d_o_m = d_o_m.append(f2)#d_ct为采矿业全国各地产量占比年内变化2006_2010
        i = i+1
    #d_ct

    d_o_m.reset_index(inplace=True)
    d_o_m.rename(columns={'index':'month'},inplace=True)
    d_o_m.to_csv('全国各省产品产量占比年内变化2006_2010_'+name+'.csv',index=False)
    
    #产品5年平均比例（之所以不算mean 是因为中间有空值，但不是一年中所有月都是空值）
    ##月份值的处理
    mon_c = d_o_m.groupby('month').count()#计算每个省每种产量一共有多少个月份有数值
    mon_m = mon_c.max(axis=0).to_frame().T#取最大月份（多少年有值）
    mon_m.drop(['year'],axis=1,inplace=True)#转换为dataframe并去掉多余列
    ##产品总比例之和
    prod_s = d_o_m.groupby('month').sum()
    ##总数和月份数拼接
    prod_mon = prod_s.append(mon_m).T[1:]
    ##计算5年的月平均值
    prod_mon[['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov',
              'Dec']] = prod_mon[['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11','12']].div(prod_mon[0].values,axis=0)
    #prod_mon[[0]]为一共有多少个月有值
    #只选取平均后的结果
    prod_mean0 = prod_mon.iloc[:,13:]
    ##  prod_mean0['sum']=prod_mean0.apply(lambda x:sum(x),axis=1)# 检查数据是否正确
    ##  prod_mean0[prod_mean0['sum']>1.0001]  #检查 没有大于1的情况
    prod_mean = prod_mean0.reset_index()
    
    prod_mean.to_csv('全国各省产品产量占比年内变化_5year_mean_'+name+'.csv',index=False)            
    print('rate and mean OK')  


def transfer_output_kind(n,sort,labels,name):
    kind = pd.DataFrame()
    for j in range(n):
        a =  sort[j]
        a_j = a.groupby('省').sum() 
        a_j['产品数']=a.groupby('省').count().max(axis=1)
        a_j.reset_index(inplace=True)
        a_j[['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11',
             '12']] = a_j[['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']].div(a_j['产品数'].values,axis=0)
        a_j.set_index('省',inplace=True)
        a1 =a_j.iloc[:,13:]
        a1['sum']=a1.apply(lambda x:sum(x),axis=1)
        a1['产业']=labels[j]
        kind = kind.append(a1)

    ##  c[c['sum']>1.001]&c[c['sum']<0.99999]#已经验证过都为1
    kind.to_csv('全国各省产业产量占比年内变化_5year_mean_'+str(name)+'.csv')
    print('success')


#产品5年平均变成产业5年平均
def transfer_output_kind_ele(d,name):
    
    replacements_chanpin_chanye= {
       '产品': {
           r'发电量':'电力、热力的生产和供应业',
           r'煤气生产量':'燃气生产和供应业', 
       }
    }
    
    d.replace(replacements_chanpin_chanye, regex=True, inplace=True)
    d.rename(columns={'产品':'产业','Jan':'01', 'Feb':'02', 'Mar':'03', 'Apr':'04', 'May':'05', 'Jun':'06',
                      'Jul':'07', 'Aug':'08', 'Sep':'09', 'Oct':'10','Nov':'11', 'Dec':'12'},inplace=True)
    d.to_csv('全国各省产业产量占比年内变化_5year_mean_'+str(name)+'.csv',index=False)
    print('ele_heat success')



# #### 加权平均
"""有两种加权平均算法：
    1.省内比例加权——也进行了计算
    2.全国的二级产业比例加权——论文选择了这种"""


# ##### 省内加权

def calcul_weighted_factor_pro(d,name,row):
    C_value = float(d.iloc[:1,2:3].values)##全国各大类产业的总取值量
    # mining total water（all province)
    d_z = d.iloc[:32,1:3]
    d_z.rename(columns={'取水总量（单位：万立方米）': str(name)+'_water (10000 m3)'},inplace=True)
    #d_cw_z

    ### 省略其他采矿业取水——这一类型取水量确实非常少——row = 192
    # # d_try_drop = d.iloc[32:192,:3].groupby('地区').sum()
    # # d_drop = pd.merge(d_z,d_try_drop,on='地区',how='left')
    # # d_drop['differ'] = d_dorp.apply(lambda x:x[str(name)+'_water (10000 m3)']-x['取水总量（单位：万立方米）'],axis=1)
    # # d_drop['rate'] = d_dorp.apply(lambda x:x['取水总量（单位：万立方米）']/x[str(name)+'_water (10000 m3)'],axis=1)
    # # d_drop
    # ###  其他采矿业取水：内蒙古-23万立方米（0.99834）四川-19万立方米（0.99888） 辽宁-10万立方米（0.99958） 云南-6万立方米（0.99941） 
    # ###                  广西-3万立方米（0.99920）  其他均为1立方米or无
    ### 制造业二级产业用水——无省略——row = 992
    ### 电热业二级产业用水——省略水的生产和供应业——row = 96

    #submining water (all province) and calculating rate
    d_p = pd.merge(d.iloc[32:row,:3],d_z.iloc[:,:2],on='地区',how='left')
    d_p.rename(columns={'取水总量（单位：万立方米）':'sub'+str(name)+'_water (10000 m3)'},inplace=True)
    d_p['rate_sub_p']=d_p.apply(lambda x:x['sub'+str(name)+'_water (10000 m3)']/x[str(name)+'_water (10000 m3)'],axis=1)
    d_p['rate_p']=d_p[str(name)+'_water (10000 m3)']/C_value #### 408382.0为全国采矿业取水量
    #d_cw_p['rate_p'][1:32]为各省市占全国采矿业取水量比例
    ## d_cw_p

    ### 检查计算的加权系数是否为1
    ### d_cwp.groupby('地区').sum()#只有陕西之和>1（具体二级产业取水之和大于总采矿业取水量）,其他都小于1，其他采矿业原因

    d_p.to_csv('规模以上'+name+'用水各产业占全省的权重&各省占全国权重前32_2008.csv',index=False)
    print('weighted_province ok')


# ##### 二级产业加权

def calcul_weighted_factor_subindustry(d,name):
    C_value = float(d.iloc[:1,2:3].values)##全国各大类产业的总取值量
    #mining total water(all submining_China)
    d_c = d[d['地区'].isin(['全国'])].iloc[:,:3]
    #全国二级产业取水占全国大类产业的取水
    d_c['rate_sub_c'] = d_c['取水总量（单位：万立方米）']/C_value #### 408382.0为全国采矿业取水量
    d_c.rename(columns={'取水总量（单位：万立方米）':str(name)+'_water (10000 m3)'},inplace=True)
    # d_cw_c

    #submining water（calculate rate）
    d_k = pd.merge(d.iloc[32:,:3],d_c,on='产业',how='left')
    d_k.drop(d_k.columns[3],axis=1,inplace=True)
    #每个省的二级产业取水占全国二级产业取水的比例
    d_k['rate_sub_p'] = d_k.apply(lambda x:x['取水总量（单位：万立方米）']/x[str(name)+'_water (10000 m3)'],axis=1)
    d_k.rename(columns={'地区_x':'地区'},inplace=True)
    # d_cw_k
    d_k.to_csv('全国规模以上各产业工业用水占'+name+'的权重&各省占全国权重_2008.csv',index=False)
    print('weighted_sub ok')



# #### 用水比例与产量数据结合

def replacement_water(f):
    replacements_chanye1 = {
       '产业': {
           r'电力热力的生产和供应业':'电力、热力的生产和供应业'}
    }
    f.replace(replacements_chanye1, regex=True, inplace=True)


def replacement_province(f):
    replacements_province = {
       '地区': {
           #r'全国':'China',
           r'北京':'北京市',
           r'天津':'天津市', 
           r'河北':'河北省', 
           r'山西':'山西省',
           #r'内蒙古':'内蒙古',
           r'辽宁':'辽宁省', 
           r'吉林':'吉林省',
           #r'黑龙江':'黑龙江', 
           r'上海':'上海市', 
           r'江苏':'江苏省',
           r'浙江':'浙江省', 
           r'安徽':'安徽省',
           r'福建':'福建省',
           r'江西':'江西省',
           r'山东':'山东省',
           r'河南':'河南省', 
           r'湖北':'湖北省', 
           r'湖南':'湖南省', 
           r'广东':'广东省', 
           r'广西':'广西区', 
           r'海南':'海南省',
           r'重庆':'重庆市',
           r'四川':'四川省',
           r'贵州':'贵州省',
           r'云南':'云南省',
           r'西藏':'西藏区',
           r'陕西':'陕西省',
           r'甘肃':'甘肃省',
           r'青海':'青海省',
           r'宁夏':'宁夏区',
           r'新疆':'新疆区'
       }
    }
    f.replace(replacements_province, regex=True, inplace=True)
    print('province ok')


# ##### 省级别数据处理

def calcul_rate_pro(d_w,d_ind,name):
    d_p_pre=pd.merge(d_w,d_ind,on=['产业','省'],how='right')
    # d_mp_pre

    # calculate 每一个二级产业每月产量在全省产量的比重
    d_p_pre[['R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7', 'R8', 'R9', 'R10', 'R11',
             'R12']] = d_p_pre[['01', '02', '03', '04', '05', '06', '07', '08','09', '10', '11', 
                                '12']].mul(d_p_pre[d_p_pre.columns[4]].values,axis=0)
    # d_mp_pre

    #去掉多余的部分
    #电热业的计算需要把[2:19]改为[2:18],没有整体汇总的['sum']列
    d_p_sub = d_p_pre.drop(d_p_pre.columns[2:19],axis=1)#5年平均值后每个省每个产业月产量占全省的百分比
    
    # d_mp_submin

    # 每个省采矿业每月用水占比
    d_p=d_p_sub.groupby('省').sum()
    d_p['sum']=d_p.apply(lambda x:sum(x),axis=1)# 检查 采矿业用水比例是不是为1
    d_p.reset_index(inplace=True)
    #d_p
    ##采矿业有些省份有特殊情况
    # 1.北京（用水权重中有4种产业，但实际上只有2种产业有产量数据---所以只能计算出0.78的用水变化）
    # 2.内蒙古（用水权重中有5种产业，但实际上只有4种产业有产量数据---所以只能计算出0.96的用水变化）
    # 3.黑龙江（用水权重中有5种产业，但实际上只有4种产业有产量数据---所以只能计算出0.98的用水变化）
    # #缺失值继续算需要用全国均值补全
    # #其他0.999的问题是由于本身产量不足（省略了其他采矿业）
    ##制造业甘肃省情况特殊
    #

    #calculate 每个省大类产业产量占全国的比例
    d_c_pre = pd.merge(d_p,d_w[['省','rate_p']][1:32],on='省',how='left')
    d_c_pre[['RR1', 'RR2', 'RR3', 'RR4', 'RR5', 'RR6', 'RR7', 'RR8', 'RR9', 'RR10', 'RR11',
             'RR12']] = d_c_pre[['R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7', 'R8', 'R9', 'R10', 'R11',
                                   'R12']].mul(d_c_pre['rate_p'].values,axis=0)

    # d_c_pre
    
    #全国大类产业产量年内占比情况
    d_c = pd.DataFrame(d_c_pre.drop(d_c_pre.columns[1:15],axis=1).sum())[1:]#.sum()#0.997752
    d_c.rename(columns={0:'China'}, inplace=True)
    d_c.reset_index(inplace=True)
    d_c.drop(['index'],axis=1,inplace=True)
    # d_c

    #combine two sheets
    d_total = pd.concat([d_p.set_index('省').T[:-1].reset_index(),d_c],axis=1)
    d_total.drop(['index'],axis=1,inplace=True)

    # save the data
    d_total.to_csv(name+'各省产量年内占比及全国产量年内占比_2006-2010mean.csv',index=False)
    
    print('rate ok')


# ##### 产业级别数据处理

def calcu_rate_ind(d_w,kind,name):
    #二级产业取水占比计算
    d_i_pre = pd.merge(kind,d_w,on=['省','产业'],how= 'left')
    #采矿业 产业用水权重中涵盖了其他采矿业，但实际产量变化中无其他采矿业这一项（约占总体0.000159
    # d_mi_pre
    d_i_pre[['R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7', 'R8', 'R9', 'R10', 'R11',
             'R12']] = d_i_pre[['01', '02', '03', '04', '05', '06', '07', '08','09', '10', '11', 
                                '12']].mul(d_i_pre[d_i_pre.columns[-1]].values,axis=0)
    # d_i_pre
    d_i = d_i_pre.groupby(['产业']).sum().iloc[:,-12:].T
    #有些产业之和不是1，但都在0.994+，每个省的取水统计量和全国统计量存在差别，按照全国统计量计算
    # d_mi_pre.groupby(['产业']).sum().iloc[:,-13:]
    #工艺品及其他制造业这一行业 总和仅为 0.778703 剩下的需要用全国平均补齐----但本身占全国用水比例不大，仅为0.008494
    ## 本身一共有31个省，但这一行业仅有15个省有数据（产品产量数据）
    
    if name == 'manufacture':
        s_gyp = pd.DataFrame(d_i.T[d_i.T.index.isin(['工艺品及其他制造业'])].sum())#.sum()#0.778703
        s_gyp['工艺品及其他制造业'] = s_gyp[0]/0.778703
        d_i['工艺品及其他制造业'] = s_gyp.iloc[:,1:].values
        #d_i
    else:
        d_i = d_i
        
    #总产业用水取水占比计算
    d_a_pre =  pd.merge(d_i.T,d_w.loc[d_w['省'].isin(['全国'])],on='产业',how='left')
    # d_mm_pre
    d_a_pre[['RR1', 'RR2', 'RR3', 'RR4', 'RR5', 'RR6', 'RR7', 'RR8', 'RR9', 'RR10', 'RR11',
             'RR12']] = d_a_pre[['R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7', 'R8', 'R9', 'R10', 'R11',
                                 'R12']].mul(d_a_pre[d_a_pre.columns[-2]].values,axis=0)
    # d_mm_pre
    d_a = pd.DataFrame(d_a_pre.iloc[:,-12:].sum())#.sum()#0.997752
    d_a.rename(columns={0:'China_'+name}, inplace=True)
    d_a.reset_index(inplace=True)
    d_a.drop(['index'],axis=1,inplace=True)
    # d_mm
    
    #combine two sheets
    d_total = pd.concat([d_i.reset_index(),d_a],axis=1)
    d_total.drop(['index'],axis=1,inplace=True)
    
    # save the data
    d_total.to_csv(name+'产量年内占比及各二级产业全国产量年内占比_2006-2010mean.csv',index=False)
    print('calculate_rate_ind OK')



# ### run code

if __name__=="__main__":
#     d_min = pd.read_excel('采矿业全国各地产量年内变化整理.xlsx')
#     calcu_output_rate_mean(d_min)    
#     d_man = pd.read_excel('制造业全国各地产量年内变化2006_2010_2.xlsx')
#     calcu_output_rate_mean(d_man)   
#     d_ele = pd.read_excel('电热全国各地产量年内变化2006-2010整理.xlsx')
#     calcu_output_rate_mean(d_ele)
#     d_ele= pd.read_csv('全国各省产品产量占比年内变化_5year_mean_电.csv')
#     transfer_output_kind_ele(d_ele,'ele_heat')


if __name__=="__main__":
#     d_min = pd.read_csv('全国各省产品产量占比年内变化_5year_mean_煤.csv')
#     ##计算省内产业平均占比（直接平均不是按照权重）——这里没有加权的原因是不知道各产品实际用水大小和比例
#     # prod_mean['产品'].unique()
#     # ['天然原油', '天然气', '原煤', '原盐', '洗煤', '硫铁矿石（折含硫35%）', '磷矿石（折含五氧化二磷30%）',
#     #  '钨精矿折合量（折三氧化钨６５％）', '钼精矿折合量（折纯钼４５％）', '铁矿石原矿', '铅金属含量', '铜金属含量',
#     #  '锌金属含量', '锑金属含量', '锡金属含量']
#     coal = d_min.loc[d_min['产品'].isin(['原煤', '洗煤'])]
#     oilgas = d_min.loc[d_min['产品'].isin(['天然原油', '天然气'])]
#     blackmetal = d_min.loc[d_min['产品'].isin(['铁矿石原矿'])]
#     colorfulmetal = d_min.loc[d_min['产品'].isin(['铜金属含量', '锌金属含量','铅金属含量', '钼精矿折合量（折纯钼４５％）',
#                                                 '锡金属含量', '钨精矿折合量（折三氧化钨６５％）', '锑金属含量'])]
#     no_metal = d_min.loc[d_min['产品'].isin(['原盐','硫铁矿石（折含硫35%）', '磷矿石（折含五氧化二磷30%）',])]

#     sort_min=[coal,oilgas,blackmetal,colorfulmetal,no_metal]
#     labels_min= ['煤炭开采和洗选业', '石油和天然气开采业', '黑色金属矿采选业', '有色金属矿采选业', '非金属矿采选业']

#     transfer_output_kind(5,sort_min,labels_min,'mining')

if __name__=="__main__":
#     d_man = pd.read_csv('全国各省产品产量占比年内变化_5year_mean_麦.csv')
#     nongfufood =d_man.loc[d_man['产品'].isin(['小麦粉', '大米', '饲料', '精制食用植物油','成品糖','鲜、冷藏肉', '冻肉'])]
#     foodmaking =d_man.loc[d_man['产品'].isin(['糕点','饼干','糖果','速冻米面食品','方便面','乳制品','罐头','味精（谷氨酸钠）',
#                                                                  '酱油','冷冻饮品'])]
#     drinking = d_man.loc[d_man['产品'].isin([  '发酵酒精（折96度,商品量）', '饮料酒', '软饮料', '精制茶'])]
#     yancao = d_man.loc[d_man['产品'].isin(['卷烟'])]
#     fangzhi= d_man.loc[d_man['产品'].isin(['纱','布','印染布','绒线（俗称毛线）','毛机织物（呢绒）','亚麻布（含亚麻≥55%）','帘子布',
#                                                               '无纺布（无纺织物）','蚕丝及交织机织物（含蚕丝≥50%）','苎麻布（含苎麻≥55%）','生丝'])]
#     clothing = d_man.loc[d_man['产品'].isin(['服装', '针织服装', '梭织服装'])]
#     leather = d_man.loc[d_man['产品'].isin([ '轻革', '皮革鞋靴', '皮革服装','天然皮革制手提包（袋）、背包', '天然毛皮服装'])]
#     woodenusing =  d_man.loc[d_man['产品'].isin(['人造板', '人造板表面装饰板', '复合木地板','实木木地板'])]
#     furniture = d_man.loc[d_man['产品'].isin([ '家具'])]
#     papermaking = d_man.loc[d_man['产品'].isin([ '纸浆（原生浆及废纸浆）', '机制纸及纸板（外购原纸加工除外）', '纸制品'])]
#     yinshuaye = d_man.loc[d_man['产品'].isin([ '本册'])]
#     wenjiaotiyu  = d_man.loc[d_man['产品'].isin([ '木杆铅笔','圆珠笔'])]
#     oilmaking = d_man.loc[d_man['产品'].isin([ '原油加工量','汽油', '煤油', '柴油', '润滑油', '燃料油', '液化石油气', '石油沥青', '焦炭'])]
#     chemicalyuan = d_man.loc[d_man['产品'].isin(['硫酸（折100％）','盐酸（氯化氢,含量31%）', '烧碱（折100％）', '乙烯', '纯苯','合成橡胶',
#                                                '农用氮、磷、钾化学肥料总计（折纯）','磷酸铵肥（实物量）', '化学农药原药（折有效成分100％）', 
#                                                 '涂料', '油墨', '颜料', '染料','初级形态的塑料', '其中:聚乙烯树酯', '聚丙烯树脂', '精甲醇',
#                                                 '聚氯乙烯树脂','合成纤维单体','合成纤维聚合物','肥（香）皂','合成洗涤剂', '冰乙酸（冰醋酸）',
#                                                 '牙膏（折65克标准支）', '香精','纯碱（碳酸钠）', '碳化钙（电石,折300升／千克）', 
#                                                 '浓硝酸（折100%）','合成氨（无水氨）', '火柴（折50支标准盒）'])]
#     medicine = d_man.loc[d_man['产品'].isin([ '化学药品原药', '中成药'])]
#     # 
#     huauxuexianwei = d_man.loc[d_man['产品'].isin([ '化学纤维用浆粕','化学纤维', '合成纤维'])]
#     xiangjiaozhipin = d_man.loc[d_man['产品'].isin([ '橡胶轮胎外胎', '胶鞋类'])]
#     plasticmaking = d_man.loc[d_man['产品'].isin([ '塑料制品'])]
#     feijinshukuangwu = d_man.loc[d_man['产品'].isin(['水泥熟料', '水泥', '商品混凝土','水泥混凝土排水管', '水泥混凝土压力管', '预应力混凝土桩', 
#                                                      '石膏板', '砖', '瓦', '瓷质砖', '细炻砖','炻质砖','天然大理石建筑板材', '天然花岗石建筑板材', 
#                                                      '平板玻璃', '钢化玻璃', '夹层玻璃', '中空玻璃', '日用玻璃制品','玻璃保温容器', '玻璃纤维纱', 
#                                                      '卫生陶瓷制品', '耐火材料制品', '石墨及炭素制品','水泥混凝土电杆', '日用陶瓷制品','陶质砖',
#                                                      '炻瓷砖'])]
#     blackmetalyelian = d_man.loc[d_man['产品'].isin([ '生铁', '粗钢', '钢材','用外购国产钢材再加工生产的钢', '铁合金'])]
#     yousemetalyelian = d_man.loc[d_man['产品'].isin(['十种有色金属', '精炼铜（电解铜）', '锡','锌','原铝（电解铝）', '镁', '海绵钛', '黄金',
#                                                      '白银（银锭）','铝合金', '铜材', '铝材','铅', '氧化铝', '镍','锑品'])]
#     metalzhiping = d_man.loc[d_man['产品'].isin([ '金属切削工具', '钢绞线', '锁具', '搪瓷制品', '不锈钢日用制品','金属集装箱'])]
#     tongyongshebei =  d_man.loc[d_man['产品'].isin(['电站锅炉', '工业锅炉', '电站用汽轮机', '电站水轮机','金属切削机床', '金属成形机床', 
#                                                     '铸造机械', '电焊机', '起重机','电动车辆（电动叉车）', '内燃叉车', '泵', '气体压缩机', '阀门',
#                                                     '液压元件', '气动元件', '滚动轴承','工业电炉', '风机', '气体分离及液化设备','电动手提式工具', 
#                                                     '包装专用设备', '减速机', '粉末冶金零件', '燃气轮机'])]
#     specialshebei = d_man.loc[d_man['产品'].isin(['采矿专用设备', '挖掘、铲土运输机械', '压实机械', '水泥专用设备', '混凝土机械',
#                                                   '金属冶炼设备','金属轧制设备', '塑料加工专用设备', '模具', '粮食加工机械', '饲料生产专用设备',
#                                                   '印刷专用设备', '缝纫机','农作物收获机械', '环境污染防治专用设备', '中型拖拉机', '小型拖拉机',
#                                                   '棉花加工机械','大型拖拉机', '场上作业机械'])]
#     jiaotongyunshu = d_man.loc[d_man['产品'].isin([ '铁路机车', '铁路货车','汽车', '改装汽车', '两轮脚踏自行车', '铁路客车','摩托车整车',
#                                                     '民用钢质船舶'])]
#     dianqijixie = d_man.loc[d_man['产品'].isin(['发电机组（发电设备）', '交流电动机', '变压器', '高压开关板', '低压开关板','通信及电子网络用电缆',
#                                                 '电力电缆', '光缆', '绝缘制品', '铅酸蓄电池', '碱性蓄电池', '锂离子电池','原电池及原电池组（折R20标准只）',
#                                                 '家用电冰箱', '商用冷藏展示柜', '家用电热烘烤器具','家用洗衣机','家用燃气灶具','微波炉', 
#                                                 '家用电热水器','家用吸尘器','家用燃气热水器','电光源','灯具及照明装置','家用冷柜（家用冷冻箱）',
#                                                 '房间空气调节器','家用吸排油烟机','电饭锅','家用电风扇' ])]
#     communication = d_man.loc[d_man['产品'].isin([ '微波终端机', '程控交换机', '其中:数字程控交换机', '电话单机','移动通信基站设备', 
#                                                    '移动通信手持机（手机）', '电子计算机整机', '显示器', '打印机', '彩色显像管','半导体分立器件',
#                                                    '集成电路', '集成电路圆片', '彩色电视机', '组合音响','传真机', '数字激光音、视盘机'])]
#     yiqiyibiao = d_man.loc[d_man['产品'].isin(['工业自动调节仪表与控制系统', '电工仪器仪表','分析仪器及装置','试验机','照相机',
#                                                '环境监测专用仪器仪表','汽车仪器仪表','表','光学仪器', '眼镜成镜', '复印和胶版印制设备'])]
#     umberlla = d_man.loc[d_man['产品'].isin(['伞类制品'])]
#     # 29
#     sort_man=[nongfufood,foodmaking,drinking,yancao,fangzhi,clothing,leather,woodenusing,furniture,papermaking ,yinshuaye,#11
#               wenjiaotiyu,oilmaking,chemicalyuan,medicine,huauxuexianwei,xiangjiaozhipin,plasticmaking,feijinshukuangwu,blackmetalyelian,#9
#               yousemetalyelian,metalzhiping,tongyongshebei,specialshebei,jiaotongyunshu,dianqijixie,communication,yiqiyibiao,umberlla]#9

#     labels_man= ['农副食品加工业', '食品制造业', '饮料制造业', '烟草制品业', '纺织业工业', '纺织服装鞋帽制造业',
#                  '皮革毛皮羽毛(绒)及其制品业', '木材加工及木竹藤棕草制品业', '家具制造业', '造纸及纸制品业',#10
#                  '印刷业和记录媒介的复制业', '文教体育用品制造业', '石油加工炼焦及核燃料加工业', '化学原料及化学制品制造业',
#                  '医药制造业', '化学纤维制造业', '橡胶制品业', '塑料制品业', '非金属矿物制品业', '黑色金属冶炼及压延加工业',#10
#                  '有色金属冶炼及压延加工业', '金属制品业', '通用设备制造业', '专用设备制造业', '交通运输设备制造业',
#                  '电气机械及器材制造业', '通信设备计算机及其他电子设备制造业', '仪器仪表及文化办公用机械制造业', '工艺品及其他制造业']#9

#     transfer_output_kind(29,sort_man,labels_man,'manufacture')


if __name__=="__main__":
#     d_cw = pd.read_excel('../工业企业用水效率/raw_data/用水情况/规模以上采矿业工业用水情况2008.xlsx')
#     d_zw =pd.read_excel('../工业企业用水效率/raw_data/用水情况/规模以上制造业工业用水情况2008.xls')
#     d_ew =pd.read_excel('../工业企业用水效率/raw_data/用水情况/规模以上电力、燃气工业用水情况2008.xlsx')
#     calcul_weighted_factor_pro(d_cw,'mining',192)
#     calcul_weighted_factor_pro(d_zw,'manufacture',992)
#     calcul_weighted_factor_pro(d_ew,'ele_heat',96,3774105.0)


if __name__=="__main__":
#     d_cw = pd.read_excel('../工业企业用水效率/raw_data/用水情况/规模以上采矿业工业用水情况2008.xlsx')
#     d_zw =pd.read_excel('../工业企业用水效率/raw_data/用水情况/规模以上制造业工业用水情况2008.xls')
#     d_ew =pd.read_excel('../工业企业用水效率/raw_data/用水情况/规模以上电力、燃气工业用水情况2008.xlsx')
#     calcul_weighted_factor_subindustry(d_cw,'mining')
#     calcul_weighted_factor_subindustry(d_zw,'manufacture')
#     calcul_weighted_factor_subindustry(d_ew,'ele_heat')


if __name__=="__main__":
#     d_cw_p = pd.read_csv('规模以上mining用水各产业占全省的权重&各省占全国权重前32_2008.csv')
#     kind_c = pd.read_csv('全国各省产业产量占比年内变化_5year_mean_mining.csv')
#     #统一格式#可以之后看看有没有必要
#     replacement_province(d_cw_p)
#     d_cw_p.rename(columns={'地区':'省'},inplace=True)
#     d_cw_p
#     kind_c
#     #两个表格的产业类型一致、地区名称一致
#     calcul_rate_pro(d_cw_p,kind_c,'mining')

if __name__=="__main__":
#     d_zw_p = pd.read_csv('规模以上manufacture用水各产业占全省的权重&各省占全国权重前32_2008.csv')
#     kind_z = pd.read_csv('全国各省产业产量占比年内变化_5year_mean_manufacture.csv')

#     replacement_province(d_zw_p)
#     d_zw_p.rename(columns={'地区':'省'},inplace=True)
#     # d_zw_p
#     # kind_z
#     # 两者的省名称一致，产业类型基本一致，但是取水量多一部分废弃资源和废旧材料回收加工业---取水量极小
#     # (共有6个空值，max=0.00424，75%=0.001035，mean=0.000786,中值=0.000579，全国占比0.000732)
#     calcul_rate_pro(d_zw_p,kind_z,'manufacture')

if __name__=="__main__":
    # d_ew_p = pd.read_csv('规模以上ele_heat用水各产业占全省的权重&各省占全国权重前32_2008.csv')
    # replacement_province(d_ew_p)
    # d_ew_p.rename(columns={'地区':'省'},inplace=True)
    # replacement_water(d_ew_p)
    # d_ew_p

    # kind_e = pd.read_csv('全国各省产业产量占比年内变化_5year_mean_ele_heat.csv')
    # kind_e
    #calcul_rate_pro(d_ew_p,kind_e,'ele_heat')###运行时要把源代码中[2:19]换为[2:18]


if __name__=="__main__":
#     kind_c = pd.read_csv('全国各省产业产量占比年内变化_5year_mean_mining.csv')
#     d_cw_i = pd.read_csv('全国规模以上各产业工业用水占mining的权重&各省占全国权重_2008.csv')
#     replacement_province(d_cw_i)
#     d_cw_i.rename(columns={'地区':'省'},inplace=True)
#     calcu_rate_ind(d_cw_i,kind_c,'mining')

if __name__=="__main__":
#     d_zw_i = pd.read_csv('全国规模以上各产业工业用水占manufacture的权重&各省占全国权重_2008.csv')
#     kind_z = pd.read_csv('全国各省产业产量占比年内变化_5year_mean_manufacture.csv')

#     replacement_province(d_zw_i)
#     d_zw_i.rename(columns={'地区':'省'},inplace=True)
#     calcu_rate_ind(d_zw_i,kind_z,'manufacture')

if __name__=="__main__":
#     d_ew_i = pd.read_csv('全国规模以上各产业工业用水占ele_heat的权重&各省占全国权重_2008.csv')
#     replacement_province(d_ew_i)
#     d_ew_i.rename(columns={'地区':'省'},inplace=True)
#     replacement_water(d_ew_i)
#     kind_e = pd.read_csv('全国各省产业产量占比年内变化_5year_mean_ele_heat.csv')
#     replacement_kind(kind_e)
#     calcu_rate_ind(d_ew_i[:64],kind_e,'ele_heat')

