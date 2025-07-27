"""
Gestionnaire d'hébergement intégré pour les sites web
Phase 1 MVP - Hébergement basique avec sous-domaines
"""
import os
import shutil
import zipfile
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
import uuid
import tempfile
import subprocess
import json

from website_exporter import WebsiteExporter

class HostingManager:
    """Gestionnaire d'hébergement intégré basique"""
    
    def __init__(self):
        # Configuration des chemins d'hébergement
        self.hosting_root = Path("/app/hosted_sites")
        self.hosting_root.mkdir(exist_ok=True)
        
        # Configuration de base
        self.base_domain = os.getenv("HOSTING_BASE_DOMAIN", "localhost:3001")
        self.use_ssl = os.getenv("USE_SSL", "false").lower() == "true"
        
    def is_subdomain_available(self, subdomain: str) -> bool:
        """Vérifie si un sous-domaine est disponible"""
        subdomain_path = self.hosting_root / subdomain
        return not subdomain_path.exists()
        
    def generate_subdomain(self, website_name: str, user_id: str) -> str:
        """Génère un sous-domaine unique basé sur le nom du site"""
        from slugify import slugify
        
        base_subdomain = slugify(website_name.lower())
        
        # Si le sous-domaine est disponible, l'utiliser
        if self.is_subdomain_available(base_subdomain):
            return base_subdomain
            
        # Sinon, ajouter un suffixe unique
        counter = 1
        while True:
            subdomain = f"{base_subdomain}-{counter}"
            if self.is_subdomain_available(subdomain):
                return subdomain
            counter += 1
            
    def deploy_website(self, website_data: Dict[str, Any], template_data: Optional[Dict[str, Any]] = None, custom_subdomain: Optional[str] = None) -> Dict[str, str]:
        """
        Déploie un site web sur l'hébergement intégré
        
        Args:
            website_data: Données du site web
            template_data: Données du template (optionnel)
            custom_subdomain: Sous-domaine personnalisé (optionnel)
            
        Returns:
            Dict contenant les informations de déploiement
        """
        try:
            # Générer le contenu HTML du site
            exporter = WebsiteExporter()
            
            # Créer un dossier temporaire pour l'export
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Exporter le site dans le dossier temporaire
                zip_buffer = exporter.export_website(website_data, template_data)
                
                # Extraire le ZIP dans le dossier temporaire
                zip_path = temp_path / "export.zip"
                with open(zip_path, 'wb') as f:
                    f.write(zip_buffer.getvalue())
                    
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_path)
                
                # Déterminer le sous-domaine
                if custom_subdomain and self.is_subdomain_available(custom_subdomain):
                    subdomain = custom_subdomain
                else:
                    subdomain = self.generate_subdomain(
                        website_data['name'], 
                        website_data.get('owner_id', 'unknown')
                    )
                
                # Créer le dossier de déploiement
                deploy_path = self.hosting_root / subdomain
                deploy_path.mkdir(exist_ok=True)
                
                # Copier les fichiers du site
                for item in temp_path.iterdir():
                    if item.name != "export.zip":
                        if item.is_dir():
                            shutil.copytree(item, deploy_path / item.name, dirs_exist_ok=True)
                        else:
                            shutil.copy2(item, deploy_path)
                
                # Générer l'URL d'accès
                protocol = "https" if self.use_ssl else "http"
                hosting_url = f"{protocol}://{subdomain}.{self.base_domain}"
                
                # Créer un fichier de métadonnées pour le site
                metadata = {
                    "website_id": website_data['id'],
                    "website_name": website_data['name'],
                    "subdomain": subdomain,
                    "hosting_url": hosting_url,
                    "deployed_at": datetime.utcnow().isoformat(),
                    "ssl_enabled": self.use_ssl,
                    "owner_id": website_data.get('owner_id'),
                    "status": "active"
                }
                
                metadata_path = deploy_path / ".site_metadata.json"
                with open(metadata_path, 'w') as f:
                    json.dump(metadata, f, indent=2)
                
                return {
                    "success": True,
                    "subdomain": subdomain,
                    "hosting_url": hosting_url,
                    "ssl_enabled": self.use_ssl,
                    "deployed_at": datetime.utcnow().isoformat(),
                    "deploy_path": str(deploy_path)
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def undeploy_website(self, subdomain: str) -> Dict[str, Any]:
        """Supprime un site de l'hébergement"""
        try:
            deploy_path = self.hosting_root / subdomain
            
            if deploy_path.exists():
                shutil.rmtree(deploy_path)
                return {
                    "success": True,
                    "message": f"Site {subdomain} supprimé avec succès"
                }
            else:
                return {
                    "success": False,
                    "error": f"Site {subdomain} non trouvé"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def update_website(self, subdomain: str, website_data: Dict[str, Any], template_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Met à jour un site déployé"""
        try:
            # Supprimer l'ancien déploiement
            self.undeploy_website(subdomain)
            
            # Redéployer avec les nouvelles données
            return self.deploy_website(website_data, template_data, subdomain)
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_site_info(self, subdomain: str) -> Optional[Dict[str, Any]]:
        """Récupère les informations d'un site déployé"""
        try:
            deploy_path = self.hosting_root / subdomain
            metadata_path = deploy_path / ".site_metadata.json"
            
            if metadata_path.exists():
                with open(metadata_path, 'r') as f:
                    return json.load(f)
            
            return None
            
        except Exception as e:
            print(f"Error getting site info: {e}")
            return None
    
    def list_hosted_sites(self) -> list:
        """Liste tous les sites hébergés"""
        sites = []
        
        for subdomain_dir in self.hosting_root.iterdir():
            if subdomain_dir.is_dir():
                site_info = self.get_site_info(subdomain_dir.name)
                if site_info:
                    sites.append(site_info)
        
        return sites
    
    def setup_ssl_certificate(self, subdomain: str) -> Dict[str, Any]:
        """
        Configure un certificat SSL pour un sous-domaine
        Phase 1 MVP - Version simplifiée (certificat auto-signé ou Let's Encrypt basique)
        """
        # Pour le MVP, on simule l'activation SSL
        # Dans une version production, ceci utiliserait Let's Encrypt ou un autre CA
        try:
            deploy_path = self.hosting_root / subdomain
            metadata_path = deploy_path / ".site_metadata.json"
            
            if metadata_path.exists():
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                
                metadata['ssl_enabled'] = True
                metadata['ssl_configured_at'] = datetime.utcnow().isoformat()
                
                with open(metadata_path, 'w') as f:
                    json.dump(metadata, f, indent=2)
                
                return {
                    "success": True,
                    "message": f"SSL activé pour {subdomain}",
                    "ssl_enabled": True
                }
            
            return {
                "success": False,
                "error": "Site non trouvé"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }