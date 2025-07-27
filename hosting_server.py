#!/usr/bin/env python3
"""
Serveur HTTP simple pour servir les sites hébergés
Port 3001 pour les sites hébergés
"""
import http.server
import socketserver
import os
from pathlib import Path
import json
from urllib.parse import urlparse

class HostedSiteHandler(http.server.SimpleHTTPRequestHandler):
    """Handler personnalisé pour servir les sites hébergés"""
    
    def __init__(self, *args, **kwargs):
        self.hosting_root = Path("/app/hosted_sites")
        super().__init__(*args, directory=str(self.hosting_root), **kwargs)
    
    def do_GET(self):
        """Handle GET requests for hosted sites"""
        host_header = self.headers.get('Host', '')
        
        # Parse subdomain from host header
        if '.' in host_header:
            subdomain = host_header.split('.')[0]
            
            # Check if subdomain exists
            site_path = self.hosting_root / subdomain
            if site_path.exists() and site_path.is_dir():
                # Serve the site
                requested_path = self.path.lstrip('/')
                if not requested_path or requested_path == '/':
                    requested_path = 'index.html'
                
                file_path = site_path / requested_path
                
                if file_path.exists() and file_path.is_file():
                    # Serve the file
                    self.send_response(200)
                    
                    # Set content type based on file extension
                    if file_path.suffix == '.html':
                        self.send_header('Content-type', 'text/html')
                    elif file_path.suffix == '.css':
                        self.send_header('Content-type', 'text/css')
                    elif file_path.suffix == '.js':
                        self.send_header('Content-type', 'application/javascript')
                    elif file_path.suffix == '.png':
                        self.send_header('Content-type', 'image/png')
                    elif file_path.suffix == '.jpg' or file_path.suffix == '.jpeg':
                        self.send_header('Content-type', 'image/jpeg')
                    else:
                        self.send_header('Content-type', 'text/plain')
                    
                    self.end_headers()
                    
                    with open(file_path, 'rb') as f:
                        self.wfile.write(f.read())
                    return
                else:
                    # File not found
                    self.send_error(404, f"File not found: {requested_path}")
                    return
            else:
                # Subdomain not found
                self.send_error(404, f"Site not found: {subdomain}")
                return
        
        # Default response for invalid requests
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        welcome_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Hébergement de Sites IA</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .container { max-width: 600px; margin: 0 auto; text-align: center; }
                h1 { color: #333; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🌐 Hébergement de Sites IA</h1>
                <p>Serveur d'hébergement pour les sites générés par l'IA</p>
                <p>Pour accéder à un site, utilisez: <strong>http://[sous-domaine].localhost:3001</strong></p>
            </div>
        </body>
        </html>
        """
        self.wfile.write(welcome_html.encode())

def start_hosting_server():
    """Démarre le serveur d'hébergement"""
    PORT = 3001
    
    with socketserver.TCPServer(("", PORT), HostedSiteHandler) as httpd:
        print(f"🌐 Serveur d'hébergement démarré sur le port {PORT}")
        print(f"📁 Dossier racine: /app/hosted_sites")
        print(f"🔗 Format d'accès: http://[subdomain].localhost:3001")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Serveur d'hébergement arrêté")

if __name__ == "__main__":
    start_hosting_server()