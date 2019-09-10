"""
e.g: http://data.eastmoney.com/bbsj/201806/lrb.html
"""
import csv
import json
import os
import re
import time

import requests

# 设置文件保存在D盘eastmoney文件夹下
file_path = '.\\eastmoney'
if not os.path.exists(file_path):
    os.mkdir(file_path)
os.chdir(file_path)

MAX_YEAR = 2019
year = 2019
quarter = 1

class eastmoney_cwbb_crawler():

    # 1 设置表格爬取时期
    def set_table(self):
        print('*' * 80)
        print('\t\t\t\t东方财富网报表下载')
        print('作者：高级农民工  2018.10.10')
        print('--------------')

        # 1 设置财务报表获取时期
        year = int(float(input('请输入要查询的年份(四位数2007-{})：\n'.format(MAX_YEAR))))
        # int表示取整，里面加float是因为输入的是str，直接int会报错，float则不会
        # https://stackoverflow.com/questions/1841565/valueerror-invalid-literal-for-int-with-base-10
        while (year < 2007 or year > MAX_YEAR):
            year = int(float(input('年份数值输入错误，请重新输入：\n')))

        quarter = int(float(input('请输入小写数字季度(1:1季报，2-年中报，3：3季报，4-年报)：\n')))
        while (quarter < 1 or quarter > 4):
            quarter = int(float(input('季度数值输入错误，请重新输入：\n')))

        # 转换为所需的quarter 两种方法,2表示两位数，0表示不满2位用0补充，
        # http://www.runoob.com/python/att-string-format.html
        quarter = '{:02d}'.format(quarter * 3)
        # quarter = '%02d' %(int(month)*3)

        # 确定季度所对应的最后一天是30还是31号
        if (quarter == '06') or (quarter == '09'):
            day = 30
        else:
            day = 31
        date = '{}-{}-{}'.format(year, quarter, day)
        # print('date:', date)  # 测试日期 ok

        # 2 设置财务报表种类
        tables = int(
            input('请输入查询的报表种类对应的数字(1-业绩报表；2-业绩快报表：3-业绩预告表；4-预约披露时间表；5-资产负债表；6-利润表；7-现金流量表): \n'))
        return self.set_talbe_param(date, tables)

    # @date:2019-06-30  2019-09-31
    # @tables [1,7]
    def set_talbe_param(self, date, bb_type):
        dict_tables = {1: '业绩报表', 2: '业绩快报表', 3: '业绩预告表',
                       4: '预约披露时间表', 5: '资产负债表', 6: '利润表', 7: '现金流量表'}

        dict = {1: 'YJBB', 2: 'YJKB', 3: 'YJYG',
                4: 'YYPL', 5: 'ZCFZB', 6: 'LRB', 7: 'XJLLB'}
        category = dict[bb_type]

        # js请求参数里的type，第1-4个表的前缀是'YJBB20_'，后3个表是'CWBB_'
        # 设置set_table()中的type、st、sr、filter参数
        if bb_type == 1:
            category_type = 'YJBB20_'
            st = 'latestnoticedate'
            sr = -1
            filter = "(securitytypecode in ('058001001','058001002'))(reportdate=^%s^)" % (date)
        elif bb_type == 2:
            category_type = 'YJBB20_'
            st = 'ldate'
            sr = -1
            filter = "(securitytypecode in ('058001001','058001002'))(rdate=^%s^)" % (date)
        elif bb_type == 3:
            category_type = 'YJBB20_'
            st = 'ndate'
            sr = -1
            filter = " (IsLatest='T')(enddate=^2018-06-30^)"
        elif bb_type == 4:
            category_type = 'YJBB20_'
            st = 'frdate'
            sr = 1
            filter = "(securitytypecode ='058001001')(reportdate=^%s^)" % (date)
        else:
            category_type = 'CWBB_'
            st = 'noticedate'
            sr = -1
            filter = '(reportdate=^%s^)' % (date)

        category_type = category_type + category
        # print(category_type)
        # 设置set_table()中的filter参数

        yield {
            'date': date,
            'category': dict_tables[bb_type],
            'category_type': category_type,
            'st': st,
            'sr': sr,
            'filter': filter
        }


    # 2 设置表格爬取起始页数
    def page_choose(self, page_all, start_page = -1, nums = -1):
        # 选择爬取页数范围
        if start_page == -1:
            start_page = int(input('请输入下载起始页数：\n'))
        if nums == -1:
            nums = input('请输入要下载的页数，（若需下载全部则按回车）：\n')
        print('*' * 80)

        # 判断输入的是数值还是回车空格
        if nums.isdigit():
            end_page = start_page + int(nums)
        elif nums == '':
            end_page = int(page_all.group(1))
        else:
            print('页数输入错误')

        # 返回所需的起始页数，供后续程序调用
        yield {
            'start_page': start_page,
            'end_page': end_page
        }

    # 3 表格正式爬取
    def get_table(self, date, category_type, st, sr, filter, page):
        # 参数设置
        params = {
            # 'type': 'CWBB_LRB',
            'type': category_type,  # 表格类型
            'token': '70f12f2f4f091e459a279469fe49eca5',
            'st': st,
            'sr': sr,
            'p': page,
            'ps': 50,  # 每页显示多少条信息
            'js': 'var LFtlXDqn={pages:(tp),data: (x)}',
            'filter': filter,
            # 'rt': 51294261  可不用
        }
        url = 'http://dcfm.eastmoney.com/em_mutisvcexpandinterface/api/js/get?'

        # print(url)
        response = requests.get(url, params=params).text
        # print(response)
        # 确定页数
        pat = re.compile('var.*?{pages:(\d+),data:.*?')
        page_all = re.search(pat, response)
        print(page_all.group(1))  # ok

        # 提取{},json.loads出错
        # pattern = re.compile('var.*?data: \[(.*)]}', re.S)

        # 提取出list，可以使用json.dumps和json.loads
        pattern = re.compile('var.*?data: (.*)}', re.S)
        items = re.search(pattern, response)
        # 等价于
        # items = re.findall(pattern,response)
        # print(items[0])
        data = items.group(1)
        data = json.loads(data)
        # data = json.dumps(data,ensure_ascii=False)

        return page_all, data, page


    def _build_file_name(self, category):
        return '{}_{}_{}.csv'.format(category, year, quarter)


    # 写入表头
    # 方法1 借助csv包，最常用
    def write_header(self, data, category):
        with open(self._build_file_name(category), 'a', encoding='utf_8_sig', newline='') as f:
            headers = list(data[0].keys())
            # print(headers)  # 测试 ok
            writer = csv.writer(f)
            writer.writerow(headers)


    def write_table(self,data, page, category):
        print('\n正在下载第 %s 页表格' % page)
        # 写入文件方法1
        for d in data:
            with open(self._build_file_name(category), 'a', encoding='utf_8_sig', newline='') as f:
                w = csv.writer(f)
                w.writerow(d.values())

    #category_type = {str} 'YJBB20_YJBB'
    # date = {str} '2019-06-30'
    # quarter = {int} 1
    # sr = {int} -1
    # st = {str} 'latestnoticedate'
    # year = {int} 2019
    def _crawl(self, date, category, category_type, st, sr, filter, start_page=0, end_page=-1):
        # 取得首页报表...
        constant = self.get_table(date, category_type, st, sr, filter, 1)
        page_all = constant[0]

        if start_page == -1 or end_page == -1:
            for i in self.page_choose(page_all):
                start_page = i.get('start_page')
                end_page = i.get('end_page')

        # 写入表头
        self.write_header(constant[1], category)
        start_time = time.time()  # 下载开始时间
        # 爬取表格主程序
        for page in range(start_page, end_page):
            func = self.get_table(date, category_type, st, sr, filter, page)
            data = func[1]
            page = func[2]
            self.write_table(data, page, category)
            #
            # self._crawl(date, category, category_type, st, sr, filter, page)
        end_time = time.time() - start_time  # 结束时间
        print('下载用时: {:.1f} s'.format(end_time))

    def do_clawl(self, params_dic, start_page=0, end_page=-1):
        # 获取总页数，确定起始爬取页数
        for i in params_dic:
            date = i.get('date')
            category = i.get('category')
            category_type = i.get('category_type')
            st = i.get('st')
            sr = i.get('sr')
            filter = i.get('filter')

        self.crawl(date, category, category_type, st, sr, filter, start_page, end_page)

    def main_bat(self):
        params_dic = self.set_table()
        # 1-业绩报表；2-业绩快报表：3-业绩预告表；4-预约披露时间表；5-资产负债表；6-利润表；7-现金流量表
        # params_dic = self.set_talbe_param("2019-09-30", 2)
        self.do_clawl(params_dic)


if __name__ == '__main__':
    ec = eastmoney_cwbb_crawler()
    params_dic = ec.set_talbe_param("2019-09-30", 2)
    ec.do_clawl(params_dic, 0, 1)

    # 创建数据库..
    header = ['scode', 'sname', 'securitytype', 'trademarket', 'latestnoticedate', 'reportdate', 'basiceps', 'cutbasiceps', 'totaloperatereve', 'ystz', 'yshz', 'parentnetprofit', 'sjltz', 'sjlhz', 'roeweighted', 'bps', 'mgjyxjje', 'xsmll', 'publishname', 'assigndscrpt', 'gxl', 'securitytypecode', 'trademarketcode', 'firstnoticedate']

