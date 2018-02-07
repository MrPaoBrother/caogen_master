# coding: utf-8
from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class ArticleDetail(Base):
    __tablename__ = 'article_detail'
    id = Column(Integer, primary_key=True)
    title = Column(String(150), default="")
    author = Column(String(50), default="")
    pubtime = Column(DateTime)
    content = Column(Text)
    create_date = Column(DateTime)
