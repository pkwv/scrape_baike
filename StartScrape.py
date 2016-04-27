# -*- coding:utf8 -*- 

from ScrapeBaike import ScrapeBaike 
from ScrapeProxy import ScrapeProxy
import time
import threading
import sys

# default 
URL_START = 8000000
URL_END = 9000000
THREAD_NUM = 20

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
        from_my_ip = 0
        from_proxy = 0
        success = 0
        for k in thread_l:
            k.print_success_error()
            from_my_ip += k.notuse
            from_proxy += k.use
            success += k.success
        print 'use my ip: ' + str(from_my_ip) + ' and ' + str(from_proxy) + ' from proxy'
        print 'there are: ' + str(success) + ' success'
        print 'there are '+ str(threading.activeCount()-1)+' spiders still scraping'
        time.sleep(120)
    for k in thread_l:
        k.join();
    tot = 0
    suc = 0
    err = 0
    for k in thread_l:
        k.print_success_error() #msg(str(k.success) + '  error: ' + str(k.error))
        tot += k.notuse
        suc += k.success
        err += k.error
    print 'use my ip: ' + str(tot)
    print 'total scrape success: '+str(suc)
    print 'error number: ' + str(err)


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print 'you must input 4 parameters\n 0:filename 1:start url 2:end url 3:number of thread'
        sys.exit()
    URL_START = int(sys.argv[1])
    URL_END = int(sys.argv[2])
    THREAD_NUM = int(sys.argv[3])
    st_time=time.time()
    main()
    end_time=time.time()
    print 'total cost time: ' + str(end_time-st_time)
