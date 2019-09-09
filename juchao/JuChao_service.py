import csv
import logging
import math
import os
import threading
import time
from queue import Queue

import requests

from juchao.PdfCaibao import PdfCaibao


def InitLogger(log_name):
    logger = logging.getLogger()
    logger.setLevel(logging.WARNING)
    # rq = time.strftime('%Y%m%d%H%M', time.localtime(time.time()))
    # log_name = OUT_DIR + '/log_wyk.log'
    logfile = log_name
    fh = logging.FileHandler(logfile, mode='w')
    fh.setLevel(logging.WARNING)
    formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    return logger

def standardize_dir(dir_str):
    assert (os.path.exists(dir_str)), 'Such directory \"' + str(dir_str) + '\" does not exists!'
    if dir_str[len(dir_str) - 1] != '/':
        return dir_str + '/'
    else:
        return dir_str

error_log = "./error.log"
def __log_error(err_msg):
    err_msg = str(err_msg)
    print(err_msg)
    with open(error_log, 'a', encoding='gb18030') as err_writer:
        err_writer.write(err_msg + '\n')


def __filter_illegal_filename(filename):
    illegal_char = {
        ' ': '',
        '*': '',
        '/': '-',
        '\\': '-',
        ':': '-',
        '?': '-',
        '"': '',
        '<': '',
        '>': '',
        '|': '',
        '－': '-',
        '—': '-',
        '（': '(',
        '）': ')',
        'Ａ': 'A',
        'Ｂ': 'B',
        'Ｈ': 'H',
        '，': ',',
        '。': '.',
        '：': '-',
        '！': '_',
        '？': '-',
        '“': '"',
        '”': '"',
        '‘': '',
        '’': ''
    }
    for item in illegal_char.items():
        filename = filename.replace(item[0], item[1])
    return filename


URL = 'http://www.cninfo.com.cn/new/hisAnnouncement/query'
HEADER = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest'
}

# 
class PdfHandler():
    def __init__(self):
        self.rLock3 = threading.RLock()

    def handle(self, path):
        pass

