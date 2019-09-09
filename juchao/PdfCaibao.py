import os
import time

import pdfplumber

COL_THIS = 1
COL_LAST = 2
COL_RATIO = 3
# 从list中删除下标开始的count个元素
def pop_list_items(tbl, index, count):
    for i in range(count - 1, -1, -1):
        tbl.pop(index + i)

def value_is_null(v):
    return v == None or v == ""


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass

    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass

    return False

# 判断财务数字: v = '-11,834,904.01'
def value_is_digit(v):
    if value_is_null(v):
        return False
    if v.isdigit() or v.isdecimal():
        return True
    v = v.replace(",", "")
    return is_number(v)

# 转换财务数字: v = '-11,834,904.01'
def VALUE_DIGIT(v):
    if value_is_null(v):
        return 0
    v = v.replace(",", "")
    v = v.replace("%", "")
    v = v.replace("(", "")
    v = v.replace(")", "")
    if value_is_null(v):
        return 0
    return float(v)

# float: '-70.62%'
def VALUE_PERCENT_DIGIT(v):
    #'增加0.28个百分点'
    if v :
        if v.startswith("增加"):
            return 0
        elif v.startswith("减少"):
            return 0
    return VALUE_DIGIT(v)

def row_value_is_null(row, key_index):
    return value_is_null(row[key_index])

def row_value_is_digit(row, key_index):
    return value_is_digit(row[key_index])

def row_is_null(row):
    for index in range(len(row)):
        isnull = row_value_is_null(row, index)
        if not isnull:
            return False
    return True

# 判断是否为空行...
def row_is_null_exept(row, indexs):
    for index in range(len(row)):
        isnull = row_value_is_null(row, index)
        if index in indexs:
            if isnull:
                return False
            continue
        elif not isnull:
            return False
    return True

# 判断是否含有2个数字key
def row_has_digit_key_2(row, key1_index, key2_index):
    return row_value_is_digit(row, key1_index) and row_value_is_digit(row, key2_index)


def row_has_key_2(row, key1_index, key1, key2_index, key2):
    return row[key1_index] and row[key1_index].startswith(key1) \
           and row[key2_index] and row[key2_index].startswith(key2)


def rows_is_head(row1, row2, row3, row4):
    return row_has_key_2(row2, COL_THIS, "本报告", COL_LAST, "上年") and row1[COL_RATIO] and row1[COL_RATIO].startswith("本报告期") \
           and row3[10] and row3[10].endswith('减') and row_is_null(row4)


def rows_can_merge(row1, row2, row3, row4):
    return row_has_digit_key_2(row2, COL_THIS, COL_LAST) and row_is_null_exept(row1, [1]) and row_is_null_exept(row3, [1]) \
           and row_is_null(row4)

# 判空并且移除空列
def clos_null_remove(row):
    for i in range(len(row)-1,-1,-1):
        if value_is_null(row[i]):
            row.pop(i)
    # for i in range(len(rows)):
    #     row = rows[i]
    #     if not value_is_null(row[clo_index]):
    #         return False
    # for i in range(len(rows)):
    #     rows[i].pop(clo_index)
    return True

class CaiBaoItem():
    def __init__(self, name):
        self.name = name
        self.value = 0
        self.value_last = 0
        self.per = 0

    def setParam(self, value, value_last, per):
        self.value = value
        self.value_last = value_last
        self.per = per

    def setParamRow(self, row):
        v1 = len(row) > COL_THIS and row[COL_THIS] or ""
        v2 = len(row) > COL_LAST and row[COL_LAST] or ""
        v3 = len(row) > COL_RATIO and row[COL_RATIO] or ""
        self.setParam(VALUE_DIGIT(v1), VALUE_DIGIT(v2), VALUE_PERCENT_DIGIT(v3))
        return 1


C_YYSR = "营业收入"
C_YYLR = "营业利润"
C_LRZE = "利润总额"
C_JLR = "归属于上市公司股东的净利润"
C_JLR_KF ="归属于上市公司股东的扣除非经常性损益的净利润"
C_KF ="扣除非经常性损益"
C_XJL_JE ="经营活动产生的现金流量净额"
C_MGSY_JB ="基本每股收益"
C_MGSY_XS ="稀释每股收益"
C_ZCSY_JQ ="加权平均净资产收益率"
C_ZCSY_JQ1 ="净资产收益率"
C_JQPJ = "加权平均"

