import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { 
  RocketLaunchIcon,
  SparklesIcon,
  CubeIcon,
  BoltIcon,
  GlobeAltIcon,
  CloudIcon
} from '@heroicons/react/24/outline';

const Home = () => {
  const { isAuthenticated } = useAuth();

  const features = [
    {
      icon: SparklesIcon,
      title: "IA Générative",
      description: "Notre IA génère automatiquement du contenu personnalisé pour votre site web"
    },
    {
      icon: CubeIcon,
      title: "Templates Professionnels",
      description: "Choisissez parmi une large sélection de templates modernes et responsive"
    },
    {
      icon: BoltIcon,
      title: "Création Rapide",
      description: "Créez votre site web en moins de 5 minutes avec notre générateur intelligent"
    },
    {
      icon: GlobeAltIcon,
      title: "Responsive Design",
      description: "Tous nos sites s'adaptent parfaitement à tous les écrans et devices"
    },
    {
      icon: CloudIcon,
      title: "Hébergement Inclus",
      description: "Déployez votre site instantanément avec notre hébergement intégré"
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50">
      {/* Hero Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-16">
        <div className="text-center">
          <div className="flex justify-center mb-8">
            <div className="w-16 h-16 bg-gradient-to-r from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center">
              <RocketLaunchIcon className="w-8 h-8 text-white" />
            </div>
          </div>
          
          <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6">
            Créez votre site web avec
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600">
              {' '}l'IA
            </span>
          </h1>
          
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
            Générez des sites web professionnels en quelques minutes grâce à notre intelligence artificielle avancée. 
            Pas besoin de compétences techniques !
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            {isAuthenticated ? (
              <Link
                to="/dashboard"
                className="bg-blue-600 text-white px-8 py-3 rounded-lg text-lg font-semibold hover:bg-blue-700 transition-colors inline-flex items-center space-x-2"
              >
                <span>Accéder au Dashboard</span>
                <RocketLaunchIcon className="w-5 h-5" />
              </Link>
            ) : (
              <>
                <Link
                  to="/register"
                  className="bg-blue-600 text-white px-8 py-3 rounded-lg text-lg font-semibold hover:bg-blue-700 transition-colors inline-flex items-center space-x-2"
                >
                  <span>Commencer gratuitement</span>
                  <RocketLaunchIcon className="w-5 h-5" />
                </Link>
                <Link
                  to="/templates"
                  className="bg-white text-gray-900 px-8 py-3 rounded-lg text-lg font-semibold hover:bg-gray-50 transition-colors border border-gray-300"
                >
                  Voir les templates
                </Link>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            Pourquoi choisir AI WebGen ?
          </h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Notre plateforme combine la puissance de l'IA avec la simplicité d'utilisation pour créer des sites web exceptionnels.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <div key={index} className="bg-white rounded-xl p-6 shadow-sm hover:shadow-md transition-shadow">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                <feature.icon className="w-6 h-6 text-blue-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                {feature.title}
              </h3>
              <p className="text-gray-600">
                {feature.description}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* CTA Section */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
            Prêt à créer votre site web ?
          </h2>
          <p className="text-xl text-blue-100 mb-8 max-w-2xl mx-auto">
            Rejoignez des milliers d'utilisateurs qui ont déjà créé leur site avec notre IA.
          </p>
          {!isAuthenticated && (
            <Link
              to="/register"
              className="bg-white text-blue-600 px-8 py-3 rounded-lg text-lg font-semibold hover:bg-gray-50 transition-colors inline-flex items-center space-x-2"
            >
              <span>Commencer maintenant</span>
              <RocketLaunchIcon className="w-5 h-5" />
            </Link>
          )}
        </div>
      </div>
    </div>
  );
};

export default Home;