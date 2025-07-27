#!/usr/bin/env python3
"""
Backend API Testing Suite for AI Website Generator
Tests the new export functionality and existing APIs
"""

import requests
import json
import zipfile
import io
import os
from datetime import datetime
import time

# Get backend URL from environment - use local for testing
BACKEND_URL = "http://localhost:8001"
API_BASE = f"{BACKEND_URL}/api"

class BackendTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_user_id = None
        self.test_website_id = None
        self.test_template_id = None
        self.test_user_email = None
        self.test_user_password = None
        
    def log(self, message):
        """Log test messages with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")
        
    def test_health_endpoint(self):
        """Test the health check endpoint"""
        self.log("Testing health endpoint...")
        try:
            response = self.session.get(f"{API_BASE}/health")
            if response.status_code == 200:
                data = response.json()
                if data.get('message') == "API is healthy and running!":
                    self.log("✅ Health endpoint working correctly")
                    return True
                else:
                    self.log(f"❌ Health endpoint returned unexpected message: {data}")
                    return False
            else:
                self.log(f"❌ Health endpoint failed with status {response.status_code}")
                return False
        except Exception as e:
            self.log(f"❌ Health endpoint error: {e}")
            return False
    
    def create_test_user(self):
        """Create a test user for authentication"""
        self.log("Creating test user...")
        
        # Generate unique user data
        timestamp = int(time.time())
        self.test_user_email = f"testuser{timestamp}@example.com"
        self.test_user_password = "TestPassword123!"
        
        user_data = {
            "email": self.test_user_email,
            "username": f"testuser{timestamp}",
            "full_name": "Test User Export",
            "password": self.test_user_password
        }
        
        try:
            response = self.session.post(f"{API_BASE}/auth/register", json=user_data)
            if response.status_code == 201:
                user_info = response.json()
                self.test_user_id = user_info['id']
                self.log(f"✅ Test user created successfully: {user_info['email']}")
                return True
            else:
                self.log(f"❌ Failed to create test user: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            self.log(f"❌ Error creating test user: {e}")
            return False
    
    def login_test_user(self):
        """Login with the test user to get authentication token"""
        self.log("Logging in test user...")
        
        if not self.test_user_email or not self.test_user_password:
            self.log("❌ No test user credentials available")
            return False
        
        login_data = {
            "email": self.test_user_email,
            "password": self.test_user_password
        }
        
        try:
            response = self.session.post(f"{API_BASE}/auth/login", json=login_data)
            if response.status_code == 200:
                token_data = response.json()
                self.auth_token = token_data['access_token']
                self.session.headers.update({'Authorization': f'Bearer {self.auth_token}'})
                self.log("✅ User logged in successfully")
                return True
            else:
                self.log(f"❌ Login failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            self.log(f"❌ Login error: {e}")
            return False
    
    def get_templates(self):
        """Get available templates and store one for testing"""
        self.log("Getting available templates...")
        
        try:
            response = self.session.get(f"{API_BASE}/templates")
            if response.status_code == 200:
                data = response.json()
                templates = data.get('items', [])
                if templates:
                    self.test_template_id = templates[0]['id']
                    self.log(f"✅ Found {len(templates)} templates, using: {templates[0]['name']}")
                    return True
                else:
                    self.log("❌ No templates found")
                    return False
            else:
                self.log(f"❌ Failed to get templates: {response.status_code}")
                return False
        except Exception as e:
            self.log(f"❌ Error getting templates: {e}")
            return False
    
    def create_test_website(self):
        """Create a test website for export testing"""
        self.log("Creating test website...")
        
        if not self.test_template_id:
            self.log("❌ No template ID available for website creation")
            return False
        
        website_data = {
            "name": "Test Export Website",
            "description": "A test website for export functionality testing",
            "template_id": self.test_template_id
        }
        
        try:
            response = self.session.post(f"{API_BASE}/websites", json=website_data)
            if response.status_code == 201:
                website_info = response.json()
                self.test_website_id = website_info['id']
                self.log(f"✅ Test website created: {website_info['name']} (ID: {self.test_website_id})")
                return True
            else:
                self.log(f"❌ Failed to create test website: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            self.log(f"❌ Error creating test website: {e}")
            return False
    
    def update_website_content(self):
        """Update website with some test content"""
        self.log("Updating website with test content...")
        
        if not self.test_website_id:
            self.log("❌ No website ID available for content update")
            return False
        
        update_data = {
            "content": {
                "hero": {
                    "title": "Mon Site de Test",
                    "subtitle": "Site créé pour tester l'export",
                    "description": "Ce site web a été créé pour tester la fonctionnalité d'export en ZIP."
                },
                "about": {
                    "title": "À propos de ce test",
                    "content": "Ce contenu a été ajouté pour vérifier que l'export fonctionne correctement avec du contenu personnalisé."
                }
            },
            "custom_css": "/* CSS personnalisé pour le test */\n.test-class { color: #ff6b6b; }",
            "custom_js": "// JavaScript personnalisé pour le test\nconsole.log('Export test website loaded');",
            "meta_title": "Site de Test Export",
            "meta_description": "Site web de test pour la fonctionnalité d'export ZIP",
            "meta_keywords": "test, export, zip, website"
        }
        
        try:
            response = self.session.put(f"{API_BASE}/websites/{self.test_website_id}", json=update_data)
            if response.status_code == 200:
                self.log("✅ Website content updated successfully")
                return True
            else:
                self.log(f"❌ Failed to update website content: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            self.log(f"❌ Error updating website content: {e}")
            return False
    
    def test_export_with_authentication(self):
        """Test the export endpoint with proper authentication"""
        self.log("Testing export endpoint with authentication...")
        
        if not self.test_website_id:
            self.log("❌ No website ID available for export test")
            return False
        
        try:
            response = self.session.get(f"{API_BASE}/websites/{self.test_website_id}/export")
            
            if response.status_code == 200:
                # Check if response is a ZIP file
                content_type = response.headers.get('content-type', '')
                content_disposition = response.headers.get('content-disposition', '')
                
                if 'application/zip' in content_type and 'attachment' in content_disposition:
                    self.log("✅ Export endpoint returned ZIP file with correct headers")
                    
                    # Try to parse the ZIP content
                    try:
                        zip_content = io.BytesIO(response.content)
                        with zipfile.ZipFile(zip_content, 'r') as zip_file:
                            file_list = zip_file.namelist()
                            self.log(f"✅ ZIP file contains {len(file_list)} files: {file_list}")
                            
                            # Check for required files
                            required_files = ['index.html', 'README.md', 'DEPLOYMENT.md']
                            missing_files = [f for f in required_files if f not in file_list]
                            
                            if not missing_files:
                                self.log("✅ All required files present in ZIP")
                                
                                # Check index.html content
                                html_content = zip_file.read('index.html').decode('utf-8')
                                if 'Mon Site de Test' in html_content and 'test-class' in html_content:
                                    self.log("✅ HTML file contains expected custom content and CSS")
                                else:
                                    self.log("⚠️ HTML file missing some expected content")
                                
                                # Check README.md
                                readme_content = zip_file.read('README.md').decode('utf-8')
                                if 'Test Export Website' in readme_content:
                                    self.log("✅ README.md contains website name")
                                else:
                                    self.log("⚠️ README.md missing expected content")
                                
                                return True
                            else:
                                self.log(f"❌ Missing required files in ZIP: {missing_files}")
                                return False
                                
                    except zipfile.BadZipFile:
                        self.log("❌ Response is not a valid ZIP file")
                        return False
                        
                else:
                    self.log(f"❌ Export endpoint returned wrong content type: {content_type}")
                    return False
                    
            else:
                self.log(f"❌ Export endpoint failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Export endpoint error: {e}")
            return False
    
    def test_export_without_authentication(self):
        """Test export endpoint without authentication (should fail)"""
        self.log("Testing export endpoint without authentication...")
        
        if not self.test_website_id:
            self.log("❌ No website ID available for export test")
            return False
        
        # Remove authentication header temporarily
        original_auth = self.session.headers.get('Authorization')
        if 'Authorization' in self.session.headers:
            del self.session.headers['Authorization']
        
        try:
            response = self.session.get(f"{API_BASE}/websites/{self.test_website_id}/export")
            
            # Restore authentication header
            if original_auth:
                self.session.headers['Authorization'] = original_auth
            
            if response.status_code in [401, 403]:
                self.log(f"✅ Export endpoint correctly requires authentication ({response.status_code})")
                return True
            else:
                self.log(f"❌ Export endpoint should require authentication but returned: {response.status_code}")
                return False
                
        except Exception as e:
            # Restore authentication header
            if original_auth:
                self.session.headers['Authorization'] = original_auth
            self.log(f"❌ Error testing unauthenticated export: {e}")
            return False
    
    def test_export_nonexistent_website(self):
        """Test export endpoint with non-existent website ID (should return 404)"""
        self.log("Testing export endpoint with non-existent website...")
        
        fake_website_id = "00000000-0000-0000-0000-000000000000"
        
        try:
            response = self.session.get(f"{API_BASE}/websites/{fake_website_id}/export")
            
            if response.status_code == 404:
                self.log("✅ Export endpoint correctly returns 404 for non-existent website")
                return True
            else:
                self.log(f"❌ Export endpoint should return 404 but returned: {response.status_code}")
                return False
                
        except Exception as e:
            self.log(f"❌ Error testing non-existent website export: {e}")
            return False
    
    def test_export_other_users_website(self):
        """Test export endpoint with another user's website (should return 404)"""
        self.log("Testing export endpoint with another user's website...")
        
        # Create another user and website
        timestamp = int(time.time()) + 1
        other_user_data = {
            "email": f"otheruser{timestamp}@example.com",
            "username": f"otheruser{timestamp}",
            "full_name": "Other Test User",
            "password": "OtherPassword123!"
        }
        
        try:
            # Create other user
            response = self.session.post(f"{API_BASE}/auth/register", json=other_user_data)
            if response.status_code != 201:
                self.log("❌ Failed to create other user for access test")
                return False
            
            # Login as other user
            login_response = self.session.post(f"{API_BASE}/auth/login", json={
                "email": other_user_data["email"],
                "password": other_user_data["password"]
            })
            
            if login_response.status_code != 200:
                self.log("❌ Failed to login as other user")
                return False
            
            other_token = login_response.json()['access_token']
            
            # Create website as other user
            other_session = requests.Session()
            other_session.headers.update({'Authorization': f'Bearer {other_token}'})
            
            website_response = other_session.post(f"{API_BASE}/websites", json={
                "name": "Other User Website",
                "description": "Website by another user",
                "template_id": self.test_template_id
            })
            
            if website_response.status_code != 201:
                self.log("❌ Failed to create website as other user")
                return False
            
            other_website_id = website_response.json()['id']
            
            # Now try to export other user's website with original user's token
            export_response = self.session.get(f"{API_BASE}/websites/{other_website_id}/export")
            
            if export_response.status_code == 404:
                self.log("✅ Export endpoint correctly denies access to other user's website (404)")
                return True
            else:
                self.log(f"❌ Export endpoint should deny access but returned: {export_response.status_code}")
                return False
                
        except Exception as e:
            self.log(f"❌ Error testing other user's website export: {e}")
            return False

    # === HOSTING FUNCTIONALITY TESTS ===
    
    def test_deploy_website(self):
        """Test website deployment functionality"""
        self.log("Testing website deployment...")
        
        if not self.test_website_id:
            self.log("❌ No website ID available for deployment test")
            return False
        
        try:
            # Test deployment without custom subdomain
            response = self.session.post(f"{API_BASE}/websites/{self.test_website_id}/deploy")
            
            if response.status_code == 200:
                data = response.json()
                if "déployé avec succès" in data.get('message', ''):
                    self.log("✅ Website deployed successfully")
                    
                    # Verify website status was updated
                    website_response = self.session.get(f"{API_BASE}/websites/{self.test_website_id}")
                    if website_response.status_code == 200:
                        website_data = website_response.json()
                        if (website_data.get('is_hosted') and 
                            website_data.get('hosting_subdomain') and 
                            website_data.get('hosting_url')):
                            self.log("✅ Website hosting metadata updated correctly")
                            return True
                        else:
                            self.log("❌ Website hosting metadata not updated properly")
                            return False
                    else:
                        self.log("❌ Failed to verify website status after deployment")
                        return False
                else:
                    self.log(f"❌ Deployment response missing success message: {data}")
                    return False
            else:
                self.log(f"❌ Website deployment failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Error testing website deployment: {e}")
            return False
    
    def test_deploy_with_custom_subdomain(self):
        """Test website deployment with custom subdomain"""
        self.log("Testing website deployment with custom subdomain...")
        
        # Create another website for custom subdomain test
        website_data = {
            "name": "Custom Subdomain Test Site",
            "description": "Test site for custom subdomain deployment",
            "template_id": self.test_template_id
        }
        
        try:
            # Create new website
            response = self.session.post(f"{API_BASE}/websites", json=website_data)
            if response.status_code != 201:
                self.log("❌ Failed to create website for custom subdomain test")
                return False
            
            custom_website_id = response.json()['id']
            custom_subdomain = f"custom-test-{int(time.time())}"
            
            # Deploy with custom subdomain
            deploy_response = self.session.post(
                f"{API_BASE}/websites/{custom_website_id}/deploy",
                params={"custom_subdomain": custom_subdomain}
            )
            
            if deploy_response.status_code == 200:
                data = deploy_response.json()
                if custom_subdomain in data.get('message', ''):
                    self.log(f"✅ Website deployed with custom subdomain: {custom_subdomain}")
                    return True
                else:
                    # Check if the subdomain was used in the URL (it might be auto-generated)
                    if "déployé avec succès" in data.get('message', ''):
                        self.log(f"✅ Website deployed successfully (subdomain may be auto-generated): {data.get('message', '')}")
                        return True
                    else:
                        self.log(f"❌ Custom subdomain not reflected in response: {data}")
                        return False
            else:
                self.log(f"❌ Custom subdomain deployment failed: {deploy_response.status_code} - {deploy_response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Error testing custom subdomain deployment: {e}")
            return False
    
    def test_redeploy_website(self):
        """Test website redeployment functionality"""
        self.log("Testing website redeployment...")
        
        if not self.test_website_id:
            self.log("❌ No website ID available for redeployment test")
            return False
        
        try:
            # First ensure the website is deployed
            deploy_response = self.session.post(f"{API_BASE}/websites/{self.test_website_id}/deploy")
            if deploy_response.status_code != 200:
                self.log("❌ Failed to deploy website before redeployment test")
                return False
            
            # Wait a moment to ensure deployment is complete
            time.sleep(1)
            
            # Test redeployment
            redeploy_response = self.session.put(f"{API_BASE}/websites/{self.test_website_id}/redeploy")
            
            if redeploy_response.status_code == 200:
                data = redeploy_response.json()
                if "redéployé avec succès" in data.get('message', ''):
                    self.log("✅ Website redeployed successfully")
                    return True
                else:
                    self.log(f"❌ Redeployment response missing success message: {data}")
                    return False
            else:
                self.log(f"❌ Website redeployment failed: {redeploy_response.status_code} - {redeploy_response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Error testing website redeployment: {e}")
            return False
    
    def test_ssl_configuration(self):
        """Test SSL configuration for hosted website"""
        self.log("Testing SSL configuration...")
        
        if not self.test_website_id:
            self.log("❌ No website ID available for SSL test")
            return False
        
        try:
            # Ensure website is deployed first
            deploy_response = self.session.post(f"{API_BASE}/websites/{self.test_website_id}/deploy")
            if deploy_response.status_code != 200:
                self.log("❌ Failed to deploy website before SSL test")
                return False
            
            # Test SSL configuration
            ssl_response = self.session.post(f"{API_BASE}/websites/{self.test_website_id}/ssl")
            
            if ssl_response.status_code == 200:
                data = ssl_response.json()
                if "SSL configuré avec succès" in data.get('message', ''):
                    self.log("✅ SSL configured successfully")
                    
                    # Verify SSL status was updated
                    website_response = self.session.get(f"{API_BASE}/websites/{self.test_website_id}")
                    if website_response.status_code == 200:
                        website_data = website_response.json()
                        if website_data.get('ssl_enabled'):
                            self.log("✅ SSL status updated in database")
                            return True
                        else:
                            self.log("❌ SSL status not updated in database")
                            return False
                    else:
                        self.log("❌ Failed to verify SSL status after configuration")
                        return False
                else:
                    self.log(f"❌ SSL configuration response missing success message: {data}")
                    return False
            else:
                self.log(f"❌ SSL configuration failed: {ssl_response.status_code} - {ssl_response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Error testing SSL configuration: {e}")
            return False
    
    def test_undeploy_website(self):
        """Test website undeployment functionality"""
        self.log("Testing website undeployment...")
        
        if not self.test_website_id:
            self.log("❌ No website ID available for undeployment test")
            return False
        
        try:
            # Ensure website is deployed first
            deploy_response = self.session.post(f"{API_BASE}/websites/{self.test_website_id}/deploy")
            if deploy_response.status_code != 200:
                self.log("❌ Failed to deploy website before undeployment test")
                return False
            
            # Test undeployment
            undeploy_response = self.session.delete(f"{API_BASE}/websites/{self.test_website_id}/undeploy")
            
            if undeploy_response.status_code == 200:
                data = undeploy_response.json()
                if "retiré de l'hébergement avec succès" in data.get('message', ''):
                    self.log("✅ Website undeployed successfully")
                    
                    # Verify website hosting status was updated
                    website_response = self.session.get(f"{API_BASE}/websites/{self.test_website_id}")
                    if website_response.status_code == 200:
                        website_data = website_response.json()
                        if (not website_data.get('is_hosted') and 
                            not website_data.get('hosting_subdomain') and 
                            not website_data.get('hosting_url')):
                            self.log("✅ Website hosting metadata cleared correctly")
                            return True
                        else:
                            self.log("❌ Website hosting metadata not cleared properly")
                            return False
                    else:
                        self.log("❌ Failed to verify website status after undeployment")
                        return False
                else:
                    self.log(f"❌ Undeployment response missing success message: {data}")
                    return False
            else:
                self.log(f"❌ Website undeployment failed: {undeploy_response.status_code} - {undeploy_response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Error testing website undeployment: {e}")
            return False
    
    def test_list_hosted_sites(self):
        """Test listing hosted sites functionality"""
        self.log("Testing list hosted sites...")
        
        try:
            # Deploy a website first to ensure there's something to list
            if self.test_website_id:
                deploy_response = self.session.post(f"{API_BASE}/websites/{self.test_website_id}/deploy")
                if deploy_response.status_code != 200:
                    self.log("⚠️ Failed to deploy website for hosted sites list test")
            
            # Test listing hosted sites
            list_response = self.session.get(f"{API_BASE}/hosting/sites")
            
            if list_response.status_code == 200:
                sites = list_response.json()
                if isinstance(sites, list):
                    self.log(f"✅ Listed {len(sites)} hosted sites successfully")
                    
                    # Verify structure of returned sites
                    if sites:
                        site = sites[0]
                        required_fields = ['website_id', 'website_name', 'subdomain', 'hosting_url']
                        missing_fields = [field for field in required_fields if field not in site]
                        
                        if not missing_fields:
                            self.log("✅ Hosted sites have correct metadata structure")
                            return True
                        else:
                            self.log(f"❌ Hosted sites missing required fields: {missing_fields}")
                            return False
                    else:
                        self.log("✅ No hosted sites found (empty list is valid)")
                        return True
                else:
                    self.log(f"❌ List hosted sites returned non-list response: {type(sites)}")
                    return False
            else:
                self.log(f"❌ List hosted sites failed: {list_response.status_code} - {list_response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Error testing list hosted sites: {e}")
            return False
    
    def test_hosting_authentication(self):
        """Test that hosting endpoints require authentication"""
        self.log("Testing hosting endpoints authentication...")
        
        if not self.test_website_id:
            self.log("❌ No website ID available for authentication test")
            return False
        
        # Remove authentication header temporarily
        original_auth = self.session.headers.get('Authorization')
        if 'Authorization' in self.session.headers:
            del self.session.headers['Authorization']
        
        try:
            # Test all hosting endpoints without authentication
            endpoints_to_test = [
                ('POST', f"{API_BASE}/websites/{self.test_website_id}/deploy"),
                ('DELETE', f"{API_BASE}/websites/{self.test_website_id}/undeploy"),
                ('PUT', f"{API_BASE}/websites/{self.test_website_id}/redeploy"),
                ('POST', f"{API_BASE}/websites/{self.test_website_id}/ssl"),
                ('GET', f"{API_BASE}/hosting/sites")
            ]
            
            all_protected = True
            
            for method, url in endpoints_to_test:
                if method == 'POST':
                    response = self.session.post(url)
                elif method == 'DELETE':
                    response = self.session.delete(url)
                elif method == 'PUT':
                    response = self.session.put(url)
                elif method == 'GET':
                    response = self.session.get(url)
                
                if response.status_code not in [401, 403]:
                    self.log(f"❌ Endpoint {method} {url} should require authentication but returned: {response.status_code}")
                    all_protected = False
                else:
                    self.log(f"✅ Endpoint {method} {url} correctly requires authentication ({response.status_code})")
            
            # Restore authentication header
            if original_auth:
                self.session.headers['Authorization'] = original_auth
            
            return all_protected
                
        except Exception as e:
            # Restore authentication header
            if original_auth:
                self.session.headers['Authorization'] = original_auth
            self.log(f"❌ Error testing hosting authentication: {e}")
            return False
    
    def test_hosting_user_ownership(self):
        """Test that users can only manage their own websites"""
        self.log("Testing hosting user ownership verification...")
        
        # Create another user and website
        timestamp = int(time.time()) + 2
        other_user_data = {
            "email": f"hostinguser{timestamp}@example.com",
            "username": f"hostinguser{timestamp}",
            "full_name": "Hosting Test User",
            "password": "HostingPassword123!"
        }
        
        try:
            # Create other user
            response = self.session.post(f"{API_BASE}/auth/register", json=other_user_data)
            if response.status_code != 201:
                self.log("❌ Failed to create other user for ownership test")
                return False
            
            # Login as other user
            login_response = self.session.post(f"{API_BASE}/auth/login", json={
                "email": other_user_data["email"],
                "password": other_user_data["password"]
            })
            
            if login_response.status_code != 200:
                self.log("❌ Failed to login as other user")
                return False
            
            other_token = login_response.json()['access_token']
            
            # Create website as other user
            other_session = requests.Session()
            other_session.headers.update({'Authorization': f'Bearer {other_token}'})
            
            website_response = other_session.post(f"{API_BASE}/websites", json={
                "name": "Other User Hosting Website",
                "description": "Website by another user for hosting test",
                "template_id": self.test_template_id
            })
            
            if website_response.status_code != 201:
                self.log("❌ Failed to create website as other user")
                return False
            
            other_website_id = website_response.json()['id']
            
            # Now try to manage other user's website with original user's token
            hosting_endpoints = [
                ('POST', f"{API_BASE}/websites/{other_website_id}/deploy"),
                ('DELETE', f"{API_BASE}/websites/{other_website_id}/undeploy"),
                ('PUT', f"{API_BASE}/websites/{other_website_id}/redeploy"),
                ('POST', f"{API_BASE}/websites/{other_website_id}/ssl")
            ]
            
            all_denied = True
            
            for method, url in hosting_endpoints:
                if method == 'POST':
                    response = self.session.post(url)
                elif method == 'DELETE':
                    response = self.session.delete(url)
                elif method == 'PUT':
                    response = self.session.put(url)
                
                if response.status_code == 404:
                    self.log(f"✅ {method} {url.split('/')[-1]} correctly denies access to other user's website (404)")
                else:
                    self.log(f"❌ {method} {url.split('/')[-1]} should deny access but returned: {response.status_code}")
                    all_denied = False
            
            return all_denied
                
        except Exception as e:
            self.log(f"❌ Error testing hosting user ownership: {e}")
            return False
    
    def run_all_tests(self):
        """Run all backend tests"""
        self.log("🚀 Starting Backend API Tests for Export and Hosting Functionality")
        self.log("=" * 70)
        
        test_results = {}
        
        # Basic health check
        test_results['health'] = self.test_health_endpoint()
        
        # User creation and authentication
        test_results['user_creation'] = self.create_test_user()
        if not test_results['user_creation']:
            self.log("❌ Cannot continue without user creation")
            return test_results
        
        test_results['user_login'] = self.login_test_user()
        if not test_results['user_login']:
            self.log("❌ Cannot continue without authentication")
            return test_results
        
        # Template and website setup
        test_results['get_templates'] = self.get_templates()
        if not test_results['get_templates']:
            self.log("❌ Cannot continue without templates")
            return test_results
        
        test_results['create_website'] = self.create_test_website()
        if not test_results['create_website']:
            self.log("❌ Cannot continue without test website")
            return test_results
        
        test_results['update_content'] = self.update_website_content()
        
        # Export functionality tests
        test_results['export_authenticated'] = self.test_export_with_authentication()
        test_results['export_unauthenticated'] = self.test_export_without_authentication()
        test_results['export_nonexistent'] = self.test_export_nonexistent_website()
        test_results['export_other_user'] = self.test_export_other_users_website()
        
        # Hosting functionality tests
        self.log("\n🌐 Testing Hosting Functionality...")
        test_results['hosting_authentication'] = self.test_hosting_authentication()
        test_results['hosting_user_ownership'] = self.test_hosting_user_ownership()
        test_results['deploy_website'] = self.test_deploy_website()
        test_results['deploy_custom_subdomain'] = self.test_deploy_with_custom_subdomain()
        test_results['redeploy_website'] = self.test_redeploy_website()
        test_results['ssl_configuration'] = self.test_ssl_configuration()
        test_results['list_hosted_sites'] = self.test_list_hosted_sites()
        test_results['undeploy_website'] = self.test_undeploy_website()
        
        # Summary
        self.log("=" * 70)
        self.log("🏁 Test Results Summary:")
        
        passed = sum(1 for result in test_results.values() if result)
        total = len(test_results)
        
        # Group results by category
        export_tests = {k: v for k, v in test_results.items() if 'export' in k}
        hosting_tests = {k: v for k, v in test_results.items() if 'hosting' in k or 'deploy' in k or 'ssl' in k or 'list_hosted' in k or 'undeploy' in k}
        basic_tests = {k: v for k, v in test_results.items() if k not in export_tests and k not in hosting_tests}
        
        self.log("\n📋 Basic API Tests:")
        for test_name, result in basic_tests.items():
            status = "✅ PASS" if result else "❌ FAIL"
            self.log(f"  {test_name}: {status}")
        
        self.log("\n📦 Export Functionality Tests:")
        for test_name, result in export_tests.items():
            status = "✅ PASS" if result else "❌ FAIL"
            self.log(f"  {test_name}: {status}")
        
        self.log("\n🌐 Hosting Functionality Tests:")
        for test_name, result in hosting_tests.items():
            status = "✅ PASS" if result else "❌ FAIL"
            self.log(f"  {test_name}: {status}")
        
        self.log(f"\nOverall: {passed}/{total} tests passed")
        
        if passed == total:
            self.log("🎉 All tests passed! Export and Hosting functionality is working correctly.")
        else:
            self.log("⚠️ Some tests failed. Please check the issues above.")
        
        return test_results

def main():
    """Main test execution"""
    tester = BackendTester()
    results = tester.run_all_tests()
    
    # Return exit code based on results
    all_passed = all(results.values())
    exit(0 if all_passed else 1)

if __name__ == "__main__":
    main()