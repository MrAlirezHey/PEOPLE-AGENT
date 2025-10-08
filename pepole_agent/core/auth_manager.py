from sqlalchemy import create_engine, Column, Integer, String, Text, JSON ,DateTime ,UUID ,ForeignKey,Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker ,relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB
import uuid 
from dotenv import load_dotenv
import os
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(project_root, '.env')
load_dotenv(dotenv_path=env_path)
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found in .env file or environment variables.")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
class Profile(Base):
    __tablename__ = "profiles"
    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    profile_data = Column(JSONB, nullable=False, server_default='{}')
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    messages = relationship("eval_messages", back_populates="user")
class chat_messages(Base):
    __tablename__ = "chat_messages"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("profiles.user_id"), nullable=False, index=True)
    sender = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
class eval_messages(Base):
    __tablename__ = "eval_messages"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("profiles.user_id"), nullable=False, index=True)
    summary = Column(Text, nullable=True)
    score = Column(Float, nullable=True)
    score_reason = Column(Text, nullable=True)
    github_link = Column(String, nullable=True)
    linkedin_link = Column(String, nullable=True)
    field_of_interest = Column(String, nullable=True)
    issues_and_strengths=Column(String, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    user = relationship("Profile", back_populates="messages")