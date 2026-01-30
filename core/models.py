from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from core.db import Base
import enum

class ImageStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class SearchTerm(Base):
    __tablename__ = "search_terms"

    id = Column(Integer, primary_key=True, index=True)
    term = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship to images
    images = relationship("Image", back_populates="search_term", cascade="all, delete-orphan")

class Image(Base):
    __tablename__ = "images"
    __table_args__ = (UniqueConstraint('source_id', 'source_api', name='_source_api_uc'),)
    
    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(String, index=True, nullable=False) # ID from the external API (Pexels, Pixabay etc.)
    source_api = Column(String, nullable=False) # 'pexels', 'pixabay', 'unsplash', 'flickr'
    
    url_original = Column(String, nullable=True)
    url_thumbnail = Column(String, nullable=True)
    url_page = Column(String, nullable=True)
    
    file_path = Column(String, nullable=True) # Local path if downloaded
    
    status = Column(String, default=ImageStatus.PENDING.value)
    
    search_term_id = Column(Integer, ForeignKey("search_terms.id"))
    search_term = relationship("SearchTerm", back_populates="images")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
