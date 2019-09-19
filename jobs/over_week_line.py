# -*-coding=utf-8-*-
from jobs.tushare_base import *

__author__ = 'rocky'
'''
http://30daydo.com
weigesysu@qq.com
'''
# 获取破指定天数内的新高 比如破60日新高


class ts_over_week_line(tushare_base):
    def __init__(self):
        super().__init__()

    def cacl_by_days(self,days):
        #days = 365*4*5/7
        end_day = datetime.date(datetime.date.today().year, datetime.date.today().month, datetime.date.today().day)
        days = int(days) * 7 / 5
        # 考虑到周六日非交易
        start_day = end_day - datetime.timedelta(days)

        start_day = start_day.strftime("%Y-%m-%d")
        end_day = end_day.strftime("%Y-%m-%d")

        self.loop_all_stocks(start_day,end_day)

    def loop_all_stocks(self,start_day,end_day):

        for name, code in self.code_name.items():
            EachStockID = code.split('.')[0]
            #self.data[name] = get_data(code)
            b, period_high, today_high = self.is_break_high(EachStockID, start_day, end_day)
            if b:
                print("High price on", EachStockID, name, period_high, today_high)

    def is_break_high(self, stockID, start_day,end_day):

        df = ts.get_k_data(stockID, start=start_day, end=end_day, ktype='W')

        period_high = df['high'].max()
        # print period_high
        today_high = df.iloc[-1]['high']
        # 这里不能直接用 .values
        # 如果用的df【：1】 就需要用.values
        # print today_high
        if today_high >= period_high*0.95:
            return True,period_high,today_high
        else:
            return False,period_high,today_high

# main函数入口
if __name__ == '__main__':
    tow = ts_over_week_line()
    tow.cacl_by_days(365*4*5/7)