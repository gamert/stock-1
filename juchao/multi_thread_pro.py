# -*- coding: utf-8 -*-
"""
Created on Fri Apr 26 15:40:31 2019

@author: Herr-kun
"""
from juchao.JuChao_service import *
import socket
import logging

def parase_saved():
    global parase_out_writer


OUT_DIR = r'./temp'

socket.setdefaulttimeout(20)
logger = InitLogger(OUT_DIR + '/log_wyk.log') 

START_DATE = '2017'
END_DATE = '2019'  # str(time.strftime('%Y-%m-%d'))
table_keyword = ['其他与经营活动', '现金']
inside_keyword = ['审计', '咨询', '中介']  # ,'咨询','中介'
outside_keyword = ['收到']

# xlsfile = OUT_DIR+'/Audit Independence 1.xlsx'   # 打开指定路径中的xls文件
# stack_code_set=parase_id(xlsfile)

stack_code_set = ['603118', '000002']  # just for test using

parase_out_file_path = OUT_DIR + '/parase_out_file.csv'
parase_out = open(parase_out_file_path, 'w', newline='', encoding='gb18030')
parase_out_writer = csv.writer(parase_out)


class PdfHandler_kuaiji(PdfHandler):

    def handle(self, path, table_keyword, inside_keyword, outside_keyword, POS = 1):
        open_pdf_succeed = 1
        start1 = time.time()
        try:
            pdf = pdfplumber.open(path, password='')
        except:
            os.remove(path)  # 屏蔽此处的话，如果文件打开出错，则不会删除
            open_pdf_succeed = 0
            print("*************open pdf error*******************")
        start2 = time.time()
        if open_pdf_succeed:
            print("*************open pdf succeed*******************")
            find_table = 0
            find_pre_table = 0
            find_keyword = 0
            find_keyword_outside = 0
            name_find = []
            value_find = []
            page_find = []
            # for page in pdf.pages:
            # print(page.extract_text())
            begin_index = 0
            if POS == 1:
                begin_index = int(len(pdf.pages) / 2)
            begin_index = 6

            for i in range(begin_index, len(pdf.pages)):
                if find_table:
                    find_pre_table = 1
                else:
                    find_pre_table = 0
                find_table = 0
                page = pdf.pages[i]
                # print(page.extract_text())
                data = page.extract_text()
                if len(table_keyword):
                    for keyword in table_keyword:
                        if keyword in data:
                            find_table = 1
                            break
                        else:
                            find_table = 0
                            break
                else:
                    find_table = 1

                if find_table or find_pre_table:

                    # 解析表格
                    # tables = page.extract_tables()
                    # for table in tables:
                    #     print(table)
                    #     # df = pd.DataFrame(table[1:], columns=table[0])
                    #     for row in table:
                    #         for cell in row:
                    #             print(cell, end="\t|")
                    #         print()

                    data_list = data.strip().split()
                    for j in range(len(data_list)):
                        if len(inside_keyword):
                            for keyword in inside_keyword:
                                if keyword in data_list[j]:
                                    find_keyword = 1
                        else:
                            find_keyword = 1

                        if find_keyword:
                            find_keyword = 0
                            print('run here')
                            if len(outside_keyword):
                                for keyword in outside_keyword:
                                    if keyword not in data_list[j]:
                                        find_keyword_outside = 1
                                    else:
                                        find_keyword_outside = 0
                                        break
                            else:
                                find_keyword_outside = 1

                            if find_keyword_outside:
                                find_keyword_outside = 0
                                try:
                                    temp_value = data_list[j + 1]
                                    temp_value = temp_value.replace(',', '')
                                    temp_value = float(temp_value)
                                    name_find.append(data_list[j])
                                    value_find.append(temp_value)
                                    page_find.append(i)
                                    self.rLock3.acquire()
                                    try:
                                        parase_out_writer.writerows([[path.strip().split('/')[-1], data_list[j],
                                                                    str(temp_value), data_list[j + 1], str(i)]])
                                    except:
                                        pass
                                    parase_out.flush()
                                    self.rLock3.release()
                                    print("*****find******{} value is {} and {}".format(data_list[j], data_list[j + 1],
                                                                                        temp_value))
                                    print("*************find in page {}*******************".format(i))
                                    print("*************find in {}*******************".format(path))
                                    break  # only find one result
                                except:
                                    continue

            pdf.close()
            start3 = time.time()

            os.remove(path)  # pdf.close 后删除文件 否则太多了

            print('****time to open PDF file is {}'.format((start2 - start1)))
            print('****time to processing PDF file is {}'.format((start3 - start2)))



if __name__ == '__main__':
    table_keyword = ['其他与经营活动', '现金']
    table_keyword = ['主要会计数据和财务指标']
    inside_keyword = ['审计', '咨询', '中介']  # ,'咨询','中介'
    outside_keyword = ['收到']

    path = "G:/_Stock/temp/000007全新好2016年半年度报告.(2181k).PDF"
    # _parse_pdf_imp(path, table_keyword, inside_keyword, outside_keyword,0)