import React from 'react';
import { Link } from 'react-router-dom';
import { 
  DocumentTextIcon,
  HeartIcon,
  CodeBracketIcon
} from '@heroicons/react/24/outline';

const Footer = () => {
  return (
    <footer className="bg-gray-50 border-t border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          
          {/* Logo & Description */}
          <div className="col-span-1 md:col-span-2">
            <div className="flex items-center space-x-2 mb-4">
              <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                <DocumentTextIcon className="w-5 h-5 text-white" />
              </div>
              <span className="text-xl font-bold text-gray-900">
                AI WebGen
              </span>
            </div>
            <p className="text-gray-600 mb-4 max-w-md">
              Créez des sites web professionnels en quelques minutes grâce à l'intelligence artificielle. 
              Notre plateforme vous aide à générer, personnaliser et déployer votre site facilement.
            </p>
            <div className="flex items-center space-x-1 text-gray-600">
              <span>Créé avec</span>
              <HeartIcon className="w-4 h-4 text-red-500" />
              <span>et</span>
              <CodeBracketIcon className="w-4 h-4 text-blue-500" />
              <span>par l'équipe AI WebGen</span>
            </div>
          </div>

          {/* Navigation */}
          <div>
            <h3 className="text-sm font-semibold text-gray-900 uppercase tracking-wider mb-4">
              Navigation
            </h3>
            <ul className="space-y-2">
              <li>
                <Link to="/" className="text-gray-600 hover:text-blue-600 transition-colors">
                  Accueil
                </Link>
              </li>
              <li>
                <Link to="/templates" className="text-gray-600 hover:text-blue-600 transition-colors">
                  Templates
                </Link>
              </li>
              <li>
                <Link to="/dashboard" className="text-gray-600 hover:text-blue-600 transition-colors">
                  Dashboard
                </Link>
              </li>
            </ul>
          </div>

          {/* Support */}
          <div>
            <h3 className="text-sm font-semibold text-gray-900 uppercase tracking-wider mb-4">
              Support
            </h3>
            <ul className="space-y-2">
              <li>
                <a href="#" className="text-gray-600 hover:text-blue-600 transition-colors">
                  Documentation
                </a>
              </li>
              <li>
                <a href="#" className="text-gray-600 hover:text-blue-600 transition-colors">
                  Aide
                </a>
              </li>
              <li>
                <a href="#" className="text-gray-600 hover:text-blue-600 transition-colors">
                  Contact
                </a>
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="mt-12 pt-8 border-t border-gray-200 flex flex-col sm:flex-row justify-between items-center">
          <div className="text-gray-600 text-sm">
            © 2025 AI WebGen. Tous droits réservés.
          </div>
          <div className="flex space-x-6 mt-4 sm:mt-0">
            <a href="#" className="text-gray-600 hover:text-blue-600 text-sm transition-colors">
              Mentions légales
            </a>
            <a href="#" className="text-gray-600 hover:text-blue-600 text-sm transition-colors">
              Politique de confidentialité
            </a>
            <a href="#" className="text-gray-600 hover:text-blue-600 text-sm transition-colors">
              Conditions d'utilisation
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;