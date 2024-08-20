from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class File(Base):
    __tablename__ = 'Files'
    file_id = Column(String(255), primary_key=True)
    abstract = Column(Text)
    full_text = Column(Text)
    keywords = relationship("Keyword", back_populates="file")

class Keyword(Base):
    __tablename__ = 'Keywords'
    keyword_id = Column(Integer, primary_key=True)
    file_id = Column(String(255), ForeignKey('Files.file_id'))
    order = Column(Integer, name="Order")
    file = relationship("File", back_populates="keywords")
