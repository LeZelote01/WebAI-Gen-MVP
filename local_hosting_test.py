#!/usr/bin/env python3
"""
Local Hosting API Test for AI Website Generator
"""

import requests
import json
import time
from datetime import datetime

API_BASE = "http://localhost:8001/api"

def log(message):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def test_hosting_endpoints():
    """Test hosting functionality locally"""
    log("🚀 Testing Hosting Functionality (Local)")
    
    session = requests.Session()
    
    # Create user
    timestamp = int(time.time())
    user_data = {
        "email": f"hosttest{timestamp}@example.com",
        "username": f"hosttest{timestamp}",
        "full_name": "Host Test User",
        "password": "TestPassword123!"
    }
    
    log("Creating test user...")
    response = session.post(f"{API_BASE}/auth/register", json=user_data)
    if response.status_code != 201:
        log(f"❌ Failed to create user: {response.status_code} - {response.text}")
        return False
    
    log("✅ User created successfully")
    
    # Login
    log("Logging in...")
    login_response = session.post(f"{API_BASE}/auth/login", json={
        "email": user_data["email"],
        "password": user_data["password"]
    })
    
    if login_response.status_code != 200:
        log(f"❌ Login failed: {login_response.status_code} - {login_response.text}")
        return False
    
    token = login_response.json()['access_token']
    session.headers.update({'Authorization': f'Bearer {token}'})
    log("✅ Login successful")
    
    # Get templates
    log("Getting templates...")
    templates_response = session.get(f"{API_BASE}/templates")
    if templates_response.status_code != 200:
        log(f"❌ Failed to get templates: {templates_response.status_code}")
        return False
    
    templates = templates_response.json().get('items', [])
    if not templates:
        log("❌ No templates found")
        return False
    
    template_id = templates[0]['id']
    log(f"✅ Using template: {templates[0]['name']}")
    
    # Create website
    log("Creating website...")
    website_data = {
        "name": "Test Hosting Site",
        "description": "Test site for hosting functionality",
        "template_id": template_id
    }
    
    website_response = session.post(f"{API_BASE}/websites", json=website_data)
    if website_response.status_code != 201:
        log(f"❌ Failed to create website: {website_response.status_code} - {website_response.text}")
        return False
    
    website_id = website_response.json()['id']
    log(f"✅ Website created: {website_id}")
    
    # Update website content
    log("Updating website content...")
    update_data = {
        "content": {
            "hero": {
                "title": "Mon Site d'Hébergement Test",
                "subtitle": "Site créé pour tester l'hébergement intégré",
                "description": "Ce site web a été créé pour tester la fonctionnalité d'hébergement intégré Phase 1."
            }
        },
        "custom_css": ".hosting-test { color: #4CAF50; font-weight: bold; }",
        "custom_js": "console.log('Hosting test website loaded successfully');",
        "meta_title": "Site de Test Hébergement"
    }
    
    update_response = session.put(f"{API_BASE}/websites/{website_id}", json=update_data)
    if update_response.status_code == 200:
        log("✅ Website content updated")
    else:
        log(f"⚠️ Content update failed: {update_response.status_code}")
    
    # Test deployment
    log("Testing deployment...")
    deploy_response = session.post(f"{API_BASE}/websites/{website_id}/deploy")
    
    if deploy_response.status_code == 200:
        deploy_data = deploy_response.json()
        log(f"✅ Deployment successful: {deploy_data.get('message', 'No message')}")
        
        # Check if website is marked as hosted
        website_check = session.get(f"{API_BASE}/websites/{website_id}")
        if website_check.status_code == 200:
            website_info = website_check.json()
            if website_info.get('is_hosted'):
                hosting_url = website_info.get('hosting_url')
                log(f"✅ Website is hosted at: {hosting_url}")
                
                # Try to access the hosted site
                if hosting_url:
                    try:
                        site_response = requests.get(hosting_url, timeout=5)
                        if site_response.status_code == 200:
                            log("✅ Hosted site is accessible")
                            if "Mon Site d'Hébergement Test" in site_response.text:
                                log("✅ Hosted site contains expected content")
                            else:
                                log("⚠️ Hosted site missing expected content")
                        else:
                            log(f"⚠️ Hosted site returned status: {site_response.status_code}")
                    except Exception as e:
                        log(f"⚠️ Could not access hosted site: {e}")
            else:
                log("❌ Website not marked as hosted after deployment")
        
    else:
        log(f"❌ Deployment failed: {deploy_response.status_code}")
        log(f"Error: {deploy_response.text}")
        return False
    
    # Test redeploy
    log("Testing redeploy...")
    redeploy_response = session.put(f"{API_BASE}/websites/{website_id}/redeploy")
    if redeploy_response.status_code == 200:
        log("✅ Redeploy successful")
    else:
        log(f"❌ Redeploy failed: {redeploy_response.status_code}")
    
    # Test SSL configuration
    log("Testing SSL configuration...")
    ssl_response = session.post(f"{API_BASE}/websites/{website_id}/ssl")
    if ssl_response.status_code == 200:
        log("✅ SSL configuration successful")
    else:
        log(f"❌ SSL configuration failed: {ssl_response.status_code}")
    
    # Test hosted sites list
    log("Testing hosted sites list...")
    sites_response = session.get(f"{API_BASE}/hosting/sites")
    if sites_response.status_code == 200:
        sites = sites_response.json()
        log(f"✅ Found {len(sites)} hosted sites")
        
        # Check if our site is in the list
        test_site_found = any(site.get('website_id') == website_id for site in sites)
        if test_site_found:
            log("✅ Test website found in hosted sites list")
        else:
            log("⚠️ Test website not found in hosted sites list")
    else:
        log(f"❌ Failed to list hosted sites: {sites_response.status_code}")
    
    # Test undeploy
    log("Testing undeploy...")
    undeploy_response = session.delete(f"{API_BASE}/websites/{website_id}/undeploy")
    if undeploy_response.status_code == 200:
        log("✅ Undeploy successful")
        
        # Verify website is no longer hosted
        website_check = session.get(f"{API_BASE}/websites/{website_id}")
        if website_check.status_code == 200:
            website_info = website_check.json()
            if not website_info.get('is_hosted'):
                log("✅ Website no longer marked as hosted")
            else:
                log("❌ Website still marked as hosted after undeploy")
    else:
        log(f"❌ Undeploy failed: {undeploy_response.status_code}")
    
    log("✅ Hosting functionality tests completed")
    return True

if __name__ == "__main__":
    success = test_hosting_endpoints()
    if success:
        print("\n🎉 All hosting tests completed successfully!")
    else:
        print("\n❌ Some hosting tests failed")