C_ZZC ="总资产"    #
C_ZZC1 ="资产总额"    #
C_ZFZ1 = "负债总额"
C_JZC ="归属于上市公司股东的净资产"

class CaiBaoDef():
    def __init__(self):
        # self.dic = {'yysr': CaiBaoItem("营业收入"),
        #             'jlr': CaiBaoItem("归属于上市公司股东的净利润"),
        #             'jlr_kf': CaiBaoItem("归属于上市公司股东的扣除非经常性损益的净利润"),
        #             'xjl_je': CaiBaoItem("经营活动产生的现金流量净额"),
        #             'mgsy_jb': CaiBaoItem("基本每股收益"),
        #             'mgsy_xs': CaiBaoItem("稀释每股收益"),
        #             'zcsy_jq': CaiBaoItem("加权平均净资产收益率"),
        #             'zzc': CaiBaoItem("总资产"),
        #             'jzc': CaiBaoItem("归属于上市公司股东的净资产")
        #             }
        self.yysr = CaiBaoItem(C_YYSR)
        self.yylr = CaiBaoItem(C_YYLR)
        self.lrze = CaiBaoItem(C_LRZE)
        self.jlr = CaiBaoItem(C_JLR)
        self.jlr_kf = CaiBaoItem(C_JLR_KF)
        self.xjl_je = CaiBaoItem(C_XJL_JE)
        self.mgsy_jb = CaiBaoItem(C_MGSY_JB)
        self.mgsy_xs = CaiBaoItem(C_MGSY_XS)
        self.zcsy_jq = CaiBaoItem(C_ZCSY_JQ)
        self.zzc = CaiBaoItem(C_ZZC)
        self.zfz = CaiBaoItem(C_ZFZ1)
        self.jzc = CaiBaoItem(C_JZC)

    def parse_row(self, row):
        row_key = row[0]
        if len(row) > 2:
            if row_key.startswith(C_YYSR):
                return self.yysr.setParamRow(row)
            if row_key.startswith(C_YYLR):
                return self.yylr.setParamRow(row)
            if row_key.startswith(C_LRZE):
                return self.lrze.setParamRow(row)
            if row_key.startswith(C_JLR):
                return self.jlr.setParamRow(row)
            if row_key.startswith(C_JLR_KF) or (row_key.__contains__(C_JLR) and row_key.__contains__(C_KF)):
                return self.jlr_kf.setParamRow(row)
            if row_key.startswith(C_XJL_JE):
                return self.xjl_je.setParamRow(row)
            if row_key.startswith(C_MGSY_JB):
                return self.mgsy_jb.setParamRow(row)
            if row_key.startswith(C_MGSY_XS):
                return self.mgsy_xs.setParamRow(row)
            if row_key.startswith(C_ZCSY_JQ) or (row_key.startswith(C_ZCSY_JQ1) and row_key.__contains__(C_JQPJ)):
                return self.zcsy_jq.setParamRow(row)
            if row_key.startswith(C_ZZC) or row_key.startswith(C_ZZC1):
                return self.zzc.setParamRow(row)
            if row_key.startswith(C_ZFZ1):
                return self.zfz.setParamRow(row)
            if row_key.startswith(C_JZC):
                return self.jzc.setParamRow(row)

        # for key, value in self.dic.items():
        #     if row_key.startswith(value.name):
        #         value.setParam(VALUE_DIGIT(row[COL_THIS]), VALUE_DIGIT(row[COL_LAST]), VALUE_PERCENT_DIGIT(row[COL_RATIO]))
        #         return 1
        return 0

    def parse(self, table):
        self.tidy_talbe(table)
        rows_find = 0
        for row in table:
            rows_find += self.parse_row(row)
        #print(self.dic)
        return rows_find > 0

    # 只能使用关键字进行...模糊匹配
    def tidy_talbe(self, table):
        for index in range(len(table) - 1, -1, -1):
            clos_null_remove(table[index])
            if len(table[index]) == 0:
                table.pop(index)
            else:
                tt = table[index][0]
                tt = tt.replace("\n", "")
                # 特殊的处理
                # 1.
                if len(table[index]) == 1 and tt.startswith("归属于上市公司股东的扣除") and row_has_digit_key_2(table[index+1],0,1):
                    table[index][0] = C_JLR_KF
                    table[index] += table[index+1]
                    table.pop(index+1)
                else:
                    table[index][0] = tt
        print(table)
        #
        # # 去除所有空的列...
        # clos = len(table[0])
        # for index in range(clos - 1, -1, -1):
        #     clos_null_remove(table, index)
        #
        # # remove the no-use title rows
        # heads = []
        # for index in range(len(table) - 4, -1, -1):
        #     if rows_is_head(table[index], table[index + 1], table[index + 2], table[index + 3]):
        #         heads.append(index)
        # for i in range(len(heads)):
        #     index = heads[i]
        #     pop_list_items(table, index, 4)
        #
        # merges = []
        # for index in range(len(table) - 4, -1, -1):
        #     if rows_can_merge(table[index], table[index + 1], table[index + 2], table[index + 3]):
        #         merges.append(index)
        #         table[index][1] += table[index + 2][1]
        #         table[index][COL_THIS] = table[index + 1][COL_THIS]
        #         table[index][COL_LAST] = table[index + 1][COL_LAST]
        #
        # for i in range(len(merges)):
        #     index = merges[i]
        #     pop_list_items(table, index+1, 3)

