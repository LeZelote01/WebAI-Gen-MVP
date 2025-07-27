#!/usr/bin/env python3
"""
Simple Hosting API Test for AI Website Generator
"""

import requests
import json
import time
from datetime import datetime

# Get backend URL from frontend .env file
try:
    with open('/app/frontend/.env', 'r') as f:
        for line in f:
            if line.startswith('REACT_APP_BACKEND_URL='):
                BACKEND_URL = line.split('=', 1)[1].strip()
                break
        else:
            BACKEND_URL = "http://localhost:8001"
except:
    BACKEND_URL = "http://localhost:8001"

API_BASE = f"{BACKEND_URL}/api"

def log(message):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def test_hosting_endpoints():
    """Test hosting functionality"""
    log("🚀 Testing Hosting Functionality")
    
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
        log(f"❌ Failed to create user: {response.status_code}")
        return False
    
    # Login
    log("Logging in...")
    login_response = session.post(f"{API_BASE}/auth/login", json={
        "email": user_data["email"],
        "password": user_data["password"]
    })
    
    if login_response.status_code != 200:
        log(f"❌ Login failed: {login_response.status_code}")
        return False
    
    token = login_response.json()['access_token']
    session.headers.update({'Authorization': f'Bearer {token}'})
    
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
    
    # Create website
    log("Creating website...")
    website_data = {
        "name": "Test Hosting Site",
        "description": "Test site for hosting",
        "template_id": template_id
    }
    
    website_response = session.post(f"{API_BASE}/websites", json=website_data)
    if website_response.status_code != 201:
        log(f"❌ Failed to create website: {website_response.status_code}")
        return False
    
    website_id = website_response.json()['id']
    log(f"✅ Website created: {website_id}")
    
    # Test deployment
    log("Testing deployment...")
    deploy_response = session.post(f"{API_BASE}/websites/{website_id}/deploy")
    
    if deploy_response.status_code == 200:
        log("✅ Deployment endpoint responded successfully")
        log(f"Response: {deploy_response.json()}")
        
        # Check if website is marked as hosted
        website_check = session.get(f"{API_BASE}/websites/{website_id}")
        if website_check.status_code == 200:
            website_info = website_check.json()
            if website_info.get('is_hosted'):
                log(f"✅ Website is hosted at: {website_info.get('hosting_url')}")
            else:
                log("⚠️ Website not marked as hosted")
        
    else:
        log(f"❌ Deployment failed: {deploy_response.status_code}")
        log(f"Error: {deploy_response.text}")
        return False
    
    # Test other hosting endpoints
    log("Testing redeploy...")
    redeploy_response = session.put(f"{API_BASE}/websites/{website_id}/redeploy")
    log(f"Redeploy status: {redeploy_response.status_code}")
    
    log("Testing SSL configuration...")
    ssl_response = session.post(f"{API_BASE}/websites/{website_id}/ssl")
    log(f"SSL config status: {ssl_response.status_code}")
    
    log("Testing hosted sites list...")
    sites_response = session.get(f"{API_BASE}/hosting/sites")
    log(f"Hosted sites status: {sites_response.status_code}")
    if sites_response.status_code == 200:
        sites = sites_response.json()
        log(f"Found {len(sites)} hosted sites")
    
    log("Testing undeploy...")
    undeploy_response = session.delete(f"{API_BASE}/websites/{website_id}/undeploy")
    log(f"Undeploy status: {undeploy_response.status_code}")
    
    log("✅ Hosting tests completed")
    return True

if __name__ == "__main__":
    test_hosting_endpoints()
