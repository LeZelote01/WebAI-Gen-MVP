#!/usr/bin/env python3
"""
Script pour initialiser la base de données avec des templates de base
"""
import json
from sqlalchemy.orm import Session
from database import SessionLocal, init_db
from models import Template

def create_sample_templates():
    """Crée des templates d'exemple pour l'MVP"""
    
    templates_data = [
        {
            "name": "Portfolio Moderne",
            "slug": "portfolio-moderne",
            "description": "Template élégant pour présenter votre portfolio professionnel",
            "category": "portfolio",
            "structure": {
                "sections": ["header", "hero", "about", "portfolio", "contact", "footer"],
                "layout": "single-page",
                "color_scheme": "modern"
            },
            "default_content": {
                "hero": {
                    "title": "Votre Nom",
                    "subtitle": "Développeur Full Stack",
                    "description": "Passionné par la création d'expériences numériques exceptionnelles"
                },
                "about": {
                    "title": "À propos",
                    "content": "Développeur expérimenté avec une expertise en technologies modernes..."
                },
                "portfolio": {
                    "title": "Mes Projets",
                    "projects": []
                }
            },
            "tags": ["moderne", "portfolio", "professionnel"],
            "is_featured": True
        },
        {
            "name": "Site d'Entreprise",
            "slug": "site-entreprise",
            "description": "Template professionnel pour votre entreprise ou startup",
            "category": "business",
            "structure": {
                "sections": ["header", "hero", "services", "about", "team", "contact", "footer"],
                "layout": "multi-page",
                "color_scheme": "corporate"
            },
            "default_content": {
                "hero": {
                    "title": "Votre Entreprise",
                    "subtitle": "Solution innovante pour votre business",
                    "description": "Découvrez nos services professionnels"
                },
                "services": {
                    "title": "Nos Services",
                    "services": []
                },
                "about": {
                    "title": "Notre Histoire",
                    "content": "Depuis notre création, nous nous engageons à..."
                }
            },
            "tags": ["entreprise", "business", "corporate"],
            "is_featured": True
        },
        {
            "name": "Blog Personnel",
            "slug": "blog-personnel",
            "description": "Template clean et moderne pour votre blog",
            "category": "blog",
            "structure": {
                "sections": ["header", "hero", "posts", "about", "sidebar", "footer"],
                "layout": "blog",
                "color_scheme": "minimal"
            },
            "default_content": {
                "hero": {
                    "title": "Mon Blog",
                    "subtitle": "Partagez vos idées avec le monde",
                    "description": "Découvrez mes derniers articles et réflexions"
                },
                "about": {
                    "title": "À propos de l'auteur",
                    "content": "Passionné par [votre domaine]..."
                }
            },
            "tags": ["blog", "personnel", "articles"],
            "is_featured": False
        },
        {
            "name": "Landing Page",
            "slug": "landing-page",
            "description": "Template optimisé pour la conversion",
            "category": "landing",
            "structure": {
                "sections": ["header", "hero", "features", "pricing", "testimonials", "cta", "footer"],
                "layout": "single-page",
                "color_scheme": "conversion"
            },
            "default_content": {
                "hero": {
                    "title": "Votre Produit",
                    "subtitle": "La solution que vous attendiez",
                    "description": "Découvrez comment notre produit peut transformer votre activité"
                },
                "features": {
                    "title": "Fonctionnalités",
                    "features": []
                },
                "pricing": {
                    "title": "Tarifs",
                    "plans": []
                }
            },
            "tags": ["landing", "conversion", "marketing"],
            "is_featured": True
        },
        {
            "name": "E-commerce Simple",
            "slug": "ecommerce-simple",
            "description": "Template pour boutique en ligne",
            "category": "ecommerce",
            "structure": {
                "sections": ["header", "hero", "products", "categories", "about", "contact", "footer"],
                "layout": "multi-page",
                "color_scheme": "ecommerce"
            },
            "default_content": {
                "hero": {
                    "title": "Votre Boutique",
                    "subtitle": "Découvrez nos produits",
                    "description": "Trouvez les meilleurs produits au meilleur prix"
                },
                "products": {
                    "title": "Nos Produits",
                    "products": []
                },
                "categories": {
                    "title": "Catégories",
                    "categories": []
                }
            },
            "tags": ["ecommerce", "boutique", "vente"],
            "is_featured": False
        }
    ]
    
    db = SessionLocal()
    try:
        # Vérifier si des templates existent déjà
        existing_count = db.query(Template).count()
        if existing_count > 0:
            print(f"⚠️  {existing_count} templates déjà présents dans la base")
            return
        
        # Créer les templates
        for template_data in templates_data:
            template = Template(
                name=template_data["name"],
                slug=template_data["slug"],
                description=template_data["description"],
                category=template_data["category"],
                structure=template_data["structure"],
                default_content=template_data["default_content"],
                tags=template_data["tags"],
                is_featured=template_data["is_featured"],
                is_active=True,
                usage_count=0,
                rating_avg=5,
                rating_count=1
            )
            db.add(template)
        
        db.commit()
        print(f"✅ {len(templates_data)} templates créés avec succès!")
        
        # Afficher les templates créés
        templates = db.query(Template).all()
        print("\n📋 Templates disponibles:")
        for template in templates:
            print(f"  - {template.name} ({template.category}) - {template.slug}")
            
    except Exception as e:
        print(f"❌ Erreur lors de la création des templates: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Initialisation des templates...")
    init_db()
    create_sample_templates()
    print("✨ Initialisation terminée!")