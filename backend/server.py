from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from typing import List, Dict, Any
import os
from dotenv import load_dotenv

# Import local modules
from database import get_db, init_db
from models import User, Website, Template
from schemas import (
    UserCreate, UserResponse, UserUpdate, LoginRequest, Token,
    WebsiteCreate, WebsiteResponse, WebsiteUpdate,
    TemplateCreate, TemplateResponse, TemplateUpdate,
    MessageResponse, ErrorResponse, PaginatedResponse
)
from auth import (
    authenticate_user, create_access_token, create_user, 
    get_current_active_user, ACCESS_TOKEN_EXPIRE_MINUTES
)
from website_exporter import WebsiteExporter
from hosting_manager import HostingManager

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title=os.getenv("PROJECT_NAME", "AI Website Generator"),
    description="API pour générateur de sites web avec IA - Phase 1 MVP",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS middleware
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    print("🚀 Starting AI Website Generator API...")
    init_db()
    print("✅ Database initialized")
    print("🌟 Server ready!")

# Health check
@app.get("/api/health", response_model=MessageResponse)
async def health_check():
    return MessageResponse(message="API is healthy and running!")

# Root endpoint
@app.get("/api", response_model=MessageResponse)
async def root():
    return MessageResponse(message="AI Website Generator API - Phase 1 MVP")

# === AUTHENTICATION ENDPOINTS ===

@app.post("/api/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    try:
        user = create_user(db, user_data)
        return UserResponse.from_orm(user)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )

@app.post("/api/auth/login", response_model=Token)
async def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """Login user and return JWT token"""
    user = authenticate_user(db, login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id}, expires_delta=access_token_expires
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

