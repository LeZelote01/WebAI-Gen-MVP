from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from database import Base

class User(Base):
    """User model for authentication and user management"""
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # OAuth fields
    google_id = Column(String, unique=True, nullable=True)
    github_id = Column(String, unique=True, nullable=True)
    
    # Profile information
    avatar_url = Column(String, nullable=True)
    bio = Column(Text, nullable=True)
    
    # Subscription info (for future use)
    subscription_plan = Column(String, default="free")  # free, pro, team, enterprise
    subscription_status = Column(String, default="active")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    # Relationships
    websites = relationship("Website", back_populates="owner", cascade="all, delete-orphan")
    templates = relationship("Template", back_populates="creator")

class Website(Base):
    """Website model for generated sites"""
    __tablename__ = "websites"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    
    # Website content and configuration
    template_id = Column(String, ForeignKey("templates.id"), nullable=True)
    content = Column(JSON, nullable=True)  # Stores the website structure/content
    settings = Column(JSON, nullable=True)  # Stores website settings
    custom_css = Column(Text, nullable=True)
    custom_js = Column(Text, nullable=True)
    
    # Status and metadata
    status = Column(String, default="draft")  # draft, published, archived
    is_public = Column(Boolean, default=False)
    domain = Column(String, nullable=True)  # Custom domain if configured
    
    # Hébergement intégré (Phase 1)
    is_hosted = Column(Boolean, default=False)  # Whether the site is hosted on our platform
    hosting_subdomain = Column(String, nullable=True)  # Subdomain for hosted sites (e.g., "mysite")
    hosting_url = Column(String, nullable=True)  # Full URL where the site is accessible
    ssl_enabled = Column(Boolean, default=True)  # SSL certificate status
    deployed_at = Column(DateTime, nullable=True)  # When the site was last deployed
    
    # SEO
    meta_title = Column(String, nullable=True)
    meta_description = Column(Text, nullable=True)
    meta_keywords = Column(String, nullable=True)
    
    # Analytics (basic counters for MVP)
    view_count = Column(Integer, default=0)
    last_published = Column(DateTime, nullable=True)
    
    # Ownership
    owner_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    owner = relationship("User", back_populates="websites")
    template = relationship("Template", back_populates="websites")

class Template(Base):
    """Template model for website templates"""
    __tablename__ = "templates"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String, nullable=False)  # portfolio, business, blog, ecommerce, landing
    
    # Template content and structure
    structure = Column(JSON, nullable=False)  # Template structure definition
    default_content = Column(JSON, nullable=True)  # Default content for the template
    preview_image = Column(String, nullable=True)  # URL to preview image
    
    # Template metadata
    is_premium = Column(Boolean, default=False)
    price = Column(Integer, default=0)  # Price in cents (0 = free)
    tags = Column(JSON, nullable=True)  # Array of tags
    
    # Statistics
    usage_count = Column(Integer, default=0)
    rating_avg = Column(Integer, default=5)  # Average rating out of 5
    rating_count = Column(Integer, default=0)
    
    # Ownership and status
    creator_id = Column(String, ForeignKey("users.id"), nullable=True)  # Null for system templates
    is_active = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    creator = relationship("User", back_populates="templates")
    websites = relationship("Website", back_populates="template")

class APIKey(Base):
    """API Keys for external integrations (Phase 2+)"""
    __tablename__ = "api_keys"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    service = Column(String, nullable=False)  # openai, anthropic, sendgrid, etc.
    key_name = Column(String, nullable=False)  # Display name for the key
    encrypted_key = Column(String, nullable=False)  # Encrypted API key
    is_active = Column(Boolean, default=True)
    
    # Usage tracking
    usage_count = Column(Integer, default=0)
    last_used = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class GenerationHistory(Base):
    """Track AI generation history (Phase 2+)"""
    __tablename__ = "generation_history"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    website_id = Column(String, ForeignKey("websites.id"), nullable=True)
    
    generation_type = Column(String, nullable=False)  # text, image, design, seo
    prompt = Column(Text, nullable=False)
    result = Column(JSON, nullable=True)  # Generated content
    
    # AI Service info
    ai_service = Column(String, nullable=False)  # openai, anthropic, etc.
    model_used = Column(String, nullable=True)
    tokens_used = Column(Integer, nullable=True)
    cost = Column(Integer, nullable=True)  # Cost in cents
    
    # Quality metrics
    user_rating = Column(Integer, nullable=True)  # 1-5 rating by user
    was_used = Column(Boolean, default=False)  # Whether the generation was actually used
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)