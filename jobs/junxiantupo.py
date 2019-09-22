import tushare as ts
import pandas as pd
import time

# 均线突破选股
def get_stock(code, jun):
    # 以当前日期为文件名保存结果文件
    now_day = time.strftime('%Y-%m-%d')
    filename = './result/' + now_day + 'result.txt'
    fp1 = open(filename, 'a')
    # 用try为了避免有些股票没有数据而报错
    try:
        # 获取股票数据从2019-01-01开始到当天的数据
        df = ts.get_hist_data(code, start='2019-01-01', end=now_day)
        df_close = df['close']
        x = pd.DataFrame(df_close)
        y = x.sort_values(by='date', ascending=True)
        # 获取均线数据
        stockDate = y.rolling(jun).mean()
        lists = []
        for i in range(1, len(df_close)):
            lists.append([df_close.index[-i], stockDate.close[i - 1], df_close[-i]])
        chang = len(df)
        lists.append([df_close.index[0], stockDate.close[chang - 1], df_close[0]])
        stock_jun = pd.DataFrame(lists, columns=('date', 'jun', 'close'))
        jun_value = float('%.2f' % stock_jun.iloc[-1].jun)
        close = float('%.2f' % stock_jun.iloc[-1].close)

        jun_1_value = float('%.2f' % stock_jun.iloc[-2].jun)
        close_1 = float('%.2f' % stock_jun.iloc[-2].close)
        if jun_1_value > close_1 and jun_value < close:
            print('%s  突破%s日均线啦' % (code, jun))
            fp1.write('%s  突破%s日均线啦\n' % (code, jun))
    except:
        pass
    fp1.close()


def get_all_stock(jun):
    fp = open('stock_code.txt')
    codes = fp.readlines()
    # 遍历所有的股票
    for code in codes:
        code_all = code.strip('\n')
        get_stock(code_all, jun)
    fp.close()


get_all_stock(60)

