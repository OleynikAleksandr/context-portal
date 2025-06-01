from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func # For server_default=func.now()
from datetime import datetime # Missing import

Base = declarative_base()

class ProductContextORM(Base):
    __tablename__ = "product_context"
    id = Column(Integer, primary_key=True, default=1) # Assuming single row
    content = Column(JSON, nullable=False, default=lambda: {})
    # last_updated = Column(DateTime, server_default=func.now(), onupdate=func.now()) # Example

class ActiveContextORM(Base):
    __tablename__ = "active_context"
    id = Column(Integer, primary_key=True, default=1) # Assuming single row
    content = Column(JSON, nullable=False, default=lambda: {})
    # last_updated = Column(DateTime, server_default=func.now(), onupdate=func.now())

# TODO: Add other ORM models here corresponding to Pydantic models and DB schema
# (Decision, ProgressEntry, SystemPattern, CustomData, ContextLink, history tables, etc.)

# Example for Decision to show a more complex model
class DecisionORM(Base):
    __tablename__ = "decisions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    summary = Column(Text, nullable=False)
    rationale = Column(Text)
    implementation_details = Column(Text)
    tags = Column(JSON) # Storing list of strings as JSON

    def __repr__(self):
        return f"<Decision(id={self.id}, summary='{self.summary[:30]}...')>"

# Alembic needs to be able to import 'Base' and see all models that inherit from it.