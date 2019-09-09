import os
import time

import pdfplumber

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
    v = v.replace(",", "")
    v = v.replace("%", "")
    if value_is_null(v):
        return 0
    return float(v)

# float: '-70.62%'
def VALUE_PERCENT_DIGIT(v):
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
    return row_has_key_2(row2, 4, "本报告", 7, "上年") and row1[10] and row1[10].startswith("本报告期") \
           and row3[10] and row3[10].endswith('减') and row_is_null(row4)


def rows_can_merge(row1, row2, row3, row4):
    return row_has_digit_key_2(row2, 4, 7) and row_is_null_exept(row1, [1]) and row_is_null_exept(row3, [1]) \
           and row_is_null(row4)


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


class CaiBaoDef():
    def __init__(self):
        self.dic = {'yysr': CaiBaoItem("营业收入"),
                    'jlr': CaiBaoItem("归属于上市公司股东的净利润"),
                    'jlr_kf': CaiBaoItem("归属于上市公司股东的扣除非经常性损益的净利润"),
                    'xjl_je': CaiBaoItem("经营活动产生的现金流量净额"),
                    'mgsy_jb': CaiBaoItem("基本每股收益"),
                    'mgsy_xs': CaiBaoItem("稀释每股收益"),
                    'zcsy_jq': CaiBaoItem("加权平均净资产收益率"),
                    'zzc': CaiBaoItem("总资产"),
                    'jzc': CaiBaoItem("归属于上市公司股东的净资产")
                    }

    def parse_row(self, row):
        row_key = row[1]
        for key, value in self.dic.items():
            if row_key.startswith(value.name):
                value.setParam(VALUE_DIGIT(row[3]), VALUE_DIGIT(row[6]), VALUE_PERCENT_DIGIT(row[10]))
                return 1
        return 0

    def parse(self, table):
        self.tidy_talbe(table)
        rows_find = 0
        for row in table:
            rows_find += self.parse_row(row)
        return rows_find > 0

    def tidy_talbe(self, table):
        # remove the no-use title rows
        heads = []
        for index in range(len(table) - 4, -1, -1):
            if rows_is_head(table[index], table[index + 1], table[index + 2], table[index + 3]):
                heads.append(index)
        for i in range(len(heads)):
            index = heads[i]
            pop_list_items(table, index, 4)

        merges = []
        for index in range(len(table) - 4, -1, -1):
            if rows_can_merge(table[index], table[index + 1], table[index + 2], table[index + 3]):
                merges.append(index)
                table[index][1] += table[index + 2][1]
                table[index][4] = table[index + 1][4]
                table[index][7] = table[index + 1][7]

        for i in range(len(merges)):
            index = merges[i]
            pop_list_items(table, index, 4)

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
            print(table)
            if self.parse_a_table(table):
                break

    def parse_a_table(self, table):
        return self.caibao_tbl.parse(table)
        # df = pd.DataFrame(table[1:], columns=table[0])


if __name__ == '__main__':
    path = "G:/_Stock/temp/000007全新好2016年半年度报告.(2181k).PDF"
    cb = PdfCaibao()
    table = [['', None, None, '', None, None, '', None, None, '', '本报告期比上年同期增', ''],
             ['', '', '', '', '本报告期', '', '', '上年同期', '', None, None, None],
             [None, None, None, None, None, None, None, None, None, None, '减', None],
             ['', None, None, '', None, None, '', None, None, None, None, None],
             ['', '营业收入（元）', '', '17,163,900.71', None, None, '58,415,469.31', None, None, '', '-70.62%', ''],
             ['', '归属于上市公司股东的净利润（元）', '', '-26,664,969.79', None, None, '-7,442,140.89', None, None, '', '', ''],
             ['', '归属于上市公司股东的扣除非经常性', '', '', None, None, '', None, None, '', None, None],
             [None, None, None, '', '-11,834,904.01', '', '', '-10,717,278.99', '', '', '', ''],
             [None, '损益的净利润（元）', None, None, None, None, None, None, None, None, None, None],
             [None, None, None, '', None, None, '', None, None, '', None, None],
             ['', '经营活动产生的现金流量净额（元）', '', '-8,215,246.15', None, None, '63,511,881.16', None, None, '', '-112.93%', ''],
             ['', '基本每股收益（元/股）', '', '-0.12', None, None, '-0.03', None, None, '', '', ''],
             ['', '稀释每股收益（元/股）', '', '-0.12', None, None, '-0.03', None, None, '', '', ''],
             ['', '加权平均净资产收益率', '', '', '-7.49%', '', '', '-2.12%', '', '', '', ''],
             ['', None, None, '', None, None, '', None, None, '', '本报告期末比上年度末', ''],
             ['', '', '', '', '本报告期末', '', '', '上年度末', '', None, None, None],
             [None, None, None, None, None, None, None, None, None, None, '增减', None],
             ['', None, None, '', None, None, '', None, None, None, None, None],
             ['', '总资产（元）', '', '538,148,609.35', None, None, '480,364,514.33', None, None, '', '12.03%', ''],
             ['', '归属于上市公司股东的净资产（元）', '', '340,940,193.22', None, None, '369,207,911.60', None, None, '', '-7.66%', '']]

    # v = '-11,834,904.01'
    # print(value_is_digit(v))
    #
    # row = table[7]
    # row_has_digit_key_2(row, 4, 7)
    # row = table[17]
    # v = row_is_null(row)
    #print('本报告期末'.startswith("本报告"))
    cb.parse_a_table(table)
    # cb.parse_pdf(path)
