# -*- coding:utf8 -*-

from ScrapeProxy import ScrapeProxy
import threading
import time


def main():
    scrapeproxy = ScrapeProxy('scrape proxy', 300, 100)
    scrapeproxy.start()
    print 'lalal'

#print __name__

if __name__ == '__main__':
    main()
