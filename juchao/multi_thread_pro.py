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


OUT_DIR = r'G:/_Stock/temp'

socket.setdefaulttimeout(20)
logger = logging.getLogger()
logger.setLevel(logging.WARNING)
rq = time.strftime('%Y%m%d%H%M', time.localtime(time.time()))
log_name = OUT_DIR + '/log_wyk.log'
logfile = log_name
fh = logging.FileHandler(logfile, mode='w')
fh.setLevel(logging.WARNING)
formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
fh.setFormatter(formatter)
logger.addHandler(fh)

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

get_url_thread = threading.Thread(target=get_url, args=(OUT_DIR, stack_code_set, START_DATE, END_DATE))
download_pdf_thread = threading.Thread(target=download_pdf, args=(OUT_DIR,))
# download_pdf_thread2 = threading.Thread(target=download_pdf, args=(OUT_DIR,))
parase_pdf_thread = threading.Thread(target=parase_pdf, args=(table_keyword, inside_keyword, outside_keyword))
parase_pdf_thread2 = threading.Thread(target=parase_pdf, args=(table_keyword, inside_keyword, outside_keyword))
parase_pdf_thread3 = threading.Thread(target=parase_pdf, args=(table_keyword, inside_keyword, outside_keyword))

get_url_thread.start()
download_pdf_thread.start()
# download_pdf_thread2.start()
parase_pdf_thread.start()
parase_pdf_thread2.start()
parase_pdf_thread3.start()

get_url_thread.join()
download_pdf_thread.join()
# download_pdf_thread2.join()
parase_pdf_thread.join()
parase_pdf_thread2.join()
parase_pdf_thread3.join()
