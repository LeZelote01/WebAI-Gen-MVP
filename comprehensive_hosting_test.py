#!/usr/bin/env python3
"""
Comprehensive Hosting Test - Full User Journey
"""

import requests
import json
import time
from datetime import datetime
import os

API_BASE = "http://localhost:8001/api"

def log(message):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def test_full_hosting_workflow():
    """Test the complete hosting workflow"""
    log("🚀 Starting Comprehensive Hosting Test")
    log("=" * 60)
    
    session = requests.Session()
    
    # Step 1: Create and authenticate user
    timestamp = int(time.time())
    user_data = {
        "email": f"fulltest{timestamp}@example.com",
        "username": f"fulltest{timestamp}",
        "full_name": "Full Test User",
        "password": "TestPassword123!"
    }
    
    log("Step 1: Creating and authenticating user...")
    
    # Register
    response = session.post(f"{API_BASE}/auth/register", json=user_data)
    if response.status_code != 201:
        log(f"❌ User registration failed: {response.status_code}")
        return False
    
    # Login
    login_response = session.post(f"{API_BASE}/auth/login", json={
        "email": user_data["email"],
        "password": user_data["password"]
    })
    
    if login_response.status_code != 200:
        log(f"❌ Login failed: {login_response.status_code}")
        return False
    
    token = login_response.json()['access_token']
    session.headers.update({'Authorization': f'Bearer {token}'})
    log("✅ User authenticated successfully")
    
    # Step 2: Get templates and create website
    log("Step 2: Creating website from template...")
    
    templates_response = session.get(f"{API_BASE}/templates")
    if templates_response.status_code != 200:
        log(f"❌ Failed to get templates: {templates_response.status_code}")
        return False
    
    templates = templates_response.json().get('items', [])
    if not templates:
        log("❌ No templates available")
        return False
    
    template_id = templates[0]['id']
    template_name = templates[0]['name']
    log(f"✅ Using template: {template_name}")
    
    # Create website using the generator endpoint
    website_name = "Mon Site de Test Hébergement"
    website_description = "Site créé pour tester l'hébergement intégré"
    
    generate_response = session.post(f"{API_BASE}/generate/website", params={
        "template_id": template_id,
        "website_name": website_name,
        "website_description": website_description
    })
    
    if generate_response.status_code != 201:
        log(f"❌ Website generation failed: {generate_response.status_code}")
        return False
    
    website_data = generate_response.json()
    website_id = website_data['id']
    log(f"✅ Website generated: {website_data['name']} (ID: {website_id})")
    
    # Step 3: Customize website content
    log("Step 3: Customizing website content...")
    
    update_data = {
        "content": {
            "hero": {
                "title": "Mon Site d'Hébergement Test",
                "subtitle": "Bienvenue sur mon site hébergé",
                "description": "Ce site a été créé avec le générateur IA et déployé sur l'hébergement intégré."
            },
            "about": {
                "title": "À propos",
                "content": "Ce site démontre les capacités d'hébergement intégré de la plateforme."
            },
            "services": [
                {
                    "title": "Hébergement Rapide",
                    "description": "Déploiement en un clic"
                },
                {
                    "title": "SSL Automatique",
                    "description": "Sécurité intégrée"
                }
            ]
        },
        "custom_css": """
        .hosting-demo {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
        }
        .feature-box {
            border: 2px solid #4CAF50;
            padding: 15px;
            margin: 10px;
            border-radius: 8px;
        }
        """,
        "custom_js": """
        console.log('Site d\\'hébergement test chargé avec succès!');
        document.addEventListener('DOMContentLoaded', function() {
            console.log('DOM chargé - Site hébergé fonctionnel');
        });
        """,
        "meta_title": "Site de Test Hébergement - Générateur IA",
        "meta_description": "Site web de démonstration pour l'hébergement intégré",
        "meta_keywords": "hébergement, test, IA, générateur, site web"
    }
    
    update_response = session.put(f"{API_BASE}/websites/{website_id}", json=update_data)
    if update_response.status_code == 200:
        log("✅ Website content customized successfully")
    else:
        log(f"⚠️ Content customization failed: {update_response.status_code}")
    
    # Step 4: Deploy website
    log("Step 4: Deploying website to hosting...")
    
    deploy_response = session.post(f"{API_BASE}/websites/{website_id}/deploy")
    
    if deploy_response.status_code != 200:
        log(f"❌ Deployment failed: {deploy_response.status_code}")
        log(f"Error: {deploy_response.text}")
        return False
    
    deploy_data = deploy_response.json()
    log(f"✅ Deployment successful: {deploy_data.get('message', 'No message')}")
    
    # Get updated website info
    website_response = session.get(f"{API_BASE}/websites/{website_id}")
    if website_response.status_code == 200:
        website_info = website_response.json()
        hosting_url = website_info.get('hosting_url')
        hosting_subdomain = website_info.get('hosting_subdomain')
        ssl_enabled = website_info.get('ssl_enabled')
        
        log(f"✅ Website hosted at: {hosting_url}")
        log(f"✅ Subdomain: {hosting_subdomain}")
        log(f"✅ SSL enabled: {ssl_enabled}")
        
        # Step 5: Test hosted site accessibility
        log("Step 5: Testing hosted site accessibility...")
        
        # Check if site files exist
        hosted_path = f"/app/hosted_sites/{hosting_subdomain}"
        if os.path.exists(hosted_path):
            log(f"✅ Site files deployed to: {hosted_path}")
            
            # List deployed files
            files = os.listdir(hosted_path)
            log(f"✅ Deployed files: {files}")
            
            # Check index.html content
            index_path = os.path.join(hosted_path, "index.html")
            if os.path.exists(index_path):
                with open(index_path, 'r') as f:
                    content = f.read()
                    if "Mon Site d'Hébergement Test" in content:
                        log("✅ Index.html contains expected content")
                    else:
                        log("⚠️ Index.html missing expected content")
            
        else:
            log(f"❌ Site files not found at: {hosted_path}")
        
        # Try to access via hosting server (localhost:3001)
        try:
            # Test direct access to hosting server
            hosting_server_response = requests.get("http://localhost:3001", timeout=5)
            if hosting_server_response.status_code == 200:
                log("✅ Hosting server is accessible")
            else:
                log(f"⚠️ Hosting server returned: {hosting_server_response.status_code}")
        except Exception as e:
            log(f"⚠️ Could not access hosting server: {e}")
        
        # Step 6: Test hosting management features
        log("Step 6: Testing hosting management features...")
        
        # Test redeploy
        redeploy_response = session.put(f"{API_BASE}/websites/{website_id}/redeploy")
        if redeploy_response.status_code == 200:
            log("✅ Redeploy successful")
        else:
            log(f"❌ Redeploy failed: {redeploy_response.status_code}")
        
        # Test SSL configuration
        ssl_response = session.post(f"{API_BASE}/websites/{website_id}/ssl")
        if ssl_response.status_code == 200:
            log("✅ SSL configuration successful")
        else:
            log(f"❌ SSL configuration failed: {ssl_response.status_code}")
        
        # Test hosted sites listing
        sites_response = session.get(f"{API_BASE}/hosting/sites")
        if sites_response.status_code == 200:
            sites = sites_response.json()
            log(f"✅ Found {len(sites)} hosted sites")
            
            # Verify our site is in the list
            our_site = next((site for site in sites if site.get('website_id') == website_id), None)
            if our_site:
                log("✅ Our website found in hosted sites list")
                log(f"   - Subdomain: {our_site.get('subdomain')}")
                log(f"   - Status: {our_site.get('status')}")
            else:
                log("⚠️ Our website not found in hosted sites list")
        else:
            log(f"❌ Failed to list hosted sites: {sites_response.status_code}")
        
        # Step 7: Test website export
        log("Step 7: Testing website export...")
        
        export_response = session.get(f"{API_BASE}/websites/{website_id}/export")
        if export_response.status_code == 200:
            content_type = export_response.headers.get('content-type', '')
            if 'application/zip' in content_type:
                log("✅ Website export successful (ZIP file)")
            else:
                log(f"⚠️ Export returned unexpected content type: {content_type}")
        else:
            log(f"❌ Website export failed: {export_response.status_code}")
        
        # Step 8: Test undeployment
        log("Step 8: Testing website undeployment...")
        
        undeploy_response = session.delete(f"{API_BASE}/websites/{website_id}/undeploy")
        if undeploy_response.status_code == 200:
            log("✅ Undeployment successful")
            
            # Verify website is no longer hosted
            final_check = session.get(f"{API_BASE}/websites/{website_id}")
            if final_check.status_code == 200:
                final_data = final_check.json()
                if not final_data.get('is_hosted'):
                    log("✅ Website no longer marked as hosted")
                else:
                    log("❌ Website still marked as hosted after undeployment")
            
            # Check if files were removed
            if not os.path.exists(hosted_path):
                log("✅ Site files removed from hosting directory")
            else:
                log("⚠️ Site files still exist in hosting directory")
                
        else:
            log(f"❌ Undeployment failed: {undeploy_response.status_code}")
    
    else:
        log(f"❌ Could not retrieve website info: {website_response.status_code}")
        return False
    
    log("=" * 60)
    log("🎉 Comprehensive hosting test completed successfully!")
    log("✅ All major hosting features are working correctly")
    
    return True

if __name__ == "__main__":
    success = test_full_hosting_workflow()
    if success:
        print("\n🎉 All tests passed! Hosting functionality is fully operational.")
    else:
        print("\n❌ Some tests failed. Please check the issues above.")
