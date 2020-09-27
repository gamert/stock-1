from jqdatasdk import *
auth('13761609001', 'zhizhi')
# 查询是否连接成功
is_auth = is_auth()
print(is_auth)

#type: 类型 : stock(股票)，index(指数)，etf(ETF基金)，fja（分级A），fjb（分级B），fjm（分级母基金），mmf（场内交易的货币基金）open_fund（开放式基金）, bond_fund（债券基金）, stock_fund（股票型基金）, QDII_fund（QDII 基金）, money_market_fund（场外交易的货币基金）, mixture_fund（混合型基金）, options(期权)
# res = get_all_securities(types=['futures'], date=None)
# res.to_excel('futures'+".xlsx")
# print(res)

code = 'IC8888.CCFX'
res = get_price(code, start_date='2015-01-01', end_date='2020-08-22 23:00:00').dropna()
res.to_excel(code+".xlsx")
print(res)

code = 'IC9999.CCFX'
res = get_price(code, start_date='2015-01-01', end_date='2020-08-22 23:00:00').dropna()
res.to_excel(code+".xlsx")
print(res)

# code = 'IC2003.CCFX'
# res = get_price(code, start_date='2015-01-01', end_date='2020-08-21 23:00:00').dropna()
# res.to_excel(code+".xlsx")
# print(res)
#
# code  = 'IC2006.CCFX'
# res = get_price(code, start_date='2015-01-01', end_date='2020-08-21 23:00:00').dropna()
# res.to_excel(code+".xlsx")
# print(res)
#
# code  = 'IC2009.CCFX'
# res = get_price(code, start_date='2015-01-01', end_date='2020-08-21 23:00:00').dropna()
# res.to_excel(code+".xlsx")
# print(res)
# # res  = get_security_info(code)
# # print(res)
#
# code  = 'IC2012.CCFX'
# res = get_price(code, start_date='2015-01-01', end_date='2020-08-21 23:00:00').dropna()
# res.to_excel(code+".xlsx")
# print(res)

# futures = 'IC1505.CCFX'
# h = attribute_history(futures, 5, '1d', ('open','close','volume')) # 取得IC1505过去5天的每天的开盘价, 收盘价, 交易量,
#
# print(h)


# 将所有股票列表转换成数组
# stocks = list(get_all_securities(['stock']).index)
#
# # 获得所有指数列表
# get_all_securities(['index'])
#
# # 获得所有基金列表
# df = get_all_securities(['fund'])
#
# # 获取所有期货列表
# get_all_securities(['futures'])
#
# # 获得etf基金列表
# df = get_all_securities(['etf'])
# # 获得lof基金列表
# df = get_all_securities(['lof'])
# # 获得分级A基金列表
# df = get_all_securities(['fja'])
# # 获得分级B基金列表
# df = get_all_securities(['fjb'])
#
# # 获得2015年10月10日还在上市的所有股票列表
# get_all_securities(date='2015-10-10')
# # 获得2015年10月10日还在上市的 etf 和 lof 基金列表
# get_all_securities(['etf', 'lof'], '2015-10-10')

