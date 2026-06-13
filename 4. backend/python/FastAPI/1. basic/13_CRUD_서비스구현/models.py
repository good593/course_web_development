from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from database import Base


class Category(Base):
    __tablename__ = "categories"

    id          = Column(Integer, primary_key=True, index=True)
    name        = Column(String(100), unique=True, nullable=False)
    description = Column(String(500))

    posts = relationship("Post", back_populates="category")


class Post(Base):
    __tablename__ = "posts"

    id          = Column(Integer, primary_key=True, index=True)
    title       = Column(String(200), nullable=False, index=True)
    content     = Column(Text, nullable=False)
    summary     = Column(String(500))
    published   = Column(Boolean, default=False, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    created_at  = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at  = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    category = relationship("Category", back_populates="posts")
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")


class Comment(Base):
    __tablename__ = "comments"

    id         = Column(Integer, primary_key=True, index=True)
    content    = Column(Text, nullable=False)
    author     = Column(String(100), nullable=False)
    post_id    = Column(Integer, ForeignKey("posts.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    post = relationship("Post", back_populates="comments")