# 财报处理...'主要会计数据和财务指标'
class PdfCaibao():
    def __init__(self):
        self.table_keyword = ['主要会计数据和财务指标']
        self.pdf = None
        self.stop = False
        self.caibao_tbl = CaiBaoDef()

    def _open_pdf(self, path):
        try:
            self.pathfile = path
            pdf = pdfplumber.open(path, password='')
            return pdf
        except:
            # os.remove(path)  # 屏蔽此处的话，如果文件打开出错，则不会删除
            print("*************open pdf error*******************", self.pathfile)
        return None

    def parse_pdf(self, path, POS=1):
        start1 = time.time()
        self.pdf = self._open_pdf(path)
        if not self.pdf:
            return
        start2 = time.time()
        begin_index = 0
        for i in range(begin_index, len(self.pdf.pages)):
            page = self.pdf.pages[i]
            self.check_page(page)
            if self.stop:
                # 解析表格
                print("_parse_pdf_imp: stop=", self.stop)
                break
        start3 = time.time()
        print("_parse_pdf_imp: ", self.pathfile, "dt=", start3 - start1)

    def check_page(self, page):
        page_text = page.extract_text()
        # print(t)
        for keyword in self.table_keyword:
            if keyword in page_text:
                self.parse_page_tables(page)
                self.stop = True
                # print(page_text)
                break

    def parse_page_tables(self, page):
        tables = page.extract_tables()
        for table in tables:
            #print(table)
            if self.parse_a_table(table):
                break

    def parse_a_table(self, table):
        return self.caibao_tbl.parse(table)
        # df = pd.DataFrame(table[1:], columns=table[0])