# 从巨潮站获取pdf... 
class JuChao_service():

    # 板块类型：沪市：shmb；深市：szse；深主板：szmb；中小板：szzx；创业板：szcy；
    # @PLATE
    # 公告类型：category_scgkfx_szsh（首次公开发行及上市）、category_ndbg_szsh（年度报告）、category_bndbg_szsh（半年度报告）
    # @CATEGORY
    def __init__(self, pdfHandler, logger, PLATE = 'szzx;', CATEGORY='category_bndbg_szsh;'):
        self.pdfHandler = pdfHandler
        self.logger = logger or InitLogger("log_juchao.log")
        self.rLock = threading.RLock()
        self.rLock2 = threading.RLock()
        # self.OUT_DIR="./temp"
        self.out_dir = standardize_dir("./temp")
        # error_log = self.out_dir + 'error.log'

        self.url_list=Queue()
        self.pdffile_list=Queue()

        self.OUTPUT_FILENAME = 'report'
        self.PLATE = PLATE
        self.CATEGORY = CATEGORY

        self.MAX_PAGESIZE = 50
        self.MAX_RELOAD_TIMES = 5
        self.RESPONSE_TIMEOUT = 10


    def get_response(self,page_num,stack_code,return_total_count=False,START_DATE = '2013-01-01',END_DATE = '2018-01-01'):
        global __filter_illegal_filename

        query = {
            'stock': stack_code,
            'searchkey': '',
            'plate': '',
            'category': self.CATEGORY,
            'trade': '',
            'column': '', #注意沪市为sse
    #        'columnTitle': '历史公告查询',
            'pageNum': page_num,
            'pageSize': self.MAX_PAGESIZE,
            'tabName': 'fulltext',
            'sortName': '',
            'sortType': '',
            'limit': '',
            'showTitle': '',
            'seDate': START_DATE + '~' + END_DATE,
        }
        result_list = []
        #reloading = 0
        while True:
    #        reloading += 1
    #        if reloading > self.MAX_RELOAD_TIMES:
    #            return []
    #        elif reloading > 1:
    #            __sleeping(random.randint(5, 10))
    #            print('... reloading: the ' + str(reloading) + ' round ...')
            try:
                r = requests.post(URL, query, HEADER, timeout=self.RESPONSE_TIMEOUT)
            except Exception as e:
                print(e)
                continue
            if r.status_code == requests.codes.ok and r.text != '':
                break
        my_query = r.json()
        try:
            r.close()
        except Exception as e:
            print(e)
        if return_total_count:
            return my_query['totalRecordNum']
        else:
            for each in my_query['announcements']:
                file_link = 'http://static.cninfo.com.cn/' + str(each['adjunctUrl'])
                file_name = __filter_illegal_filename(
                    str(each['secCode']) + str(each['secName']) + str(each['announcementTitle']) + '.'  + '(' + str(each['adjunctSize'])  + 'k)' +
                    file_link[-file_link[::-1].find('.') - 1:]  # 最后一项是获取文件类型后缀名
                )
                if file_name.endswith('.PDF') or file_name.endswith('.pdf'):
                    if '取消' not in file_name and '摘要' not in file_name and '年度' in file_name and\
                    '更正' not in file_name and '英文' not in file_name and '补充' not in file_name:
                        result_list.append([file_name, file_link])
                        self.rLock.acquire()
                        self.url_list.put([file_name, file_link])
                        self.rLock.release()
            return result_list


    # 取得财报url:
    # @START_DATE
    # @END_DATE
    def get_url(self, stack_code_set, START_DATE, END_DATE):
        global __log_error
        START_DATE = START_DATE + '-01-01'
        END_DATE = END_DATE + '-01-01'
        # 初始化重要变量
        output_csv_file = self.out_dir + self.OUTPUT_FILENAME.replace('/', '') + '_' + \
                        START_DATE.replace('-', '') + '-' + END_DATE.replace('-', '') + '.csv'
        # with open(output_csv_file, 'w', newline='', encoding='gb18030') as csv_out:
        csv_out = open(output_csv_file, 'w', newline='', encoding='gb18030')
        writer = csv.writer(csv_out)

        start = time.time()

        for stack_code in stack_code_set:
            # 获取记录数、页数
            item_count = self.get_response(1, stack_code, True, START_DATE=START_DATE, END_DATE=END_DATE)
            assert (item_count != []), 'Please restart this script!'
            begin_pg = 1
            end_pg = int(math.ceil(item_count / self.MAX_PAGESIZE))
            print('Page count: ' + str(end_pg) + '; item count: ' + str(item_count) + '.')
            time.sleep(2)

            # 逐页抓取
            # with open(output_csv_file, 'w', newline='', encoding='gb18030') as csv_out:
            # writer = csv.writer(csv_out)
            for i in range(begin_pg, end_pg + 1):
                row = self.get_response(i, stack_code, START_DATE=START_DATE, END_DATE=END_DATE)
                if not row:
                    __log_error('Failed to fetch page #' + str(i) +
                                ': exceeding max reloading times (' + str(self.MAX_RELOAD_TIMES) + ').')
                    continue
                else:
                    writer.writerows(row)
                    last_item = i * self.MAX_PAGESIZE if i < end_pg else item_count
                    print('Page ' + str(i) + '/' + str(end_pg) + ' fetched, it contains items: (' +
                        str(1 + (i - 1) * self.MAX_PAGESIZE) + '-' + str(last_item) + ')/' + str(item_count) + '.')
        csv_out.close()

        end = time.time()

        print('********time to open processing all files are {}*********'.format((end - start)))

        return output_csv_file


    def download_pdf(self, path, MAX_COUNT=5):

        print('get in download')
        print(self.url_list.qsize())
        DST_DIR = path
        assert (os.path.exists(DST_DIR)), 'No such destination directory \"' + DST_DIR + '\"!'
        if DST_DIR[len(DST_DIR) - 1] != '/':
            DST_DIR += '/'
        # 读取待下载文件列表
        print("run here")

        while True:
            self.rLock.acquire()  # 在此处加锁后，必须有对应的解锁，下面加一个else防止死锁
            if not self.url_list.empty():
                # self.rLock.acquire()
                each = self.url_list.get()
                print('get')
                self.rLock.release()
                download_count = 1
                download_token = False
                while download_count <= MAX_COUNT:
                    try:
                        download_count += 1
                        r = requests.get(each[1])
                        download_token = True
                        break
                    except:
                        # 下载失败则报错误
                        self.logger.error('Failed to download file', exc_info=True)
                        now_thread = threading.current_thread()
                        self.logger.warning(now_thread.getName() + str(now_thread.isAlive()))
                        print(str(each[0] + 1) + '::' + str(download_count) + ':\"' + '\" failed!')
                        download_token = False
                        time.sleep(3)  # 防止频繁访问网站被当做攻击关闭连接
                if download_token:
                    # 下载成功则保存
                    with open(DST_DIR + each[0], 'wb') as file:
                        file.write(r.content)
                        r.close()
                        time.sleep(3)
                        print(each[0] + '\" downloaded.')
                        self.rLock2.acquire()
                        self.pdffile_list.put(DST_DIR + each[0])
                        print('write pdf address ')
                        self.rLock2.release()
                else:
                    # 彻底下载失败则记录日志
                    with open(DST_DIR + 'error.log', 'a') as log_file:
                        log_file.write(
                            time.strftime('[%Y/%m/%d %H:%M:%S] ', time.localtime(time.time())) + 'Failed to download\"' +
                            each[0] + '\"\n')
                        print('...' + each[0] + '\" finally failed ...')
            else:
                self.rLock.release()

    # ,table_keyword, inside_keyword, outside_keyword
    def parase_pdf(self):
        while True:
            try:
                path = None
                self.rLock2.acquire()
                if not self.pdffile_list.empty():
                    # self.rLock2.acquire()
                    print('get pdf address')
                    path = self.pdffile_list.get()
                self.rLock2.release()
                if path :
                    self.pdfHandler.handle(path)
                    #_parse_pdf_imp(path, table_keyword, inside_keyword, outside_keyword)

            except:
                print('*****some thing error happend******')
        # return name_find, value_find, page_find  # 一定不要把return放到while里面，遇到return会立即结束


