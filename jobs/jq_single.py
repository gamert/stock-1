'''-------api调用聚宽-----'''
# 导入函数库
from jqdata import *
import datetime
import numpy as np
import pandas as pd

# 模型选择
from sklearn.model_selection import train_test_split, cross_val_score

# 数据处理
from sklearn.preprocessing import StandardScaler
# from sklearn.preprocessing import KBinsDiscretizer
# 填充缺失值
# from sklearn.impute import SimpleImputer

# 特征选择
from sklearn.feature_selection import SelectKBest, chi2, f_regression, SelectPercentile, RFE, SelectFromModel
from scipy.stats import pearsonr

# 模型
from sklearn.svm import SVR
from sklearn.linear_model import LinearRegression, Ridge, Lasso, RandomizedLasso, LogisticRegression
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier

# 调参
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import learning_curve

# 模型评估
from sklearn.metrics import silhouette_score, silhouette_samples, r2_score, roc_auc_score


# 初始化函数，设定基准等等
def initialize(context):
    # 设定沪深300作为基准
    g.security = list(get_all_securities(types=["stock"]).index)

    set_benchmark('000300.XSHG')
    # 开启动态复权模式(真实价格)
    set_option('use_real_price', True)
    # 输出内容到日志 log.info()
    # 过滤掉order系列API产生的比error级别低的log
    # log.set_level('order', 'error')

    ### 股票相关设定 ###
    # 股票类每笔交易时的手续费是：买入时佣金万分之三，卖出时佣金万分之三加千分之一印花税, 每笔交易佣金最低扣5块钱
    set_order_cost(OrderCost(close_tax=0.001, open_commission=0.0003, close_commission=0.0003, min_commission=5),
                   type='stock')
    # 设置滑点
    set_slippage(PriceRelatedSlippage(0.002))
    # 开盘前运行
    run_daily(before_market_open, time='before_open', reference_security='000300.XSHG')
    # 开盘时运行
    run_daily(market_open, time='open', reference_security='000300.XSHG')
    # 收盘后运行
    run_daily(after_market_close, time='after_close', reference_security='000300.XSHG')
    # 检测因子
    g.factor = valuation.market_cap
    # 分类数
    g.class_num = 10
    g.day = 0
    # 时间窗口
    g.rate = 22
    g.stock_class_list = {}
    g.stock_class_close = {}
    g.stock_class_return = {}
    # 收益率
    for i in range(g.class_num):
        g.stock_class_return["class%d" % (i)] = 1
    # 超额收益率
    g.stock_class_excess_return = {}
    for i in range(g.class_num):
        g.stock_class_excess_return["class%d" % (i)] = 1
    # 窗口胜率
    g.stock_class_win_return = {}
    for i in range(g.class_num):
        g.stock_class_win_return["class%d" % (i)] = 0

    g.benchmark_start = None
    g.benchmark_open = None


## 开盘前运行函数
def before_market_open(context):
    # 输出运行时间
    # log.info('函数运行时间(before_market_open)：'+str(context.current_dt.time()))
    log.info('##############################################################')


