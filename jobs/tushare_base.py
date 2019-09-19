import pandas as pd
import tushare as ts
import matplotlib.pyplot as plt
# %matplotlib inline

# 正常显示画图时出现的中文和负号
from pylab import mpl

import datetime

mpl.rcParams['font.sans-serif'] = ['SimHei']
mpl.rcParams['axes.unicode_minus'] = False

# 使用之前先输入token，可以从个人主页上复制出来，
# 每次调用数据需要先运行该命令
token = '1a5a1c37219acda3a569e8b809bd86b06ebc7c34d8dee170ef5ad5d1'
ts.set_token(token)
pro = ts.pro_api()

class tushare_base:
    def __init__(self):
        df = pro.stock_basic(exchange='', list_status='L',
                             fields='ts_code,symbol,name,area,industry,list_date')
        print(len(df))
        # 输出结果：3594

        # 排除掉新股次新股，这里是只考虑2017年1月1日以前上市的股票
        # 20170101 : 834
        # 20000101 : 834
        # 19960101 : 272
        # 19930101 : 47
        # 19920101 : 11
        df = df[df['list_date'].apply(int).values < 20170101]
        print(len(df))
        # 输出结果：3024

        # 获取当前所有非新股次新股代码和名称
        codes = df.ts_code.values
        names = df.name.values
        # 构建一个字典方便调用
        self.code_name = dict(zip(names, codes))

    def fill_datas(self):
        # 使用tushare获取上述股票周价格数据并转换为周收益率
        # 设定默认起始日期为2018年1月5日，结束日期为2019年3月19日
        # 日期可以根据需要自己改动
        def get_data(code, start='20150101', end='20190319'):
            df = pro.daily(ts_code=code, start_date=start, end_date=end, fields='trade_date,close')
            # 将交易日期设置为索引值
            df.index = pd.to_datetime(df.trade_date)
            df = df.sort_index()
            # 计算收益率
            return df.close

        # 通过定义的函数获取上述3024只股票自2018年1月5日以来的所有日交易数据，并计算每只股票120日滚动收益率。
        # 构建一个空的dataframe用来装数据
        self.data = pd.DataFrame()
        for name, code in self.code_name.items():
            self.data[name] = get_data(code)



