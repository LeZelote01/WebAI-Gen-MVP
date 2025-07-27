"""
Website Export Module
Handles the generation of clean HTML/CSS/JS code from website data
"""
import os
import json
import zipfile
from typing import Dict, Any, Optional
from io import BytesIO
from datetime import datetime
from jinja2 import Template, Environment, DictLoader

class WebsiteExporter:
    """Class to handle website export functionality"""
    
    def __init__(self):
        # HTML template for exported websites
        self.html_template = """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{{ meta_description or description or 'Site web généré avec AI Website Generator' }}">
    <meta name="keywords" content="{{ meta_keywords or '' }}">
    <title>{{ meta_title or name or 'Mon Site Web' }}</title>
    
    <!-- Generated with AI Website Generator -->
    <meta name="generator" content="AI Website Generator - https://ai-webgen.com">
    
    <!-- TailwindCSS CDN for styling -->
    <script src="https://cdn.tailwindcss.com"></script>
    
    <!-- Custom CSS -->
    <style>
        {{ custom_css }}
        
        /* Default styles for common components */
        .hero-section {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        
        .btn-primary {
            @apply bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors;
        }
        
        .btn-secondary {
            @apply border border-blue-600 text-blue-600 px-6 py-3 rounded-lg font-semibold hover:bg-blue-50 transition-colors;
        }
        
        .section-padding {
            @apply py-16 px-4 sm:px-6 lg:px-8;
        }
        
        .container {
            @apply max-w-7xl mx-auto;
        }
        
        .card {
            @apply bg-white rounded-lg shadow-sm p-6;
        }
    </style>
</head>
<body class="bg-gray-50">
    {{ html_content }}
    
    <!-- Custom JavaScript -->
    <script>
        {{ custom_js }}
        
        // Default interaction scripts
        document.addEventListener('DOMContentLoaded', function() {
            // Mobile menu toggle
            const mobileMenuButton = document.querySelector('[data-mobile-menu-button]');
            const mobileMenu = document.querySelector('[data-mobile-menu]');
            
            if (mobileMenuButton && mobileMenu) {
                mobileMenuButton.addEventListener('click', function() {
                    mobileMenu.classList.toggle('hidden');
                });
            }
            
            // Smooth scrolling for anchor links
            document.querySelectorAll('a[href^="#"]').forEach(anchor => {
                anchor.addEventListener('click', function (e) {
                    e.preventDefault();
                    const target = document.querySelector(this.getAttribute('href'));
                    if (target) {
                        target.scrollIntoView({
                            behavior: 'smooth'
                        });
                    }
                });
            });
        });
    </script>
</body>
</html>"""

        # Default HTML structures for different template types
        self.template_structures = {
            "portfolio": self._get_portfolio_html(),
            "business": self._get_business_html(),
            "blog": self._get_blog_html(),
            "landing": self._get_landing_html(),
            "ecommerce": self._get_ecommerce_html()
        }

    def export_website(self, website_data: Dict[str, Any], template_data: Optional[Dict[str, Any]] = None) -> BytesIO:
        """
        Export a website as a ZIP file containing HTML, CSS, and JS
        """
        # Generate the HTML content
        html_content = self._generate_html_content(website_data, template_data)
        
        # Create ZIP file in memory
        zip_buffer = BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Add main HTML file
            zip_file.writestr('index.html', html_content)
            
            # Add CSS file if custom CSS exists
            if website_data.get('custom_css'):
                zip_file.writestr('assets/style.css', website_data['custom_css'])
            
            # Add JS file if custom JS exists
            if website_data.get('custom_js'):
                zip_file.writestr('assets/script.js', website_data['custom_js'])
            
            # Add README file
            readme_content = self._generate_readme(website_data)
            zip_file.writestr('README.md', readme_content)
            
            # Add deployment guide
            deployment_guide = self._generate_deployment_guide()
            zip_file.writestr('DEPLOYMENT.md', deployment_guide)
        
        zip_buffer.seek(0)
        return zip_buffer

    def _generate_html_content(self, website_data: Dict[str, Any], template_data: Optional[Dict[str, Any]] = None) -> str:
        """Generate the complete HTML content"""
        
        # Get template structure
        template_category = "business"  # default
        if template_data and template_data.get('category'):
            template_category = template_data['category']
        
        # Get the HTML structure for this template type
        html_body = self.template_structures.get(template_category, self.template_structures["business"])
        
        # Render with website content
        if website_data.get('content'):
            html_body = self._render_content_in_template(html_body, website_data['content'])
        
        # Create Jinja2 template and render
        template = Template(self.html_template)
        
        return template.render(
            name=website_data.get('name', 'Mon Site Web'),
            description=website_data.get('description', ''),
            meta_title=website_data.get('meta_title', ''),
            meta_description=website_data.get('meta_description', ''),
            meta_keywords=website_data.get('meta_keywords', ''),
            custom_css=website_data.get('custom_css', ''),
            custom_js=website_data.get('custom_js', ''),
            html_content=html_body
        )

    def _render_content_in_template(self, html_template: str, content: Dict[str, Any]) -> str:
        """Replace template placeholders with actual content"""
        
        # Replace common content placeholders
        replacements = {
            '{{SITE_TITLE}}': content.get('hero', {}).get('title', 'Mon Site Web'),
            '{{SITE_SUBTITLE}}': content.get('hero', {}).get('subtitle', 'Bienvenue sur mon site'),
            '{{SITE_DESCRIPTION}}': content.get('hero', {}).get('description', 'Description de mon site web'),
            '{{ABOUT_TITLE}}': content.get('about', {}).get('title', 'À propos'),
            '{{ABOUT_CONTENT}}': content.get('about', {}).get('content', 'Contenu à propos...'),
            '{{CONTACT_TITLE}}': 'Contact',
            '{{CURRENT_YEAR}}': str(datetime.now().year)
        }
        
        # Apply replacements
        for placeholder, value in replacements.items():
            html_template = html_template.replace(placeholder, str(value))
        
        return html_template

    def _generate_readme(self, website_data: Dict[str, Any]) -> str:
        """Generate README.md file for the exported website"""
        return f"""# {website_data.get('name', 'Mon Site Web')}

{website_data.get('description', 'Site web généré avec AI Website Generator')}

## 📋 Informations

- **Nom du site :** {website_data.get('name', 'Mon Site Web')}
- **Description :** {website_data.get('description', 'Aucune description')}
- **Généré le :** {datetime.now().strftime('%d/%m/%Y à %H:%M')}
- **Générateur :** AI Website Generator

## 🚀 Déploiement

Ce site est prêt à être déployé ! Consultez le fichier `DEPLOYMENT.md` pour les instructions détaillées.

### Déploiement rapide

Vous pouvez déployer ce site sur :

- **Netlify** : Glissez-déposez le dossier sur [netlify.com/drop](https://netlify.com/drop)
- **Vercel** : Utilisez la commande `vercel --prod`
- **GitHub Pages** : Poussez vers un repository GitHub et activez Pages
- **Serveur web** : Copiez les fichiers dans le dossier public de votre serveur

## 📁 Structure des fichiers

```
/
├── index.html          # Page principale
├── assets/
│   ├── style.css      # Styles personnalisés (si présents)
│   └── script.js      # Scripts personnalisés (si présents)
├── README.md          # Ce fichier
└── DEPLOYMENT.md      # Guide de déploiement
```

## 🛠️ Personnalisation

- Modifiez `index.html` pour changer le contenu
- Ajoutez vos styles dans `assets/style.css`
- Ajoutez vos scripts dans `assets/script.js`

## 📞 Support

Site généré avec AI Website Generator.
Pour plus d'aide, consultez notre documentation.
"""

    def _generate_deployment_guide(self) -> str:
        """Generate deployment guide"""
        return """# 🚀 Guide de Déploiement

Ce guide vous explique comment déployer votre site web sur différentes plateformes.

## 📋 Prérequis

Votre site est entièrement statique et peut être hébergé sur n'importe quelle plateforme supportant les sites statiques.

## 🌟 Plateformes recommandées

### 1. Netlify (Recommandé)

**Déploiement par glisser-déposer :**
1. Allez sur [netlify.com](https://netlify.com)
2. Créez un compte gratuit
3. Glissez-déposez le dossier de votre site dans Netlify Drop
4. Votre site sera automatiquement déployé !

**Déploiement via Git :**
1. Poussez votre code sur GitHub/GitLab
2. Connectez votre repository à Netlify
3. Le déploiement se fera automatiquement

### 2. Vercel

1. Installez Vercel CLI : `npm i -g vercel`
2. Dans le dossier de votre site : `vercel --prod`
3. Suivez les instructions

### 3. GitHub Pages

1. Créez un repository GitHub
2. Poussez vos fichiers
3. Allez dans Settings > Pages
4. Sélectionnez la branche source
5. Votre site sera disponible sur `username.github.io/repository`

### 4. Serveur Web Traditional

**Apache/Nginx :**
1. Copiez tous les fichiers dans le dossier public de votre serveur
2. Assurez-vous que `index.html` est reconnu comme page d'accueil
3. Votre site est prêt !

## 🔧 Configuration Avancée

### Domaine Personnalisé

**Netlify :**
1. Allez dans Site settings > Domain management
2. Ajoutez votre domaine personnalisé
3. Configurez les DNS selon les instructions

**Vercel :**
1. Allez dans Project Settings > Domains
2. Ajoutez votre domaine
3. Configurez les DNS

### SSL/HTTPS

La plupart des plateformes (Netlify, Vercel, GitHub Pages) fournissent automatiquement le SSL.

### Optimisations

- **Compression** : Activée automatiquement sur Netlify/Vercel
- **CDN** : Fourni automatiquement
- **Cache** : Configuré automatiquement

## 🚨 Dépannage

### Site ne s'affiche pas correctement
- Vérifiez que `index.html` est à la racine
- Vérifiez les chemins des fichiers CSS/JS

### Erreur 404
- Assurez-vous que le serveur est configuré pour servir `index.html`
- Vérifiez les permissions des fichiers

### Problèmes de style
- Vérifiez que TailwindCSS se charge depuis le CDN
- Vérifiez le fichier `assets/style.css` s'il existe

## 📞 Support

Pour plus d'aide :
1. Consultez la documentation de votre plateforme d'hébergement
2. Contactez le support AI Website Generator
3. Vérifiez notre FAQ en ligne

---

*Généré avec AI Website Generator - Votre partenaire pour créer des sites web professionnels*
"""

    def _get_portfolio_html(self) -> str:
        """Get HTML structure for portfolio template"""
        return """
    <!-- Navigation -->
    <nav class="bg-white shadow-sm">
        <div class="container">
            <div class="flex items-center justify-between h-16">
                <div class="font-bold text-xl text-gray-900">{{SITE_TITLE}}</div>
                <div class="hidden md:flex space-x-8">
                    <a href="#home" class="text-gray-700 hover:text-blue-600">Accueil</a>
                    <a href="#about" class="text-gray-700 hover:text-blue-600">À propos</a>
                    <a href="#portfolio" class="text-gray-700 hover:text-blue-600">Portfolio</a>
                    <a href="#contact" class="text-gray-700 hover:text-blue-600">Contact</a>
                </div>
                <button data-mobile-menu-button class="md:hidden">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path>
                    </svg>
                </button>
            </div>
            <div data-mobile-menu class="hidden md:hidden">
                <div class="px-2 pt-2 pb-3 space-y-1">
                    <a href="#home" class="block px-3 py-2 text-gray-700">Accueil</a>
                    <a href="#about" class="block px-3 py-2 text-gray-700">À propos</a>  
                    <a href="#portfolio" class="block px-3 py-2 text-gray-700">Portfolio</a>
                    <a href="#contact" class="block px-3 py-2 text-gray-700">Contact</a>
                </div>
            </div>
        </div>
    </nav>

    <!-- Hero Section -->
    <section id="home" class="hero-section text-white section-padding">
        <div class="container text-center">
            <h1 class="text-4xl md:text-6xl font-bold mb-4">{{SITE_TITLE}}</h1>
            <p class="text-xl md:text-2xl mb-2">{{SITE_SUBTITLE}}</p>
            <p class="text-lg mb-8 max-w-2xl mx-auto">{{SITE_DESCRIPTION}}</p>
            <div class="space-x-4">
                <a href="#portfolio" class="btn-primary">Voir mon travail</a>
                <a href="#contact" class="btn-secondary bg-white text-blue-600 hover:bg-gray-100">Me contacter</a>
            </div>
        </div>
    </section>

    <!-- About Section -->
    <section id="about" class="section-padding bg-white">
        <div class="container">
            <div class="max-w-4xl mx-auto text-center">
                <h2 class="text-3xl font-bold text-gray-900 mb-8">{{ABOUT_TITLE}}</h2>
                <p class="text-lg text-gray-600 leading-relaxed">{{ABOUT_CONTENT}}</p>
            </div>
        </div>
    </section>

    <!-- Portfolio Section -->
    <section id="portfolio" class="section-padding">
        <div class="container">
            <h2 class="text-3xl font-bold text-gray-900 text-center mb-12">Mes Projets</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                <div class="card hover:shadow-lg transition-shadow">
                    <div class="bg-gray-200 h-48 rounded-lg mb-4"></div>
                    <h3 class="text-xl font-semibold mb-2">Projet 1</h3>
                    <p class="text-gray-600">Description du projet...</p>
                </div>
                <div class="card hover:shadow-lg transition-shadow">
                    <div class="bg-gray-200 h-48 rounded-lg mb-4"></div>
                    <h3 class="text-xl font-semibold mb-2">Projet 2</h3>
                    <p class="text-gray-600">Description du projet...</p>
                </div>
                <div class="card hover:shadow-lg transition-shadow">
                    <div class="bg-gray-200 h-48 rounded-lg mb-4"></div>
                    <h3 class="text-xl font-semibold mb-2">Projet 3</h3>
                    <p class="text-gray-600">Description du projet...</p>
                </div>
            </div>
        </div>
    </section>

    <!-- Contact Section -->
    <section id="contact" class="section-padding bg-white">
        <div class="container">
            <div class="max-w-2xl mx-auto text-center">
                <h2 class="text-3xl font-bold text-gray-900 mb-8">{{CONTACT_TITLE}}</h2>
                <p class="text-lg text-gray-600 mb-8">Interessé par une collaboration ? Contactez-moi !</p>
                <div class="space-y-4">
                    <a href="mailto:contact@example.com" class="btn-primary inline-block">Envoyer un email</a>
                </div>
            </div>
        </div>
    </section>

    <!-- Footer -->
    <footer class="bg-gray-900 text-white section-padding">
        <div class="container text-center">
            <p>&copy; {{CURRENT_YEAR}} {{SITE_TITLE}}. Tous droits réservés.</p>
            <p class="text-sm text-gray-400 mt-2">Site créé avec AI Website Generator</p>
        </div>
    </footer>
        """

    def _get_business_html(self) -> str:
        """Get HTML structure for business template"""
        return """
    <!-- Navigation -->
    <nav class="bg-white shadow-sm">
        <div class="container">
            <div class="flex items-center justify-between h-16">
                <div class="font-bold text-xl text-gray-900">{{SITE_TITLE}}</div>
                <div class="hidden md:flex space-x-8">
                    <a href="#home" class="text-gray-700 hover:text-blue-600">Accueil</a>
                    <a href="#services" class="text-gray-700 hover:text-blue-600">Services</a>
                    <a href="#about" class="text-gray-700 hover:text-blue-600">À propos</a>
                    <a href="#contact" class="text-gray-700 hover:text-blue-600">Contact</a>
                </div>
                <button data-mobile-menu-button class="md:hidden">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path>
                    </svg>
                </button>
            </div>
            <div data-mobile-menu class="hidden md:hidden">
                <div class="px-2 pt-2 pb-3 space-y-1">
                    <a href="#home" class="block px-3 py-2 text-gray-700">Accueil</a>
                    <a href="#services" class="block px-3 py-2 text-gray-700">Services</a>
                    <a href="#about" class="block px-3 py-2 text-gray-700">À propos</a>
                    <a href="#contact" class="block px-3 py-2 text-gray-700">Contact</a>
                </div>
            </div>
        </div>
    </nav>

    <!-- Hero Section -->
    <section id="home" class="hero-section text-white section-padding">
        <div class="container">
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
                <div>
                    <h1 class="text-4xl md:text-5xl font-bold mb-6">{{SITE_TITLE}}</h1>
                    <p class="text-xl mb-4">{{SITE_SUBTITLE}}</p>
                    <p class="text-lg mb-8">{{SITE_DESCRIPTION}}</p>
                    <div class="space-x-4">
                        <a href="#services" class="btn-primary">Nos Services</a>
                        <a href="#contact" class="btn-secondary bg-white text-blue-600 hover:bg-gray-100">Nous contacter</a>
                    </div>
                </div>
                <div>
                    <div class="bg-white bg-opacity-20 rounded-lg p-8 text-center">
                        <svg class="w-24 h-24 mx-auto mb-4" fill="currentColor" viewBox="0 0 20 20">
                            <path d="M13 6a3 3 0 11-6 0 3 3 0 016 0zM18 8a2 2 0 11-4 0 2 2 0 014 0zM14 15a4 4 0 00-8 0v3h8v-3z"></path>
                        </svg>
                        <h3 class="text-xl font-semibold">Excellence & Innovation</h3>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Services Section -->
    <section id="services" class="section-padding bg-white">
        <div class="container">
            <div class="text-center mb-12">
                <h2 class="text-3xl font-bold text-gray-900 mb-4">Nos Services</h2>
                <p class="text-lg text-gray-600 max-w-2xl mx-auto">Découvrez notre gamme complète de services professionnels</p>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                <div class="card text-center hover:shadow-lg transition-shadow">
                    <div class="w-16 h-16 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                        <svg class="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path>
                        </svg>
                    </div>
                    <h3 class="text-xl font-semibold mb-3">Conseil Stratégique</h3>
                    <p class="text-gray-600">Accompagnement personnalisé pour développer votre stratégie d'entreprise.</p>
                </div>
                <div class="card text-center hover:shadow-lg transition-shadow">
                    <div class="w-16 h-16 bg-green-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                        <svg class="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
                        </svg>
                    </div>
                    <h3 class="text-xl font-semibold mb-3">Solutions Techniques</h3>
                    <p class="text-gray-600">Développement et mise en place de solutions techniques innovantes.</p>
                </div>
                <div class="card text-center hover:shadow-lg transition-shadow">
                    <div class="w-16 h-16 bg-purple-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                        <svg class="w-8 h-8 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"></path>
                        </svg>
                    </div>
                    <h3 class="text-xl font-semibold mb-3">Support Client</h3>
                    <p class="text-gray-600">Un support client réactif et professionnel pour tous vos besoins.</p>
                </div>
            </div>
        </div>
    </section>

    <!-- About Section -->
    <section id="about" class="section-padding">
        <div class="container">
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
                <div>
                    <h2 class="text-3xl font-bold text-gray-900 mb-6">{{ABOUT_TITLE}}</h2>
                    <p class="text-lg text-gray-600 mb-6">{{ABOUT_CONTENT}}</p>
                    <div class="space-y-4">
                        <div class="flex items-center">
                            <svg class="w-6 h-6 text-green-500 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                            </svg>
                            <span>Plus de 10 ans d'expérience</span>
                        </div>
                        <div class="flex items-center">
                            <svg class="w-6 h-6 text-green-500 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                            </svg>
                            <span>Équipe d'experts qualifiés</span>
                        </div>
                        <div class="flex items-center">
                            <svg class="w-6 h-6 text-green-500 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                            </svg>
                            <span>Solutions sur mesure</span>
                        </div>
                    </div>
                </div>
                <div>
                    <div class="bg-gray-200 h-96 rounded-lg"></div>
                </div>
            </div>
        </div>
    </section>

    <!-- Contact Section -->
    <section id="contact" class="section-padding bg-white">
        <div class="container">
            <div class="max-w-4xl mx-auto">
                <div class="text-center mb-12">
                    <h2 class="text-3xl font-bold text-gray-900 mb-4">{{CONTACT_TITLE}}</h2>
                    <p class="text-lg text-gray-600">Prêt à démarrer votre projet ? Contactez-nous dès aujourd'hui !</p>
                </div>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
                    <div>
                        <h3 class="text-xl font-semibold mb-4">Informations de contact</h3>
                        <div class="space-y-4">
                            <div class="flex items-center">
                                <svg class="w-6 h-6 text-blue-600 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path>
                                </svg>
                                <span>contact@example.com</span>
                            </div>
                            <div class="flex items-center">
                                <svg class="w-6 h-6 text-blue-600 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"></path>
                                </svg>
                                <span>+33 1 23 45 67 89</span>
                            </div>
                            <div class="flex items-center">
                                <svg class="w-6 h-6 text-blue-600 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path>
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path>
                                </svg>
                                <span>123 Rue Example, 75001 Paris</span>
                            </div>
                        </div>
                    </div>
                    <div>
                        <a href="mailto:contact@example.com" class="btn-primary block text-center">Nous contacter</a>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Footer -->
    <footer class="bg-gray-900 text-white section-padding">
        <div class="container text-center">
            <div class="mb-8">
                <h3 class="text-2xl font-bold mb-4">{{SITE_TITLE}}</h3>
                <p class="text-gray-400">{{SITE_DESCRIPTION}}</p>
            </div>
            <div class="border-t border-gray-800 pt-8">
                <p>&copy; {{CURRENT_YEAR}} {{SITE_TITLE}}. Tous droits réservés.</p>
                <p class="text-sm text-gray-400 mt-2">Site créé avec AI Website Generator</p>
            </div>
        </div>
    </footer>
        """

    def _get_blog_html(self) -> str:
        """Get HTML structure for blog template"""
        return """
    <!-- Navigation -->
    <nav class="bg-white shadow-sm">
        <div class="container">
            <div class="flex items-center justify-between h-16">
                <div class="font-bold text-xl text-gray-900">{{SITE_TITLE}}</div>
                <div class="hidden md:flex space-x-8">
                    <a href="#home" class="text-gray-700 hover:text-blue-600">Accueil</a>
                    <a href="#posts" class="text-gray-700 hover:text-blue-600">Articles</a>
                    <a href="#about" class="text-gray-700 hover:text-blue-600">À propos</a>
                    <a href="#contact" class="text-gray-700 hover:text-blue-600">Contact</a>
                </div>
            </div>
        </div>
    </nav>

    <!-- Hero Section -->
    <section id="home" class="hero-section text-white section-padding">
        <div class="container text-center">
            <h1 class="text-4xl md:text-6xl font-bold mb-4">{{SITE_TITLE}}</h1>
            <p class="text-xl md:text-2xl mb-2">{{SITE_SUBTITLE}}</p>
            <p class="text-lg mb-8 max-w-2xl mx-auto">{{SITE_DESCRIPTION}}</p>
            <a href="#posts" class="btn-primary">Lire les articles</a>
        </div>
    </section>

    <!-- Posts Section -->
    <section id="posts" class="section-padding bg-white">
        <div class="container">
            <h2 class="text-3xl font-bold text-gray-900 text-center mb-12">Derniers Articles</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                <article class="card hover:shadow-lg transition-shadow">
                    <div class="bg-gray-200 h-48 rounded-lg mb-4"></div>
                    <div class="text-sm text-blue-600 mb-2">15 Janvier 2024</div>
                    <h3 class="text-xl font-semibold mb-3">Premier article du blog</h3>
                    <p class="text-gray-600 mb-4">Lorem ipsum dolor sit amet, consectetur adipiscing elit...</p>
                    <a href="#" class="text-blue-600 font-semibold hover:text-blue-800">Lire la suite →</a>
                </article>
                <article class="card hover:shadow-lg transition-shadow">
                    <div class="bg-gray-200 h-48 rounded-lg mb-4"></div>
                    <div class="text-sm text-blue-600 mb-2">10 Janvier 2024</div>
                    <h3 class="text-xl font-semibold mb-3">Deuxième article</h3>
                    <p class="text-gray-600 mb-4">Lorem ipsum dolor sit amet, consectetur adipiscing elit...</p>
                    <a href="#" class="text-blue-600 font-semibold hover:text-blue-800">Lire la suite →</a>
                </article>
                <article class="card hover:shadow-lg transition-shadow">
                    <div class="bg-gray-200 h-48 rounded-lg mb-4"></div>
                    <div class="text-sm text-blue-600 mb-2">5 Janvier 2024</div>
                    <h3 class="text-xl font-semibold mb-3">Troisième article</h3>
                    <p class="text-gray-600 mb-4">Lorem ipsum dolor sit amet, consectetur adipiscing elit...</p>
                    <a href="#" class="text-blue-600 font-semibold hover:text-blue-800">Lire la suite →</a>
                </article>
            </div>
        </div>
    </section>

    <!-- About Section -->
    <section id="about" class="section-padding">
        <div class="container">
            <div class="max-w-4xl mx-auto text-center">
                <h2 class="text-3xl font-bold text-gray-900 mb-8">{{ABOUT_TITLE}}</h2>
                <div class="bg-gray-200 w-32 h-32 rounded-full mx-auto mb-6"></div>
                <p class="text-lg text-gray-600 leading-relaxed">{{ABOUT_CONTENT}}</p>
            </div>
        </div>
    </section>

    <!-- Footer -->
    <footer class="bg-gray-900 text-white section-padding">
        <div class="container text-center">
            <p>&copy; {{CURRENT_YEAR}} {{SITE_TITLE}}. Tous droits réservés.</p>
            <p class="text-sm text-gray-400 mt-2">Site créé avec AI Website Generator</p>
        </div>
    </footer>
        """

    def _get_landing_html(self) -> str:
        """Get HTML structure for landing page template"""
        return """
    <!-- Navigation -->
    <nav class="bg-white shadow-sm">
        <div class="container">
            <div class="flex items-center justify-between h-16">
                <div class="font-bold text-xl text-gray-900">{{SITE_TITLE}}</div>
                <div class="hidden md:flex space-x-8">
                    <a href="#home" class="text-gray-700 hover:text-blue-600">Accueil</a>
                    <a href="#features" class="text-gray-700 hover:text-blue-600">Fonctionnalités</a>
                    <a href="#pricing" class="text-gray-700 hover:text-blue-600">Tarifs</a>
                    <a href="#contact" class="text-gray-700 hover:text-blue-600">Contact</a>
                </div>
                <a href="#" class="btn-primary">Commencer</a>
            </div>
        </div>
    </nav>

    <!-- Hero Section -->
    <section id="home" class="hero-section text-white section-padding">
        <div class="container text-center">
            <h1 class="text-4xl md:text-6xl font-bold mb-6">{{SITE_TITLE}}</h1>
            <p class="text-xl md:text-2xl mb-4">{{SITE_SUBTITLE}}</p>
            <p class="text-lg mb-8 max-w-3xl mx-auto">{{SITE_DESCRIPTION}}</p>
            <div class="space-x-4">
                <a href="#" class="btn-primary">Essai Gratuit</a>
                <a href="#features" class="btn-secondary bg-white text-blue-600 hover:bg-gray-100">En savoir plus</a>
            </div>
        </div>
    </section>

    <!-- Features Section -->
    <section id="features" class="section-padding bg-white">
        <div class="container">
            <div class="text-center mb-12">
                <h2 class="text-3xl font-bold text-gray-900 mb-4">Fonctionnalités</h2>
                <p class="text-lg text-gray-600 max-w-2xl mx-auto">Découvrez tout ce que notre solution peut faire pour vous</p>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
                <div class="text-center">
                    <div class="w-16 h-16 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                        <svg class="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
                        </svg>
                    </div>
                    <h3 class="text-xl font-semibold mb-3">Rapide</h3>
                    <p class="text-gray-600">Performance optimisée pour une expérience utilisateur exceptionnelle</p>
                </div>
                <div class="text-center">
                    <div class="w-16 h-16 bg-green-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                        <svg class="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                        </svg>
                    </div>
                    <h3 class="text-xl font-semibold mb-3">Fiable</h3>
                    <p class="text-gray-600">Une solution robuste sur laquelle vous pouvez compter</p>
                </div>
                <div class="text-center">
                    <div class="w-16 h-16 bg-purple-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                        <svg class="w-8 h-8 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"></path>
                        </svg>
                    </div>
                    <h3 class="text-xl font-semibold mb-3">Simple</h3>
                    <p class="text-gray-600">Interface intuitive conçue pour tous les utilisateurs</p>
                </div>
            </div>
        </div>
    </section>

    <!-- Pricing Section -->
    <section id="pricing" class="section-padding">
        <div class="container">
            <div class="text-center mb-12">
                <h2 class="text-3xl font-bold text-gray-900 mb-4">Tarifs</h2>
                <p class="text-lg text-gray-600">Choisissez le plan qui vous convient</p>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto">
                <div class="card text-center border-2 border-gray-200">
                    <h3 class="text-2xl font-bold mb-4">Gratuit</h3>
                    <div class="text-4xl font-bold text-gray-900 mb-4">0€<span class="text-lg text-gray-600">/mois</span></div>
                    <ul class="space-y-3 mb-8">
                        <li class="flex items-center justify-center"><svg class="w-5 h-5 text-green-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>1 site web</li>
                        <li class="flex items-center justify-center"><svg class="w-5 h-5 text-green-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>Support de base</li>
                    </ul>
                    <a href="#" class="btn-secondary w-full">Commencer</a>
                </div>
                <div class="card text-center border-2 border-blue-500 relative">
                    <div class="absolute -top-4 left-1/2 transform -translate-x-1/2 bg-blue-500 text-white px-4 py-1 rounded-full text-sm">Populaire</div>
                    <h3 class="text-2xl font-bold mb-4">Pro</h3>
                    <div class="text-4xl font-bold text-gray-900 mb-4">29€<span class="text-lg text-gray-600">/mois</span></div>
                    <ul class="space-y-3 mb-8">
                        <li class="flex items-center justify-center"><svg class="w-5 h-5 text-green-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>Sites illimités</li>
                        <li class="flex items-center justify-center"><svg class="w-5 h-5 text-green-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>Support prioritaire</li>
                        <li class="flex items-center justify-center"><svg class="w-5 h-5 text-green-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>Analytics avancés</li>
                    </ul>
                    <a href="#" class="btn-primary w-full">Commencer</a>
                </div>
                <div class="card text-center border-2 border-gray-200">
                    <h3 class="text-2xl font-bold mb-4">Enterprise</h3>
                    <div class="text-4xl font-bold text-gray-900 mb-4">99€<span class="text-lg text-gray-600">/mois</span></div>
                    <ul class="space-y-3 mb-8">
                        <li class="flex items-center justify-center"><svg class="w-5 h-5 text-green-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>Tout inclus</li>
                        <li class="flex items-center justify-center"><svg class="w-5 h-5 text-green-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>Support dédié</li>
                        <li class="flex items-center justify-center"><svg class="w-5 h-5 text-green-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>Personnalisation</li>
                    </ul>
                    <a href="#" class="btn-secondary w-full">Nous contacter</a>
                </div>
            </div>
        </div>
    </section>

    <!-- CTA Section -->
    <section class="section-padding bg-blue-600 text-white">
        <div class="container text-center">
            <h2 class="text-3xl font-bold mb-4">Prêt à commencer ?</h2>
            <p class="text-xl mb-8">Rejoignez des milliers d'utilisateurs satisfaits</p>
            <a href="#" class="btn-primary bg-white text-blue-600 hover:bg-gray-100">Démarrer maintenant</a>
        </div>
    </section>

    <!-- Footer -->
    <footer class="bg-gray-900 text-white section-padding">
        <div class="container text-center">
            <p>&copy; {{CURRENT_YEAR}} {{SITE_TITLE}}. Tous droits réservés.</p>
            <p class="text-sm text-gray-400 mt-2">Site créé avec AI Website Generator</p>
        </div>
    </footer>
        """

    def _get_ecommerce_html(self) -> str:
        """Get HTML structure for e-commerce template"""
        return """
    <!-- Navigation -->
    <nav class="bg-white shadow-sm">
        <div class="container">
            <div class="flex items-center justify-between h-16">
                <div class="font-bold text-xl text-gray-900">{{SITE_TITLE}}</div>
                <div class="hidden md:flex space-x-8">
                    <a href="#home" class="text-gray-700 hover:text-blue-600">Accueil</a>
                    <a href="#products" class="text-gray-700 hover:text-blue-600">Produits</a>
                    <a href="#about" class="text-gray-700 hover:text-blue-600">À propos</a>
                    <a href="#contact" class="text-gray-700 hover:text-blue-600">Contact</a>
                </div>
                <div class="flex items-center space-x-4">
                    <button class="p-2 text-gray-600 hover:text-gray-900">
                        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4m0 0L7 13m0 0l-2.5 5M7 13v6a2 2 0 002 2h6a2 2 0 002-2v-6"></path>
                        </svg>
                        <span class="sr-only">Panier</span>
                    </button>
                </div>
            </div>
        </div>
    </nav>

    <!-- Hero Section -->
    <section id="home" class="hero-section text-white section-padding">
        <div class="container">
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
                <div>
                    <h1 class="text-4xl md:text-5xl font-bold mb-6">{{SITE_TITLE}}</h1>
                    <p class="text-xl mb-4">{{SITE_SUBTITLE}}</p>
                    <p class="text-lg mb-8">{{SITE_DESCRIPTION}}</p>
                    <div class="space-x-4">
                        <a href="#products" class="btn-primary">Voir nos produits</a>
                        <a href="#about" class="btn-secondary bg-white text-blue-600 hover:bg-gray-100">En savoir plus</a>
                    </div>
                </div>
                <div>
                    <div class="bg-white bg-opacity-20 rounded-lg p-8 text-center">
                        <svg class="w-24 h-24 mx-auto mb-4" fill="currentColor" viewBox="0 0 20 20">
                            <path fill-rule="evenodd" d="M10 2L3 7v11a2 2 0 002 2h10a2 2 0 002-2V7l-7-5zM10 12a2 2 0 100-4 2 2 0 000 4z" clip-rule="evenodd"></path>
                        </svg>
                        <h3 class="text-xl font-semibold">Livraison Gratuite</h3>
                        <p class="text-sm mt-2">Dès 50€ d'achats</p>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Products Section -->
    <section id="products" class="section-padding bg-white">
        <div class="container">
            <div class="text-center mb-12">
                <h2 class="text-3xl font-bold text-gray-900 mb-4">Nos Produits</h2>
                <p class="text-lg text-gray-600 max-w-2xl mx-auto">Découvrez notre sélection de produits de qualité</p>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
                <div class="card hover:shadow-lg transition-shadow">
                    <div class="bg-gray-200 h-48 rounded-lg mb-4"></div>
                    <h3 class="text-lg font-semibold mb-2">Produit 1</h3>
                    <p class="text-gray-600 text-sm mb-3">Description du produit...</p>
                    <div class="flex items-center justify-between">
                        <span class="text-xl font-bold text-blue-600">29,99€</span>
                        <button class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition-colors">Ajouter</button>
                    </div>
                </div>
                <div class="card hover:shadow-lg transition-shadow">
                    <div class="bg-gray-200 h-48 rounded-lg mb-4"></div>
                    <h3 class="text-lg font-semibold mb-2">Produit 2</h3>
                    <p class="text-gray-600 text-sm mb-3">Description du produit...</p>
                    <div class="flex items-center justify-between">
                        <span class="text-xl font-bold text-blue-600">39,99€</span>
                        <button class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition-colors">Ajouter</button>
                    </div>
                </div>
                <div class="card hover:shadow-lg transition-shadow">
                    <div class="bg-gray-200 h-48 rounded-lg mb-4"></div>
                    <h3 class="text-lg font-semibold mb-2">Produit 3</h3>
                    <p class="text-gray-600 text-sm mb-3">Description du produit...</p>
                    <div class="flex items-center justify-between">
                        <span class="text-xl font-bold text-blue-600">49,99€</span>
                        <button class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition-colors">Ajouter</button>
                    </div>
                </div>
                <div class="card hover:shadow-lg transition-shadow">
                    <div class="bg-gray-200 h-48 rounded-lg mb-4"></div>
                    <h3 class="text-lg font-semibold mb-2">Produit 4</h3>
                    <p class="text-gray-600 text-sm mb-3">Description du produit...</p>
                    <div class="flex items-center justify-between">
                        <span class="text-xl font-bold text-blue-600">59,99€</span>
                        <button class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition-colors">Ajouter</button>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- About Section -->
    <section id="about" class="section-padding">
        <div class="container">
            <div class="max-w-4xl mx-auto text-center">
                <h2 class="text-3xl font-bold text-gray-900 mb-8">{{ABOUT_TITLE}}</h2>
                <p class="text-lg text-gray-600 leading-relaxed">{{ABOUT_CONTENT}}</p>
            </div>
        </div>
    </section>

    <!-- Footer -->
    <footer class="bg-gray-900 text-white section-padding">
        <div class="container">
            <div class="grid grid-cols-1 md:grid-cols-4 gap-8">
                <div>
                    <h3 class="text-lg font-semibold mb-4">{{SITE_TITLE}}</h3>
                    <p class="text-gray-400 text-sm">{{SITE_DESCRIPTION}}</p>
                </div>
                <div>
                    <h4 class="font-semibold mb-4">Liens Rapides</h4>
                    <ul class="space-y-2 text-sm text-gray-400">
                        <li><a href="#" class="hover:text-white">Accueil</a></li>
                        <li><a href="#" class="hover:text-white">Produits</a></li>
                        <li><a href="#" class="hover:text-white">À propos</a></li>
                        <li><a href="#" class="hover:text-white">Contact</a></li>
                    </ul>
                </div>
                <div>
                    <h4 class="font-semibold mb-4">Support</h4>
                    <ul class="space-y-2 text-sm text-gray-400">
                        <li><a href="#" class="hover:text-white">FAQ</a></li>
                        <li><a href="#" class="hover:text-white">Livraison</a></li>
                        <li><a href="#" class="hover:text-white">Retours</a></li>
                        <li><a href="#" class="hover:text-white">Contact</a></li>
                    </ul>
                </div>
                <div>
                    <h4 class="font-semibold mb-4">Suivez-nous</h4>
                    <div class="flex space-x-4">
                        <a href="#" class="text-gray-400 hover:text-white">Facebook</a>
                        <a href="#" class="text-gray-400 hover:text-white">Twitter</a>
                        <a href="#" class="text-gray-400 hover:text-white">Instagram</a>
                    </div>
                </div>
            </div>
            <div class="border-t border-gray-800 pt-8 mt-8 text-center">
                <p>&copy; {{CURRENT_YEAR}} {{SITE_TITLE}}. Tous droits réservés.</p>
                <p class="text-sm text-gray-400 mt-2">Site créé avec AI Website Generator</p>
            </div>
        </div>
    </footer>
        """