import os
import time

import pdfplumber


# 财报处理...'主要会计数据和财务指标'
class PdfCaibao():
    def __init__(self):
        self.table_keyword = ['主要会计数据和财务指标']
        self.pdf = None
        self.stop = False

    def _open_pdf(self, path):
        try:
            self.pathfile=path
            pdf = pdfplumber.open(path, password='')
            return pdf
        except:
            #os.remove(path)  # 屏蔽此处的话，如果文件打开出错，则不会删除
            print("*************open pdf error*******************",self.pathfile)
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
        print("_parse_pdf_imp: ", self.pathfile,"dt=",start3-start1)

    # df = pd.DataFrame(table[1:], columns=table[0])
    # for row in table:
    #     for cell in row:
    #         print(cell, end="\t|")
    #     print()
    def check_page(self, page):
        page_text = page.extract_text()
        # print(t)
        for keyword in self.table_keyword:
            if keyword in page_text:
                self.parse_page_tables(page)
                self.stop = True
                #print(page_text)
                break

    def parse_page_tables(self,page):
        tables = page.extract_tables()
        for table in tables:
            print(table)
            if self.parse_a_table(table):
                break

    # <class 'list'>: [['', None, None, '', None, None, '', None, None, '', '本报告期比上年同期增', ''], ['', '', '', '', '本报告期', '', '', '上年同期', '', None, None, None], [None, None, None, None, None, None, None, None, None, None, '减', None], ['', None, None, '', None, None, '', None, None, None, None, None], ['', '营业收入（元）', '', '17,163,900.71', None, None, '58,415,469.31', None, None, '', '-70.62%', ''], ['', '归属于上市公司股东的净利润（元）', '', '-26,664,969.79', None, None, '-7,442,140.89', None, None, '', '', ''], ['', '归属于上市公司股东的扣除非经常性', '', '', None, None, '', None, None, '', None, None], [None, None, None, '', '-11,834,904.01', '', '', '-10,717,278.99', '', '', '', ''], [None, '损益的净利润（元）', None, None, None, None, None, None, None, None, None, None], [None, None, None, '', None, None, '', None, None, '', None, None], ['', '经营活动产生的现金流量净额（元）', '', '-8,215,246.15', None, None, '63,511,881.16', None, None, '', '-112.93%', ''], ['', '基本每股收益（元/股）', '', '-0.12', None, None, '-0.03', None, None, '', '', ''], ['', '稀释每股收益（元/股）', '', '-0.12', None, None, '-0.03', None, None, '', '', ''], ['', '加权平均净资产收益率', '', '', '-7.49%', '', '', '-2.12%', '', '', '', ''], ['', None, None, '', None, None, '', None, None, '', '本报告期末比上年度末', ''], ['', '', '', '', '本报告期末', '', '', '上年度末', '', None, None, None], [None, None, None, None, None, None, None, None, None, None, '增减', None], ['', None, None, '', None, None, '', None, None, None, None, None], ['', '总资产（元）', '', '538,148,609.35', None, None, '480,364,514.33', None, None, '', '12.03%', ''], ['', '归属于上市公司股东的净资产（元）', '', '340,940,193.22', None, None, '369,207,911.60', None, None, '', '-7.66%', '']]
    def parse_a_table(self,table):
        return True


if __name__ == '__main__':
    path = "G:/_Stock/temp/000007全新好2016年半年度报告.(2181k).PDF"
    cb = PdfCaibao()
    cb.parse_pdf(path)