## 开盘时运行函数
def market_open(context):
    if not g.benchmark_start:
        g.benchmark_start = \
        get_price('000300.XSHG', start_date=context.current_dt, end_date=context.current_dt, frequency='daily',
                  fields="close", skip_paused=False, fq='pre').ix[0, "close"]

    if g.day % g.rate == 0:
        # step1:计算不同种类的当前时间窗口下的平均收益率
        if g.stock_class_list:
            benchmark_new = \
            get_price('000300.XSHG', start_date=context.current_dt, end_date=context.current_dt, frequency='daily',
                      fields="close", skip_paused=False, fq='pre').ix[0, "close"]

            for i in range(g.class_num):
                new_stock_class_close = get_price(g.stock_class_list["class%d" % (i)], start_date=context.current_dt,
                                                  end_date=context.current_dt, frequency='daily', fields="close",
                                                  skip_paused=False, fq='pre')["close"].T.ix[:, 0].values
                df = pd.DataFrame({"L": g.stock_class_close["class%d" % (i)], "N": new_stock_class_close})
                df["R"] = (df["N"] - df["L"]) / df["L"]

                g.stock_class_return["class%d" % (i)] = g.stock_class_return["class%d" % (i)] * (
                            1 + df["R"].sum() / len(df["R"]))
                g.stock_class_excess_return["class%d" % (i)] = g.stock_class_return["class%d" % (i)] - (
                            (benchmark_new - g.benchmark_start) / g.benchmark_start)
                g.stock_class_win_return["class%d" % (i)] = df["R"].sum() / len(df["R"]) - (
                            (benchmark_new - g.benchmark_open) / g.benchmark_open)

        # step2:画出每个组别的收益率曲线
        record(class0=g.stock_class_win_return["class0"])
        # record(class1=g.stock_class_win_return["class1"])
        # record(class2=g.stock_class_win_return["class2"])
        # record(class3=g.stock_class_win_return["class3"])
        # record(class4=g.stock_class_win_return["class4"])
        # record(class5=g.stock_class_win_return["class5"])
        # record(class6=g.stock_class_win_return["class6"])
        # record(class7=g.stock_class_win_return["class7"])
        # record(class8=g.stock_class_win_return["class8"])
        record(class9=g.stock_class_win_return["class9"])

        # step3:将股票分类并且保存每个类别下个时间窗口起始收盘价数据
        setclose(context, g.factor, g.class_num, sort="desc", moveNeg=True, moveNan=True)
        # Momentum_factor(context,g.class_num,countNum=66,ascending_bol=False)
        g.benchmark_open = \
        get_price('000300.XSHG', start_date=context.current_dt, end_date=context.current_dt, frequency='daily',
                  fields="close", skip_paused=False, fq='pre').ix[0, "close"]
    g.day += 1


## 收盘后运行函数
def after_market_close(context):
    # log.info(str('函数运行时间(after_market_close):'+str(context.current_dt.time())))
    # #得到当天所有成交记录
    # trades = get_trades()
    # for _trade in trades.values():
    #     log.info('成交记录：'+str(_trade))
    # log.info('一天结束')
    log.info('##############################################################')


# 通过加减获取交易日
def getsecurities(datatime, num):
    # 交易日列表
    trade_days = map(lambda x: x.strftime("%Y-%m-%d"), get_all_trade_days())
    index = trade_days.index(datatime)
    return trade_days[index + num]


# 特征排序
def feat_sort(l1, l2, reverse_bol=True):
    coef_zip = zip(l1, l2)
    return sorted(coef_zip, key=lambda x: abs(x[1]), reverse=reverse_bol)


def setclose(context, factor, classNum, sort="desc", moveNeg=True, moveNan=True):
    q = 0
    if sort == "desc":
        q = query(
            valuation.code
            , factor
        ).filter(
            valuation.code.in_(g.security)
        ).order_by(
            # 按市值降序排列
            factor.desc()
        )
    else:
        q = query(
            valuation.code
            , factor
        ).filter(
            valuation.code.in_(g.security)
        ).order_by(
            # 按市值升序排列
            factor
        )
    df = get_fundamentals(q)
    if moveNeg:
        df = df[df.iloc[:, 1] > 0]
    if moveNan:
        df = df[~np.isnan(df.iloc[:, 1])]
    list_index = map(lambda x: int(x), np.linspace(0, df.shape[0], classNum + 1))
    for i in range(classNum):
        class_list = df.iloc[list_index[i]:list_index[i + 1], :].code.values.tolist()
        g.stock_class_list["class%d" % (i)] = class_list
        g.stock_class_close["class%d" % (i)] = \
        get_price(class_list, start_date=context.current_dt, end_date=context.current_dt, frequency='daily',
                  fields="close", skip_paused=False, fq='pre')["close"].T.ix[:, 0].values


# 动量
def Momentum_factor(context, classNum, countNum=22, ascending_bol=True):
    df = get_price(g.security, count=countNum, end_date=context.current_dt, frequency='daily', fields="close",
                   skip_paused=False, fq='pre')["close"].T
    df["return"] = (df.iloc[:, -1] - df.iloc[:, 0]) / df.iloc[:, 0]
    df = df.sort("return", ascending=ascending_bol)
    df = df[~np.isnan(df["return"])]
    list_index = map(lambda x: int(x), np.linspace(0, df.shape[0], classNum + 1))
    for i in range(classNum):
        class_list = df.iloc[list_index[i]:list_index[i + 1], :].index.values.tolist()
        g.stock_class_list["class%d" % (i)] = class_list
        g.stock_class_close["class%d" % (i)] = df.ix[class_list, -2].values


