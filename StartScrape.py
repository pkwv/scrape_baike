# -*- coding:utf8 -*- 

from ScrapeBaike import ScrapeBaike 
from ScrapeProxy import ScrapeProxy
import time
import threading

URL_START = 1000000
URL_END = 2000001
THREAD_NUM = 50

def print_time():
    print time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))

def main():
#    scr_p = ScrapeProxy('Scrape Proxy',100 ,30)
#    scr_p.start()
#    time.sleep(20)

    st = URL_START
    ed = URL_END
    thread_num = THREAD_NUM
    num = (ed - st) / thread_num
    i = 0
    j = st
    thread_l=[]
    while i<thread_num:
        thread_l.append(ScrapeBaike('scraper_'+str(i), j, j+num))
        j += num
        i += 1
    for k in thread_l:
        k.start()
    while threading.activeCount()>1:
        print_time()
        for k in thread_l:
            k.print_success_error()
        time.sleep(100)
    for k in thread_l:
        k.join();
    for k in thread_l:
        k.print_msg(str(k.success) + '  error: ' + str(k.error))


if __name__ == '__main__':
    main()