# 
class JuChaoServiceTask():
    def __init__(self, juchao_service, stack_code_set, START_DATE, END_DATE): 

        get_url_thread = threading.Thread(target=juchao_service.get_url, args=(stack_code_set, START_DATE, END_DATE))
        download_pdf_thread = threading.Thread(target=juchao_service.download_pdf, args=(stack_code_set, START_DATE, END_DATE))
        # download_pdf_thread2 = threading.Thread(target=download_pdf, args=(OUT_DIR,))
        parase_pdf_thread = threading.Thread(target=juchao_service.parase_pdf)
        parase_pdf_thread2 = threading.Thread(target=juchao_service.parase_pdf)
        parase_pdf_thread3 = threading.Thread(target=juchao_service.parase_pdf)

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


# 财报处理...'主要会计数据和财务指标'
class PdfHandler_caiwuzhibiao(PdfHandler):
    def __init__(self):
        pass

    def handle(self, path):
        pdfcb = PdfCaibao()
        pdfcb.parse_pdf(path)
        # 上传到数据库
        # insert_db()

if __name__ == '__main__':
    path = "G:/_Stock/temp/000007全新好2016年半年度报告.(2181k).PDF"
    cwzb = PdfHandler_caiwuzhibiao()
    cwzb.handle(path)

    jcs = JuChao_service(cwzb, None)

    stack_code_set = ['603118', '000002']  # just for test using
    # task = JuChaoServiceTask(jcs, stack_code_set, '2017', '2019')

    #jcs.parase_pdf()
    # _parse_pdf_imp(path, table_keyword, inside_keyword, outside_keyword,0)