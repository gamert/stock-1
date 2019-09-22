# coding=utf-8
from __future__ import print_function, absolute_import, unicode_literals
from gm.api import *
from sklearn import preprocessing

'''
策略思路：
我们按照一定排列规则，将所有股票排序，并选取排名最前或最后的股票，买入，每月换仓一次。
回测数据:SZSE.399239的成份股
回测时间:2018-01-01 08:00:00到2018-08-01 16:00:00
'''


def init(context):
    # 每月第一个交易日的09:40 定时执行algo任务
    schedule(schedule_func=algo, date_rule='1m', time_rule='09:40:00')


def algo(context):
    # 获取上一个交易日的日期
    last_day = get_previous_trading_date(exchange='SHSE', date=context.now)
    # 获取沪深300成份股
    context.stock300 = get_history_constituents(index='SZSE.399239', start_date=last_day,
                                                end_date=last_day)[0]['constituents'].keys()
    # 获取当天有交易的股票
    not_suspended = get_history_instruments(symbols=context.stock300, start_date=last_day, end_date=last_day)
    not_suspended = [item['symbol'] for item in not_suspended if not item['is_suspended']]
    fin = get_fundamentals(table='deriv_finance_indicator', symbols=not_suspended, start_date=last_day,
                           end_date=last_day,
                           fields='TAGRT,ROEANNUAL,SHTLIABTOTLIABRT', df=True)
    fin['PB'] = get_fundamentals(table='trading_derivative_indicator', symbols=not_suspended, start_date=last_day,
                                 end_date=last_day, fields='PB', df=True)['PB']
    fin.index = fin.symbol
    del fin['symbol'], fin['pub_date'], fin['end_date']
    fin = fin.fillna(0)

    data = preprocessing.scale(fin)
    score = []
    for i in data:
        # score.append(5.96*i[0]+3.36*i[1]+5.03*i[2]+3*i[3])
        score.append(sum(i))
    fin['score'] = score
    fin = fin.sort_values(by='score', axis=0, ascending=True)

    symbols_pool = list(fin.tail(10).index)

    print(symbols_pool)
    order_close_all()

    # 获取股票的权重
    percent = 1 / len(symbols_pool)
    # 买在标的池中的股票
    for symbol in symbols_pool:
        order_target_percent(symbol=symbol, percent=percent, order_type=OrderType_Market,
                             position_side=PositionSide_Long)
        print(symbol, '以市价单调多仓到仓位', percent)


if __name__ == '__main__':
    '''
    strategy_id策略ID,由系统生成
    filename文件名,请与本文件名保持一致
    mode实时模式:MODE_LIVE回测模式:MODE_BACKTEST
    token绑定计算机的ID,可在系统设置-密钥管理中生成
    backtest_start_time回测开始时间
    backtest_end_time回测结束时间
    backtest_adjust股票复权方式不复权:ADJUST_NONE前复权:ADJUST_PREV后复权:ADJUST_POST
    backtest_initial_cash回测初始资金
    backtest_commission_ratio回测佣金比例
    backtest_slippage_ratio回测滑点比例
    '''
    run(strategy_id='73bb5bf2-a536-11e8-bd52-9cd21ef04ea9',
        filename='多因子策略.py',
        mode=MODE_BACKTEST,
        token='c395247a76e8a5caeee699d668d6f550213bc418',
        backtest_start_time='2018-01-01 08:00:00',
        backtest_end_time='2018-08-01 16:00:00',
        backtest_adjust=ADJUST_PREV,
        backtest_initial_cash=10000000,
        backtest_commission_ratio=0.0001,
        backtest_slippage_ratio=0.0001)

