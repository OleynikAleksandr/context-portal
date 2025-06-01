from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func # For server_default=func.now()
from datetime import datetime

Base = declarative_base()

class ProductContextORM(Base):
    __tablename__ = "product_context"
    id = Column(Integer, primary_key=True, index=True, default=1) # Assuming single row
    content = Column(JSON, nullable=False, default=lambda: {})
    history = relationship("ProductContextHistoryORM", back_populates="product_context")


class ActiveContextORM(Base):
    __tablename__ = "active_context"
    id = Column(Integer, primary_key=True, index=True, default=1) # Assuming single row
    content = Column(JSON, nullable=False, default=lambda: {})
    history = relationship("ActiveContextHistoryORM", back_populates="active_context")


class DecisionORM(Base):
    __tablename__ = "decisions"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    summary = Column(Text, nullable=False)
    rationale = Column(Text)
    implementation_details = Column(Text)
    tags = Column(JSON) # Storing list of strings as JSON

    def __repr__(self):
        return f"<Decision(id={self.id}, summary='{self.summary[:30]}...')>"

class ProgressEntryORM(Base):
    __tablename__ = "progress_entries"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    status = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    parent_id = Column(Integer, ForeignKey('progress_entries.id'), nullable=True)
    # Relationships for parent/child tasks
    parent = relationship("ProgressEntryORM", remote_side=[id], back_populates="children")
    children = relationship("ProgressEntryORM", back_populates="parent")


class SystemPatternORM(Base):
    __tablename__ = "system_patterns"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    name = Column(String, nullable=False, unique=True)
    description = Column(Text)
    tags = Column(JSON)


class CustomDataORM(Base):
    __tablename__ = "custom_data"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    category = Column(String, nullable=False, index=True)
    key = Column(String, nullable=False, index=True)
    value = Column(JSON, nullable=False)
    __table_args__ = (UniqueConstraint('category', 'key', name='uq_custom_data_category_key'),)


class ProductContextHistoryORM(Base):
    __tablename__ = "product_context_history"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    product_context_id = Column(Integer, ForeignKey("product_context.id", ondelete="CASCADE"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    version = Column(Integer, nullable=False)
    content = Column(JSON, nullable=False)
    change_source = Column(String)
    product_context = relationship("ProductContextORM", back_populates="history")


class ActiveContextHistoryORM(Base):
    __tablename__ = "active_context_history"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    active_context_id = Column(Integer, ForeignKey("active_context.id", ondelete="CASCADE"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    version = Column(Integer, nullable=False)
    content = Column(JSON, nullable=False)
    change_source = Column(String)
    active_context = relationship("ActiveContextORM", back_populates="history")


class ContextLinkORM(Base):
    __tablename__ = "context_links"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    source_item_type = Column(String, nullable=False, index=True)
    source_item_id = Column(String, nullable=False, index=True) # String to accommodate various ID types
    target_item_type = Column(String, nullable=False, index=True)
    target_item_id = Column(String, nullable=False, index=True) # String to accommodate various ID types
    relationship_type = Column(String, nullable=False, index=True)
    description = Column(Text)

# Alembic needs to be able to import 'Base' and see all models that inherit from it.
# Ensure all models are defined above this line or imported if defined elsewhere.