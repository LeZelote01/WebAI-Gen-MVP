import React from 'react';
import { Link } from 'react-router-dom';
import { 
  ExclamationTriangleIcon,
  HomeIcon,
  ArrowLeftIcon
} from '@heroicons/react/24/outline';

const NotFound = () => {
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="text-center">
        <div className="flex justify-center mb-8">
          <div className="w-16 h-16 bg-red-100 rounded-2xl flex items-center justify-center">
            <ExclamationTriangleIcon className="w-8 h-8 text-red-600" />
          </div>
        </div>
        
        <h1 className="text-6xl font-bold text-gray-900 mb-4">404</h1>
        <h2 className="text-2xl font-semibold text-gray-700 mb-4">
          Page non trouvée
        </h2>
        <p className="text-lg text-gray-600 mb-8 max-w-md mx-auto">
          Désolé, la page que vous recherchez n'existe pas ou a été déplacée.
        </p>
        
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link
            to="/"
            className="bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors inline-flex items-center space-x-2"
          >
            <HomeIcon className="w-5 h-5" />
            <span>Retour à l'accueil</span>
          </Link>
          
          <button
            onClick={() => window.history.back()}
            className="bg-white text-gray-900 px-6 py-3 rounded-lg font-semibold hover:bg-gray-50 transition-colors border border-gray-300 inline-flex items-center space-x-2"
          >
            <ArrowLeftIcon className="w-5 h-5" />
            <span>Page précédente</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default NotFound;