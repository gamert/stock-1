# https://zhuanlan.zhihu.com/p/59867869
# 如何利用欧奈尔的RPS寻找强势股？
# RPS英文全称Relative Price Strength Rating，即股价相对强度，该指标是欧奈尔CANSLIM选股法则中的趋势分析，具有很强的实战指导意义。
# RPS指标是指在一段时间内，个股涨幅在全部股票涨幅排名中的位次值。
# 比如A股共有3500只股票，若某只股票的120日涨幅在所有股票中排名第350位，则该股票的RPS值为：(1-350/3500)*100=90。
# RPS的值代表该股的120日涨幅超过其他90%的股票的涨幅。通过该指标可以反映个股股价走势在同期市场中的表现相对强弱。
# RPS的值介于0-100之间，在过去的一年中，所有股票的涨幅排行中，前1%的股票的RPS值为99至100，前2%的股票的RPS值为98至99，
# 以此类推。RPS时间周期可以自己根据需要进行调整，常用的有60日（3个月）、120日（半年）和250日（一年）等。

# 先引入后面可能用到的library
import pandas as pd
import tushare as ts
import matplotlib.pyplot as plt
# %matplotlib inline

# 正常显示画图时出现的中文和负号
from pylab import mpl

mpl.rcParams['font.sans-serif'] = ['SimHei']
mpl.rcParams['axes.unicode_minus'] = False

# 使用之前先输入token，可以从个人主页上复制出来，
# 每次调用数据需要先运行该命令
token = '1a5a1c37219acda3a569e8b809bd86b06ebc7c34d8dee170ef5ad5d1'
ts.set_token(token)
pro = ts.pro_api()

df = pro.stock_basic(exchange='', list_status='L',
                     fields='ts_code,symbol,name,area,industry,list_date')
print(len(df))
# 输出结果：3594


# 排除掉新股次新股，这里是只考虑2017年1月1日以前上市的股票
# 20000101 : 834
# 19960101 : 272
# 19930101 : 47
# 19920101 : 11
df = df[df['list_date'].apply(int).values < 19930101]
print(len(df))
# 输出结果：3024

# 获取当前所有非新股次新股代码和名称
codes = df.ts_code.values
names = df.name.values
# 构建一个字典方便调用
code_name = dict(zip(names, codes))


# 使用tushare获取上述股票周价格数据并转换为周收益率
# 设定默认起始日期为2018年1月5日，结束日期为2019年3月19日
# 日期可以根据需要自己改动
def get_data(code, start='20100101', end='20190319'):
    df = pro.daily(ts_code=code, start_date=start, end_date=end, fields='trade_date,close')
    # 将交易日期设置为索引值
    df.index = pd.to_datetime(df.trade_date)
    df = df.sort_index()
    # 计算收益率
    return df.close


# 通过定义的函数获取上述3024只股票自2018年1月5日以来的所有日交易数据，并计算每只股票120日滚动收益率。

# 构建一个空的dataframe用来装数据
data = pd.DataFrame()
for name, code in code_name.items():
    data[name] = get_data(code)


# data.to_csv('daily_data.csv',encoding='gbk')
# data=pd.read_csv('stock_data.csv',encoding='gbk',index_col='trade_date')
# data.index=(pd.to_datetime(data.index)).strftime('%Y%m%d')

# 计算收益率
def cal_ret(df, w=5):
    '''w:周5;月20;半年：120; 一年250
    '''
    df = df / df.shift(w) - 1
    return df.iloc[w:, :].fillna(0)


# 经过这一轮的大幅上涨，截至2019年3月19日，上述3024只股票中，有49只股票120日收益率超过100%，占比1.68%；收益率在20%-100%之间的股票有1280只，占比达到43.99%；仍有360只股票120日收益率为负数。


ret120 = cal_ret(data, w=120)


# 计算RPS
def get_RPS(ser):
    df = pd.DataFrame(ser.sort_values(ascending=False))
    df['n'] = range(1, len(df) + 1)
    df['rps'] = (1 - df['n'] / len(df)) * 100
    return df


