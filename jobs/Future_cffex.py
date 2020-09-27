from io import StringIO
import csv
import urllib.request

# 中金所金融期货日统计数据爬取
# 构造URL下载每个交易日统计的附件csv文件，提取csv文件中的次月交割的股指期货统计数据
def get_csv(month, day, year='2018'):
    """构造URL下载日统计数据文件"""
    try:
        url = 'http://www.cffex.com.cn/sj/hqsj/rtj/2018' + month + '/' + day + '/2018' + month + day + '_1.csv'
        data = urllib.request.urlopen(url).read().decode('ascii', 'ignore')
        dataFile = StringIO(data)
        csvReader = csv.reader(dataFile)
        print(url)
        with open('data_cffex_IH.csv', 'a', encoding='utf-8', newline='') as csvfile:
            fieldnames = ['time', 'code', 'open', 'highest', 'lowest', 'volume', 'inventory', 'close', 'settlement',
                          'zhangdie1', 'zhangdie2', 'implied volatility', 'delta']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            time = year + month + day
            for row in csvReader:

                if row[0] == 'IH18' + str(int(month) + 1).zfill(
                        2) + '                        ':  # row[0]=='IH18'+str(int(month)+1).zfill(2)+'                        '
                    row.insert(12, time)
                    print(row[12] + row[0] + '!')

                    writer.writerow(
                        {'code': row[0], 'open': row[1], 'highest': row[2], 'lowest': row[3], 'volume': row[4],
                         'inventory': row[5], 'close': row[6], 'settlement': row[7], 'zhangdie1': row[8],
                         'zhangdie2': row[9], 'implied volatility': row[10], 'delta': row[11], 'time': row[12]})
    except:
        print("It is not a trading day! ")


if __name__ == '__main__':
    for month in range(8, 9):  # 改变range参数可以获取不同月份的日统计文件
        month = str(month)
        month = month.zfill(2)
        for day in range(1, 32):  # 提取31日的日统计文件
            day = str(day)
            day = day.zfill(2)
            get_csv(month, day, year='2020')
