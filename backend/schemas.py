from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
import re

# Base schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = Field(None, max_length=100)

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)
    
    @validator('password')
    def validate_password(cls, v):
        if not re.search(r"[A-Za-z]", v):
            raise ValueError('Password must contain at least one letter')
        if not re.search(r"\d", v):
            raise ValueError('Password must contain at least one digit')
        return v
    
    @validator('username')
    def validate_username(cls, v):
        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError('Username can only contain letters, numbers, hyphens, and underscores')
        return v

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    full_name: Optional[str] = Field(None, max_length=100)
    bio: Optional[str] = Field(None, max_length=500)
    avatar_url: Optional[str] = None

class UserResponse(UserBase):
    id: str
    is_active: bool
    is_verified: bool
    avatar_url: Optional[str]
    bio: Optional[str]
    subscription_plan: str
    subscription_status: str
    created_at: datetime
    last_login: Optional[datetime]

    class Config:
        from_attributes = True

# Authentication schemas
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class TokenData(BaseModel):
    user_id: Optional[str] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class PasswordReset(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8, max_length=100)

# Website schemas
class WebsiteBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    template_id: Optional[str] = None

class WebsiteCreate(WebsiteBase):
    pass

class WebsiteUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    content: Optional[Dict[str, Any]] = None
    settings: Optional[Dict[str, Any]] = None
    custom_css: Optional[str] = None
    custom_js: Optional[str] = None
    meta_title: Optional[str] = Field(None, max_length=60)
    meta_description: Optional[str] = Field(None, max_length=160)
    meta_keywords: Optional[str] = Field(None, max_length=200)
    is_public: Optional[bool] = None
    domain: Optional[str] = None

class WebsiteResponse(WebsiteBase):
    id: str
    slug: str
    template_id: Optional[str]
    content: Optional[Dict[str, Any]]
    settings: Optional[Dict[str, Any]]
    status: str
    is_public: bool
    domain: Optional[str]
    
    # Hébergement intégré
    is_hosted: bool
    hosting_subdomain: Optional[str]
    hosting_url: Optional[str]
    ssl_enabled: bool
    deployed_at: Optional[datetime]
    
    meta_title: Optional[str]
    meta_description: Optional[str]
    view_count: int
    owner_id: str
    created_at: datetime
    updated_at: datetime
    last_published: Optional[datetime]

    class Config:
        from_attributes = True

class WebsitePublicResponse(BaseModel):
    """Public view of website (without sensitive data)"""
    id: str
    name: str
    slug: str
    description: Optional[str]
    content: Optional[Dict[str, Any]]
    settings: Optional[Dict[str, Any]]
    meta_title: Optional[str]
    meta_description: Optional[str]
    view_count: int
    last_published: Optional[datetime]

    class Config:
        from_attributes = True

# Template schemas
class TemplateBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    category: str = Field(..., pattern="^(portfolio|business|blog|ecommerce|landing)$")

class TemplateCreate(TemplateBase):
    structure: Dict[str, Any]
    default_content: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    is_premium: bool = False
    price: int = Field(0, ge=0)  # Price in cents

class TemplateUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    structure: Optional[Dict[str, Any]] = None
    default_content: Optional[Dict[str, Any]] = None
    preview_image: Optional[str] = None
    tags: Optional[List[str]] = None
    is_premium: Optional[bool] = None
    price: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None
    is_featured: Optional[bool] = None

class TemplateResponse(TemplateBase):
    id: str
    slug: str
    structure: Dict[str, Any]
    default_content: Optional[Dict[str, Any]]
    preview_image: Optional[str]
    is_premium: bool
    price: int
    tags: Optional[List[str]]
    usage_count: int
    rating_avg: int
    rating_count: int
    is_active: bool
    is_featured: bool
    creator_id: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

# Generation schemas (for Phase 2)
class GenerateContentRequest(BaseModel):
    type: str = Field(..., pattern="^(text|image|design|seo)$")
    prompt: str = Field(..., min_length=1, max_length=1000)
    website_id: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None

class GenerateContentResponse(BaseModel):
    generation_id: str
    type: str
    result: Dict[str, Any]
    ai_service: str
    model_used: Optional[str]
    tokens_used: Optional[int]
    created_at: datetime

# Utility schemas
class MessageResponse(BaseModel):
    message: str
    success: bool = True

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    success: bool = False

# Pagination
class PaginationParams(BaseModel):
    page: int = Field(1, ge=1)
    size: int = Field(10, ge=1, le=100)

class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    size: int
    pages: int

    @classmethod
    def create(cls, items: List[Any], total: int, page: int, size: int):
        return cls(
            items=items,
            total=total,
            page=page,
            size=size,
            pages=(total + size - 1) // size  # Ceiling division
        )