# 计算每个交易日所有股票滚动w日的RPS
def all_RPS(data):
    dates = (data.index).strftime('%Y%m%d')
    RPS = {}
    for i in range(len(data)):
        RPS[dates[i]] = pd.DataFrame(get_RPS(data.iloc[i]).values, columns=['收益率', '排名', 'RPS'],
                                     index=get_RPS(data.iloc[i]).index)
    return RPS


rps120 = all_RPS(ret120)


# 获取所有股票在某个期间的RPS值
def all_data(rps, ret):
    df = pd.DataFrame(pd.np.NaN, columns=ret.columns, index=ret.index)
    for date in ret.index:
        date = date.strftime('%Y%m%d')
        d = rps[date]
        for c in d.index:
            df.loc[date, c] = d.loc[c, 'RPS']
    return df


# 构建一个以前面收益率为基础的空表
df_new = pd.DataFrame(pd.np.NaN, columns=ret120.columns, index=ret120.index)

# 计算所有股票在每一个交易日的向前120日滚动RPS值。对股票价格走势和RPS进行可视化。

for date in df_new.index:
    date = date.strftime('%Y%m%d')
    d = rps120[date]
    for c in d.index:
        df_new.loc[date, c] = d.loc[c, 'RPS']


def plot_rps(stock):
    plt.subplot(211)
    data[stock][120:].plot(figsize=(16, 16), color='r')
    plt.title(stock + '股价走势', fontsize=15)
    plt.yticks(fontsize=12)
    plt.xticks([])
    ax = plt.gca()
    ax.spines['right'].set_color('none')
    ax.spines['top'].set_color('none')
    plt.subplot(212)
    df_new[stock].plot(figsize=(16, 8), color='b')
    plt.title(stock + 'RPS相对强度', fontsize=15)
    my_ticks = pd.date_range('2018-06-9', '2019-3-31', freq='m')
    plt.xticks(my_ticks, fontsize=12)
    plt.yticks(fontsize=12)
    ax = plt.gca()
    ax.spines['right'].set_color('none')
    ax.spines['top'].set_color('none')
    plt.show()


# 查看2018年7月31日-2019年3月19日每月RPS情况。下面仅列出每个月RPS排名前十的股票，里面出现不少熟悉的“妖股”身影。
dates = ['20180731', '20180831', '20180928', '20181031', '20181130', '20181228', '20190131', '20190228', '20190319']
df_rps = pd.DataFrame()
for date in dates:
    df_rps[date] = rps120[date].index[:50]

plot_rps('东方通信')
plot_rps('华业资本')
plot_rps('顺鑫农业')

# 欧奈尔研究了1953年至1993年，500只年度涨幅最大的股票，发现每年涨幅居前的，在他们股价真正大幅度攀升之前，其平均的相对强弱指标RPS为87％。
# 这并不意味着，只要RPS>87%就可以买入该股票呢？其实RPS指标只是对强势股的个一个初步筛选，对于A股而言，RPS大于87%的股票就有400多只，
# 都买进也不太现实，具体运用还需结合个股基本面、题材和整体市场情况分析。RPS实际上是欧奈尔在《笑傲股市》中提出的CANSLIM七步选股法的一个技术分析。
# 各字母含义如下所示：
#
# C：最近一季度报表显示的盈利（每股收益）
#
# A：每年度每股盈利的增长幅度
#
# N：新产品，新服务，股价创新高
#
# S：该股流通盘大小，市值以及交易量的情况
#
# L：该股票在行业中的低位，是否为龙头
#
# I：该股票有无有实力的庄家，机构大流通股东
#
# M：大盘走势如何，如何判断大盘走向
#
# RPS可以帮助选出创出新高的股票。牛股一定创新高，但是新高不一定是牛股。所以关键是将RPS结合基本面进一步选择，基本面情况好，
# 销售额和盈利增长很快，且这种增长是由公司推出的新产品或新服务带来的。本文主要分享了欧奈尔RPS指标的原理和Python计算方法，受篇幅所限，
# 文中只给出了核心代码，如需完整代码可通过加入知识星球，向博主索要。文中提及股票不构成任何投资建议，投资有风险，入市需谨慎！
