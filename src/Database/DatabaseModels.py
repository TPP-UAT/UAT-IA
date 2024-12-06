from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class FileModel(Base):
    __tablename__ = 'files'
    file_id = Column(String(255), primary_key=True)
    abstract = Column(Text)
    full_text = Column(Text)
    summarized_text = Column(Text)
    keywords = relationship("KeywordModel", back_populates="file")

class KeywordModel(Base):
    __tablename__ = 'keywords'
    keyword_id = Column(Integer, primary_key=True)
    file_id = Column(String(255), ForeignKey('files.file_id'))
    order = Column(Integer, name="order")
    file = relationship("FileModel", back_populates="keywords")
