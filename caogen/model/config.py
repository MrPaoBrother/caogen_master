# -*- coding: utf-8 -*-

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import ConfigParser
import redis

config = ConfigParser.ConfigParser()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 默认使用开发环境
config.read(os.path.join(BASE_DIR, 'caogen_scrapy.ini'))
# 初始化数据库连接:
mysql_conn_info_str = 'mysql+mysqldb://%(user)s:%(password)s@%(host)s:%(port)s/%(db)s?charset=utf8'
mysql_conn_info_dict = {'user': config.get('default', 'user'), 'password': config.get('default', 'password'),
                        'host': config.get('default', 'host'), 'port': config.get('default', 'port'),
                        'db': config.get('default', 'db'),
                        }
engine = create_engine(mysql_conn_info_str % mysql_conn_info_dict,
                       echo=config.getboolean('default', 'echo'))
# 创建DBSession类型:
DBSession = sessionmaker(bind=engine)

# 配置redis
REDIS_CONN = redis.Redis(host=config.get('redis', 'host'), port=config.get('redis', 'port'), decode_responses=True)
