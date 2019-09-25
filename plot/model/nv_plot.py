import pandas as pd
import numpy as np
from pyecharts import options as opts
from pyecharts.charts import Kline, Line, Bar, Grid, Page,Scatter

nv = pd.read_csv('nv_all1.csv',index_col=0) #读取因子值全样本文件
nnv = pd.read_csv('nv_all1.csv',index_col=0).loc['2019-09-10 10:00':]   #选取最近两周因子值
kdata = pd.read_csv('kdata1.csv',index_col=0)   #读取股票价格数据


#将最近两周的因子数据归一化
for i in range(0,len(nnv.columns),2):
    for j in range(1,len(nnv.index)):
        nnv.iloc[j,i] = nnv.iloc[j,i]/nnv.iloc[0,i]
for i in range(0,len(nnv.columns),2):
    nnv.iloc[0,i] = 1


#将5分钟股票数据转化为30分钟股票数据（保留全样本）
kdata_all = []
for i in range(5,len(kdata),6):
    kdata_all.append(kdata.iloc[i,:])
kdata_all = pd.DataFrame(kdata_all)['close'].loc['2018/1/11 10:00':].reset_index(drop = True)   #要保证股票数据行数与因子值数据行数相同

#将5分钟股票数据转化为30分钟股票数据（保留最近两周）
kdata_part = []
for i in range(5,len(kdata),6):
    kdata_part.append(kdata.iloc[i,:])
kdata_part = pd.DataFrame(kdata_part)['close'].loc['2019/9/10 10:00':].reset_index(drop=True)


#全样本及最新股票数据归一化
for j in range(1,len(kdata_part.index)):
        kdata_part.iloc[j] = kdata_part.iloc[j]/kdata_part.iloc[0]
kdata_part.iloc[0] = 1
for j in range(1,len(kdata_all.index)):
        kdata_all.iloc[j] = kdata_all.iloc[j]/kdata_all.iloc[0]
kdata_all.iloc[0] = 1


#将因子值文件中对各因子打分列提取出来，方便后面在收盘价上根据打分画不同颜色点
new_p = pd.DataFrame()  #最新数据
n1=[]
for i in range(1,len(nnv.columns),2):
    n1.append(nnv.columns[i])
new_p = nnv[n1]
new_p['close'] = kdata_part.values

new_a = pd.DataFrame()  #全样本
n=[]
for i in range(1,len(nv.columns),2):
    n.append(nv.columns[i])
new_a = nv[n]
new_a['close'] = kdata_all.values

#因子值、收盘价及因子打分叠加
def getplot(factor,factor2,klinedata,file,new,instrument,xaxis_index=None):
    line = (
        Line()
            .add_xaxis(list(file.index))
            .add_yaxis(factor,list(file[factor]),label_opts=opts.LabelOpts(is_show=False)) #叠放因子值
            .add_yaxis(instrument,list(klinedata),label_opts=opts.LabelOpts(is_show=False),is_symbol_show=False)#叠放股票收盘价
            .set_global_opts(yaxis_opts=opts.AxisOpts(is_scale=True))
            .set_global_opts(
            datazoom_opts=opts.DataZoomOpts(is_show=False,range_start=0,range_end=100,type_='inside',xaxis_index=xaxis_index),
            legend_opts=opts.LegendOpts(is_show=True, pos_top=10, pos_left='left')))

    scatter = (#根据打分不同拆分画点
        Scatter()
            .add_xaxis(list(file.index[file.index.isin(new[new[factor2]==-1].index)]))
            .add_yaxis("sell(score=-1)",list(new[new[factor2]== -1]['close']),label_opts=opts.LabelOpts(is_show=False),symbol_size=5)
            .add_xaxis(list(file.index[file.index.isin(new[new[factor2] == 1].index)]))
            .add_yaxis("buy(score=1)", list(new[new[factor2] == 1]['close']), label_opts=opts.LabelOpts(is_show=False),symbol_size=5)
    )
    line.overlap(scatter) #叠放因子打分
    return line

def grid(factor,factor2,instrument):
    gridchart = Grid(
        init_opts=opts.InitOpts(
        width="100vw",
        height="50vh",
        animation_opts=opts.AnimationOpts(animation=True)
    ))
    gridchart.add( #左边画最新数据
            getplot(factor,factor2,kdata_part,nnv,new_p,instrument,xaxis_index=[0,1]),
            grid_opts=opts.GridOpts(pos_left="5%",pos_right="68%")

    )
    gridchart.add(  # 右边画全样本数据
        getplot(factor, factor2,kdata_all, nv, new_a,instrument, xaxis_index=None),
        grid_opts=opts.GridOpts(pos_left="40%", pos_right="5%")
    )

    return gridchart
# print(new_p.columns[2])
page1 = Page(layout=Page.SimplePageLayout)
for i in range(len(new_a.columns)-1):
    page1.add(grid(nv.columns[2*i],new_a.columns[i],str(kdata['symbol'][0][-6:])))
page1.render('renkoMA_NV.html')