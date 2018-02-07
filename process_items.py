# -*- coding: UTF-8 -*-

"""A script to process items from a redis queue."""
from __future__ import print_function, unicode_literals

import argparse
import json
import logging
import pprint
import sys
import time
from caogen.model.config import DBSession
from caogen.model.models import ArticleDetail
import datetime

reload(sys)
sys.setdefaultencoding('utf8')
logger = logging.getLogger(__name__)
from scrapy_redis import get_redis


# 初始化数据库操作
session = DBSession()


def process_items(r, keys, timeout, limit=0, log_every=1000, wait=.1):
    """Process items from a redis queue.

    Parameters
    ----------
    r : Redis
        Redis connection instance.
    keys : list
        List of keys to read the items from.
    timeout: int
        Read timeout.

    """
    limit = limit or float('inf')
    processed = 0
    while processed < limit:
        # Change ``blpop`` to ``brpop`` to process as LIFO.
        ret = r.blpop(keys, timeout)
        # If data is found before the timeout then we consider we are done.
        if ret is None:
            time.sleep(wait)
            continue

        source, data = ret
        try:
            item = json.loads(data)
        except Exception:
            logger.exception("Failed to load item:\n%r", pprint.pformat(data))
            continue

        try:
            """
            处理item
            """
            process_item(item)
            # logger.debug("[%s] Processing item: %s <%s>", source, str(title), str(image_path))
            logger.debug("[%s] Processing item", source)
        except KeyError:
            logger.exception("[%s] Failed to process item:\n%r",
                             source, pprint.pformat(item))
            continue

        processed += 1
        if processed % log_every == 0:
            logger.info("Processed %s items", processed)


def process_item(item):
    """
    处理传过来的item
    :param self:
    :param item:
    :return:
    """
    # 将item做相应的处理
    process_article(item)


def process_article(item):
    """
    将文章存入数据库
    :param item:
    :return:
    """
    try:
        a = ArticleDetail(title=item["title"],
                          author=item['author'],
                          pubtime=item["pubtime"],
                          content=deal_content(item["content"]),
                          create_date=get_current_time())
        session.merge(a)
        session.commit()
        return item
    except Exception as e:
        session.rollback()
        logger.error(u"保存文章%s 出错 " % item['title'] + e.message)


def get_current_time():
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return current_time


def deal_content(content):
    content = content.replace("\n", '')
    content = content.replace(' ', '')
    ontent = content.replace("\t", '')
    return content


def main():
    """
    主函数
    :return:
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('key', help="Redis key where items are stored")
    parser.add_argument('--host')
    parser.add_argument('--port')
    parser.add_argument('--timeout', type=int, default=5)
    parser.add_argument('--limit', type=int, default=0)
    parser.add_argument('--progress-every', type=int, default=100)
    parser.add_argument('-v', '--verbose', action='store_true')

    args = parser.parse_args()

    params = {}
    if args.host:
        params['host'] = args.host
    if args.port:
        params['port'] = args.port

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    r = get_redis(**params)
    host = r.connection_pool.get_connection('info').host
    logger.info("Waiting for items in '%s' (server: %s)", args.key, host)
    kwargs = {
        'keys': [args.key],
        'timeout': args.timeout,
        'limit': args.limit,
        'log_every': args.progress_every,
    }
    try:
        process_items(r, **kwargs)
        retcode = 0  # ok
    except KeyboardInterrupt:
        retcode = 0  # ok
    except Exception:
        logger.exception("Unhandled exception")
        retcode = 2

    return retcode


if __name__ == '__main__':
    # python process_items.py (key_name):items -v
    sys.exit(main())