if __name__ == '__main__':
    cb = PdfCaibao()
    # table = [['', None, None, '', None, None, '', None, None, '', '本报告期比上年同期增', ''],
    #          ['', '', '', '', '本报告期', '', '', '上年同期', '', None, None, None],
    #          [None, None, None, None, None, None, None, None, None, None, '减', None],
    #          ['', None, None, '', None, None, '', None, None, None, None, None],
    #          ['', '营业收入（元）', '', '17,163,900.71', None, None, '58,415,469.31', None, None, '', '-70.62%', ''],
    #          ['', '归属于上市公司股东的净利润（元）', '', '-26,664,969.79', None, None, '-7,442,140.89', None, None, '', '', ''],
    #          ['', '归属于上市公司股东的扣除非经常性', '', '', None, None, '', None, None, '', None, None],
    #          [None, None, None, '', '-11,834,904.01', '', '', '-10,717,278.99', '', '', '', ''],
    #          [None, '损益的净利润（元）', None, None, None, None, None, None, None, None, None, None],
    #          [None, None, None, '', None, None, '', None, None, '', None, None],
    #          ['', '经营活动产生的现金流量净额（元）', '', '-8,215,246.15', None, None, '63,511,881.16', None, None, '', '-112.93%', ''],
    #          ['', '基本每股收益（元/股）', '', '-0.12', None, None, '-0.03', None, None, '', '', ''],
    #          ['', '稀释每股收益（元/股）', '', '-0.12', None, None, '-0.03', None, None, '', '', ''],
    #          ['', '加权平均净资产收益率', '', '', '-7.49%', '', '', '-2.12%', '', '', '', ''],
    #          ['', None, None, '', None, None, '', None, None, '', '本报告期末比上年度末', ''],
    #          ['', '', '', '', '本报告期末', '', '', '上年度末', '', None, None, None],
    #          [None, None, None, None, None, None, None, None, None, None, '增减', None],
    #          ['', None, None, '', None, None, '', None, None, None, None, None],
    #          ['', '总资产（元）', '', '538,148,609.35', None, None, '480,364,514.33', None, None, '', '12.03%', ''],
    #          ['', '归属于上市公司股东的净资产（元）', '', '340,940,193.22', None, None, '369,207,911.60', None, None, '', '-7.66%', '']]
    #
    # table = [['项目', '2018年 1-6月', '2017年 1-6月', '比上年同期增减'],
    #                 ['营业收入', '105,974,537,269.94', '69,810,477,567.49', '51.80%'],
    #                 ['营业利润', '19,629,139,535.89', '13,662,612,097.69', '43.67%'],
    #                 ['利润总额', '19,667,844,908.03', '13,826,911,377.53', '42.24%'],
    #                 ['归属于上市公司股东的净利润', '9,123,743,200.32', '7,302,723,984.96', '24.94%'],
    #                 ['扣除非经常性损益后归属于上市公\n司股东的净利润', '9,096,648,908.14', '7,123,504,445.30', '27.70%'],
    #                 ['经营活动产生的现金流量净额', '(4,255,092,906.29)', '21,850,160,718.36', '-119.47%'],
    #                 ['基本每股收益', '0.83', '0.66', '24.94%'], ['稀释每股收益', '0.83', '0.66', '24.94%'],
    #                 ['净资产收益率（全面摊薄）', '6.76%', '6.48%', '增加0.28个百分点'], ['净资产收益率（加权平均）', '6.51%', '6.22%', '增加0.29个百分点'],
    #                 ['项目', '2018年6月 30日', '2017年12月31日', '比年初数增减'],
    #                 ['资产总额', '1,345,151,635,212.87', '1,165,346,917,804.55', '15.43%'],
    #                 ['负债总额', '1,139,367,483,490.15', '978,672,978,646.26', '16.42%'],
    #                 ['归属于上市公司股东的净资产', '134,892,180,436.06', '132,675,315,293.33', '1.67%']]
    #
    table = [['', '本报告期', '上年同期', '本报告期比上年同期增减'], ['营业收入（元）', '102,150,497.70', '59,545,809.66', '71.55%'],
                    ['归属于上市公司股东的净利润（元）', '2,985,718.12', '1,212,220.46', '146.30%'], ['归属于上市公司股东的扣除非经常性损', '', '', ''],
                    [None, '2,997,716.74', '1,324,311.10', '126.36%'], ['益的净利润（元）', None, None, None],
                    [None, '', '', ''], ['经营活动产生的现金流量净额（元）', '105,056,325.86', '-6,509,453.03', '1,713.90%'],
                    ['基本每股收益（元/股）', '0.0356', '0.0144', '147.22%'], ['稀释每股收益（元/股）', '0.0356', '0.0144', '147.22%'],
                    ['加权平均净资产收益率', '3.60%', '1.50%', '2.10%'], ['', '', '', '本报告期末比上年度末增'], ['', '本报告期末', '上年度末', None],
                    [None, None, None, '减'], ['', '', '', None],
                    ['总资产（元）', '463,831,852.88', '398,673,507.14', '16.34%'],
                    ['归属于上市公司股东的净资产（元）', '84,508,894.38', '81,523,176.25', '3.66%']]

    # v = '-11,834,904.01'
    # print(value_is_digit(v))
    #
    # row = table[COL_LAST]
    # row_has_digit_key_2(row, COL_THIS, COL_LAST)
    # row = table[17]
    # v = row_is_null(row)
    #print('本报告期末'.startswith("本报告"))
    cb.parse_a_table(table)
    path = "G:/_Stock/temp/000007全新好2016年半年度报告.(2181k).PDF"
    path = "G:/_Stock/temp/000002万科A2018年半年度报告.(5223k).PDF"
    path = "G:/_Stock/temp/000004国农科技2016年半年度报告.(1789k).PDF"
    #cb.parse_pdf(path)
