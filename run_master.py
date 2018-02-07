# -*- coding:utf8 -*-

from scrapy import cmdline
RUN_CMD = "scrapy crawl caogen_master"


def run(cmd):
    cmdline.execute(cmd.split())


if __name__ == '__main__':
    run(RUN_CMD)