@app.get("/api/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """Get current user information"""
    return UserResponse.from_orm(current_user)

@app.put("/api/auth/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update current user information"""
    for field, value in user_update.dict(exclude_unset=True).items():
        setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    return UserResponse.from_orm(current_user)

# === WEBSITE ENDPOINTS ===

@app.post("/api/websites", response_model=WebsiteResponse, status_code=status.HTTP_201_CREATED)
async def create_website(
    website_data: WebsiteCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new website"""
    # Generate unique slug
    from slugify import slugify
    import uuid
    
    base_slug = slugify(website_data.name)
    slug = base_slug
    counter = 1
    
    while db.query(Website).filter(Website.slug == slug).first():
        slug = f"{base_slug}-{counter}"
        counter += 1
    
    website = Website(
        name=website_data.name,
        slug=slug,
        description=website_data.description,
        template_id=website_data.template_id,
        owner_id=current_user.id
    )
    
    db.add(website)
    db.commit()
    db.refresh(website)
    
    return WebsiteResponse.from_orm(website)

@app.get("/api/websites", response_model=PaginatedResponse)
async def get_user_websites(
    page: int = 1,
    size: int = 10,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current user's websites"""
    offset = (page - 1) * size
    
    websites_query = db.query(Website).filter(Website.owner_id == current_user.id)
    total = websites_query.count()
    websites = websites_query.offset(offset).limit(size).all()
    
    return PaginatedResponse.create(
        items=[WebsiteResponse.from_orm(w) for w in websites],
        total=total,
        page=page,
        size=size
    )

@app.get("/api/websites/{website_id}", response_model=WebsiteResponse)
async def get_website(
    website_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific website"""
    website = db.query(Website).filter(
        Website.id == website_id,
        Website.owner_id == current_user.id
    ).first()
    
    if not website:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Website not found"
        )
    
    return WebsiteResponse.from_orm(website)

@app.put("/api/websites/{website_id}", response_model=WebsiteResponse)
async def update_website(
    website_id: str,
    website_update: WebsiteUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a website"""
    website = db.query(Website).filter(
        Website.id == website_id,
        Website.owner_id == current_user.id
    ).first()
    
    if not website:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Website not found"
        )
    
    for field, value in website_update.dict(exclude_unset=True).items():
        setattr(website, field, value)
    
    db.commit()
    db.refresh(website)
    
    return WebsiteResponse.from_orm(website)

@app.delete("/api/websites/{website_id}", response_model=MessageResponse)
async def delete_website(
    website_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a website"""
    website = db.query(Website).filter(
        Website.id == website_id,
        Website.owner_id == current_user.id
    ).first()
    
    if not website:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Website not found"
        )
    
    db.delete(website)
    db.commit()
    
    return MessageResponse(message="Website deleted successfully")

# === TEMPLATE ENDPOINTS ===

@app.get("/api/templates", response_model=PaginatedResponse)
async def get_templates(
    page: int = 1,
    size: int = 20,
    category: str = None,
    db: Session = Depends(get_db)
):
    """Get available templates"""
    offset = (page - 1) * size
    
    templates_query = db.query(Template).filter(Template.is_active == True)
    
    if category:
        templates_query = templates_query.filter(Template.category == category)
    
    total = templates_query.count()
    templates = templates_query.offset(offset).limit(size).all()
    
    return PaginatedResponse.create(
        items=[TemplateResponse.from_orm(t) for t in templates],
        total=total,
        page=page,
        size=size
    )

@app.get("/api/templates/{template_id}", response_model=TemplateResponse)
async def get_template(template_id: str, db: Session = Depends(get_db)):
    """Get a specific template"""
    template = db.query(Template).filter(
        Template.id == template_id,
        Template.is_active == True
    ).first()
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    return TemplateResponse.from_orm(template)

# === GENERATOR ENDPOINTS (MVP version) ===

@app.post("/api/generate/website", response_model=WebsiteResponse, status_code=status.HTTP_201_CREATED)
async def generate_website_quick(
    template_id: str,
    website_name: str,
    website_description: str = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Quick website generation (MVP version)"""
    # Verify template exists
    template = db.query(Template).filter(
        Template.id == template_id,
        Template.is_active == True
    ).first()
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    # Generate unique slug
    from slugify import slugify
    base_slug = slugify(website_name)
    slug = base_slug
    counter = 1
    
    while db.query(Website).filter(Website.slug == slug).first():
        slug = f"{base_slug}-{counter}"
        counter += 1
    
    # Create website with template default content
    website = Website(
        name=website_name,
        slug=slug,
        description=website_description,
        template_id=template_id,
        content=template.default_content,
        settings={"generated": True, "template_name": template.name},
        owner_id=current_user.id,
        status="draft"
    )
    
    db.add(website)
    
    # Update template usage count
    template.usage_count += 1
    
    db.commit()
    db.refresh(website)
    
    return WebsiteResponse.from_orm(website)

# === EXPORT ENDPOINTS ===

@app.get("/api/websites/{website_id}/export")
async def export_website(
    website_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Export website as downloadable ZIP file with HTML/CSS/JS"""
    
    # Get website data
    website = db.query(Website).filter(
        Website.id == website_id,
        Website.owner_id == current_user.id
    ).first()
    
    if not website:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Website not found"
        )
    
    # Get template data if available
    template_data = None
    if website.template_id:
        template = db.query(Template).filter(Template.id == website.template_id).first()
        if template:
            template_data = {
                'id': template.id,
                'name': template.name,
                'category': template.category,
                'structure': template.structure,
                'default_content': template.default_content
            }
    
    # Prepare website data for export
    website_data = {
        'id': website.id,
        'name': website.name,
        'slug': website.slug,
        'description': website.description,
        'content': website.content or {},
        'settings': website.settings or {},
        'custom_css': website.custom_css or '',
        'custom_js': website.custom_js or '',
        'meta_title': website.meta_title,
        'meta_description': website.meta_description,
        'meta_keywords': website.meta_keywords,
        'status': website.status,
        'created_at': website.created_at,
        'updated_at': website.updated_at
    }
    
    try:
        # Create exporter and generate ZIP
        exporter = WebsiteExporter()
        zip_buffer = exporter.export_website(website_data, template_data)
        
        # Generate filename
        safe_name = website.slug or website.name.replace(' ', '-').lower()
        filename = f"{safe_name}-export.zip"
        
        # Return as streaming response
        return StreamingResponse(
            iter([zip_buffer.getvalue()]),
            media_type="application/zip",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Length": str(len(zip_buffer.getvalue()))
            }
        )
        
    except Exception as e:
        print(f"Export error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to export website"
        )

# === HOSTING ENDPOINTS (Phase 1) ===

@app.post("/api/websites/{website_id}/deploy", response_model=MessageResponse)
async def deploy_website(
    website_id: str,
    custom_subdomain: str = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Déploie un site web sur l'hébergement intégré"""
    
    # Vérifier que le site appartient à l'utilisateur
    website = db.query(Website).filter(
        Website.id == website_id,
        Website.owner_id == current_user.id
    ).first()
    
    if not website:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Website not found"
        )
    
    # Récupérer les données du template si disponible
    template_data = None
    if website.template_id:
        template = db.query(Template).filter(Template.id == website.template_id).first()
        if template:
            template_data = {
                'id': template.id,
                'name': template.name,
                'category': template.category,
                'structure': template.structure,
                'default_content': template.default_content
            }
    
    # Préparer les données du site
    website_data = {
        'id': website.id,
        'name': website.name,
        'slug': website.slug,
        'description': website.description,
        'content': website.content or {},
        'settings': website.settings or {},
        'custom_css': website.custom_css or '',
        'custom_js': website.custom_js or '',
        'meta_title': website.meta_title,
        'meta_description': website.meta_description,
        'meta_keywords': website.meta_keywords,
        'owner_id': website.owner_id,
        'status': website.status,
        'created_at': website.created_at,
        'updated_at': website.updated_at
    }
    
    try:
        # Déployer le site
        hosting_manager = HostingManager()
        result = hosting_manager.deploy_website(website_data, template_data, custom_subdomain)
        
        if result['success']:
            # Mettre à jour la base de données
            website.is_hosted = True
            website.hosting_subdomain = result['subdomain']
            website.hosting_url = result['hosting_url']
            website.ssl_enabled = result['ssl_enabled']
            website.deployed_at = datetime.utcnow()
            website.status = "published"
            
            db.commit()
            db.refresh(website)
            
            return MessageResponse(
                message=f"Site déployé avec succès ! Accessible sur {result['hosting_url']}"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Deployment failed: {result.get('error', 'Unknown error')}"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to deploy website: {str(e)}"
        )

@app.delete("/api/websites/{website_id}/undeploy", response_model=MessageResponse)
async def undeploy_website(
    website_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Supprime un site de l'hébergement intégré"""
    
    website = db.query(Website).filter(
        Website.id == website_id,
        Website.owner_id == current_user.id
    ).first()
    
    if not website:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Website not found"
        )
    
    if not website.is_hosted or not website.hosting_subdomain:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Website is not currently hosted"
        )
    
    try:
        hosting_manager = HostingManager()
        result = hosting_manager.undeploy_website(website.hosting_subdomain)
        
        if result['success']:
            # Mettre à jour la base de données
            website.is_hosted = False
            website.hosting_subdomain = None
            website.hosting_url = None
            website.deployed_at = None
            website.status = "draft"
            
            db.commit()
            
            return MessageResponse(message="Site retiré de l'hébergement avec succès")
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Undeployment failed: {result.get('error', 'Unknown error')}"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to undeploy website: {str(e)}"
        )

@app.put("/api/websites/{website_id}/redeploy", response_model=MessageResponse)
async def redeploy_website(
    website_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Redéploie un site web avec les dernières modifications"""
    
    website = db.query(Website).filter(
        Website.id == website_id,
        Website.owner_id == current_user.id
    ).first()
    
    if not website:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Website not found"
        )
    
    if not website.is_hosted or not website.hosting_subdomain:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Website is not currently hosted"
        )
    
    # Récupérer les données du template si disponible
    template_data = None
    if website.template_id:
        template = db.query(Template).filter(Template.id == website.template_id).first()
        if template:
            template_data = {
                'id': template.id,
                'name': template.name,
                'category': template.category,
                'structure': template.structure,
                'default_content': template.default_content
            }
    
    # Préparer les données du site
    website_data = {
        'id': website.id,
        'name': website.name,
        'slug': website.slug,
        'description': website.description,
        'content': website.content or {},
        'settings': website.settings or {},
        'custom_css': website.custom_css or '',
        'custom_js': website.custom_js or '',
        'meta_title': website.meta_title,
        'meta_description': website.meta_description,
        'meta_keywords': website.meta_keywords,
        'owner_id': website.owner_id,
        'status': website.status,
        'created_at': website.created_at,
        'updated_at': website.updated_at
    }
    
    try:
        hosting_manager = HostingManager()
        result = hosting_manager.update_website(website.hosting_subdomain, website_data, template_data)
        
        if result['success']:
            # Mettre à jour la date de déploiement
            website.deployed_at = datetime.utcnow()
            
            db.commit()
            
            return MessageResponse(
                message=f"Site redéployé avec succès ! Accessible sur {website.hosting_url}"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Redeployment failed: {result.get('error', 'Unknown error')}"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to redeploy website: {str(e)}"
        )

@app.post("/api/websites/{website_id}/ssl", response_model=MessageResponse)
async def configure_ssl(
    website_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Configure SSL pour un site hébergé"""
    
    website = db.query(Website).filter(
        Website.id == website_id,
        Website.owner_id == current_user.id
    ).first()
    
    if not website:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Website not found"
        )
    
    if not website.is_hosted or not website.hosting_subdomain:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Website must be hosted to configure SSL"
        )
    
    try:
        hosting_manager = HostingManager()
        result = hosting_manager.setup_ssl_certificate(website.hosting_subdomain)
        
        if result['success']:
            website.ssl_enabled = True
            
            # Mettre à jour l'URL avec HTTPS si SSL activé
            if website.hosting_url and not website.hosting_url.startswith('https://'):
                website.hosting_url = website.hosting_url.replace('http://', 'https://')
            
            db.commit()
            
            return MessageResponse(message="SSL configuré avec succès")
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"SSL configuration failed: {result.get('error', 'Unknown error')}"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to configure SSL: {str(e)}"
        )

@app.get("/api/hosting/sites", response_model=List[Dict[str, Any]])
async def list_hosted_sites(
    current_user: User = Depends(get_current_active_user)
):
    """Liste tous les sites hébergés de l'utilisateur (admin endpoint)"""
    
    # Pour le MVP, on retourne tous les sites hébergés
    # Dans une version production, on filtrerait par utilisateur
    try:
        hosting_manager = HostingManager()
        sites = hosting_manager.list_hosted_sites()
        
        # Filtrer par propriétaire si pas admin
        user_sites = [site for site in sites if site.get('owner_id') == current_user.id]
        
        return user_sites
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list hosted sites: {str(e)}"
        )

# === ERROR HANDLERS ===

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(error=exc.detail).dict()
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal server error",
            detail=str(exc) if os.getenv("DEBUG") == "True" else None
        ).dict()
    )

# Run with: uvicorn server:app --reload --host 0.0.0.0 --port 8001
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )