from sqlalchemy import Column, String, Text
from core.database import Base

class CacheItem(Base):
    __tablename__ = "cache_items"

    key = Column(String, primary_key=True, index=True)
    value = Column(Text)