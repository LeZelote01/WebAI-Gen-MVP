import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { templateAPI } from '../services/api';
import { 
  MagnifyingGlassIcon,
  FunnelIcon,
  EyeIcon,
  StarIcon,
  TagIcon,
  ArrowRightIcon,
  SparklesIcon
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

const Templates = () => {
  const { isAuthenticated } = useAuth();
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [sortBy, setSortBy] = useState('popular');

  const categories = [
    { id: 'all', name: 'Tous', count: 0 },
    { id: 'portfolio', name: 'Portfolio', count: 0 },
    { id: 'business', name: 'Entreprise', count: 0 },
    { id: 'blog', name: 'Blog', count: 0 },
    { id: 'ecommerce', name: 'E-commerce', count: 0 },
    { id: 'landing', name: 'Landing Page', count: 0 }
  ];

  useEffect(() => {
    fetchTemplates();
  }, []);

  const fetchTemplates = async () => {
    try {
      setLoading(true);
      const response = await templateAPI.getTemplates();
      const templatesData = response.data.items || [];
      setTemplates(templatesData);
    } catch (error) {
      toast.error('Erreur lors du chargement des templates');
    } finally {
      setLoading(false);
    }
  };

  const filteredTemplates = templates.filter(template => {
    const matchesSearch = template.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         template.description?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || template.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  const sortedTemplates = [...filteredTemplates].sort((a, b) => {
    switch (sortBy) {
      case 'popular':
        return b.usage_count - a.usage_count;
      case 'rating':
        return b.rating_avg - a.rating_avg;
      case 'newest':
        return new Date(b.created_at) - new Date(a.created_at);
      case 'name':
        return a.name.localeCompare(b.name);
      default:
        return 0;
    }
  });

  const getCategoryColor = (category) => {
    const colors = {
      portfolio: 'bg-blue-100 text-blue-800',
      business: 'bg-green-100 text-green-800',
      blog: 'bg-purple-100 text-purple-800',
      ecommerce: 'bg-yellow-100 text-yellow-800',
      landing: 'bg-pink-100 text-pink-800'
    };
    return colors[category] || 'bg-gray-100 text-gray-800';
  };

  const renderStars = (rating) => {
    return Array.from({ length: 5 }, (_, i) => (
      <StarIcon 
        key={i} 
        className={`w-4 h-4 ${i < rating ? 'text-yellow-400 fill-current' : 'text-gray-300'}`} 
      />
    ));
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Chargement des templates...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Templates</h1>
          <p className="text-gray-600">
            Choisissez parmi notre collection de templates professionnels et créez votre site en quelques clics.
          </p>
        </div>

        {/* Search and Filters */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
          <div className="flex flex-col lg:flex-row gap-4">
            {/* Search Bar */}
            <div className="flex-1">
              <div className="relative">
                <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  placeholder="Rechercher un template..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>

            {/* Category Filter */}
            <div className="flex items-center space-x-2">
              <FunnelIcon className="w-5 h-5 text-gray-400" />
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                {categories.map(category => (
                  <option key={category.id} value={category.id}>
                    {category.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Sort Options */}
            <div className="flex items-center space-x-2">
              <span className="text-sm text-gray-500">Trier par:</span>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="popular">Popularité</option>
                <option value="rating">Note</option>
                <option value="newest">Plus récent</option>
                <option value="name">Nom</option>
              </select>
            </div>
          </div>
        </div>

        {/* Templates Grid */}
        {sortedTemplates.length === 0 ? (
          <div className="text-center py-12">
            <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <SparklesIcon className="w-8 h-8 text-gray-400" />
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Aucun template trouvé
            </h3>
            <p className="text-gray-600 mb-6">
              Essayez de modifier vos critères de recherche ou de filtrage.
            </p>
            <button
              onClick={() => {
                setSearchTerm('');
                setSelectedCategory('all');
              }}
              className="bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
            >
              Voir tous les templates
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {sortedTemplates.map((template) => (
              <div key={template.id} className="bg-white rounded-lg shadow-sm overflow-hidden hover:shadow-md transition-shadow">
                {/* Template Preview */}
                <div className="relative h-48 bg-gradient-to-br from-blue-50 to-purple-50 flex items-center justify-center">
                  {template.preview_image ? (
                    <img 
                      src={template.preview_image} 
                      alt={template.name}
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="text-center">
                      <div className="w-16 h-16 bg-white rounded-lg flex items-center justify-center mx-auto mb-2">
                        <SparklesIcon className="w-8 h-8 text-blue-600" />
                      </div>
                      <p className="text-gray-600 text-sm">Preview</p>
                    </div>
                  )}
                  
                  {/* Preview overlay */}
                  <div className="absolute inset-0 bg-black bg-opacity-0 hover:bg-opacity-20 transition-opacity flex items-center justify-center">
                    <button className="opacity-0 hover:opacity-100 transition-opacity bg-white text-gray-900 px-4 py-2 rounded-lg font-semibold flex items-center space-x-2">
                      <EyeIcon className="w-4 h-4" />
                      <span>Aperçu</span>
                    </button>
                  </div>
                </div>

                {/* Template Info */}
                <div className="p-6">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="text-lg font-semibold text-gray-900">
                      {template.name}
                    </h3>
                    {template.is_premium && (
                      <span className="bg-gradient-to-r from-yellow-400 to-orange-500 text-white text-xs px-2 py-1 rounded-full font-semibold">
                        Premium
                      </span>
                    )}
                  </div>

                  <p className="text-gray-600 text-sm mb-3 line-clamp-2">
                    {template.description || 'Template professionnel pour votre site web'}
                  </p>

                  {/* Category */}
                  <div className="flex items-center justify-between mb-3">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getCategoryColor(template.category)}`}>
                      {template.category}
                    </span>
                    
                    {/* Rating */}
                    <div className="flex items-center space-x-1">
                      <div className="flex">
                        {renderStars(template.rating_avg)}
                      </div>
                      <span className="text-sm text-gray-500">
                        ({template.rating_count})
                      </span>
                    </div>
                  </div>

                  {/* Usage count */}
                  <div className="flex items-center justify-between mb-4">
                    <span className="text-sm text-gray-500">
                      {template.usage_count} utilisations
                    </span>
                    
                    {/* Tags */}
                    {template.tags && template.tags.length > 0 && (
                      <div className="flex items-center space-x-1">
                        <TagIcon className="w-4 h-4 text-gray-400" />
                        <span className="text-sm text-gray-500">
                          {template.tags.slice(0, 2).join(', ')}
                        </span>
                      </div>
                    )}
                  </div>

                  {/* Action Button */}
                  <div className="flex items-center justify-between">
                    <div className="text-sm text-gray-500">
                      {template.is_premium ? `${template.price / 100}€` : 'Gratuit'}
                    </div>
                    
                    {isAuthenticated ? (
                      <Link
                        to={`/editor?template=${template.id}`}
                        className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-blue-700 transition-colors flex items-center space-x-2"
                      >
                        <span>Utiliser</span>
                        <ArrowRightIcon className="w-4 h-4" />
                      </Link>
                    ) : (
                      <Link
                        to="/login"
                        className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-blue-700 transition-colors flex items-center space-x-2"
                      >
                        <span>Connexion</span>
                        <ArrowRightIcon className="w-4 h-4" />
                      </Link>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* CTA Section */}
        {!isAuthenticated && (
          <div className="mt-16 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg p-8 text-center">
            <h2 className="text-2xl font-bold text-white mb-4">
              Prêt à créer votre site web ?
            </h2>
            <p className="text-blue-100 mb-6">
              Créez votre compte gratuitement et commencez à utiliser nos templates professionnels.
            </p>
            <Link
              to="/register"
              className="bg-white text-blue-600 px-8 py-3 rounded-lg font-semibold hover:bg-gray-50 transition-colors inline-flex items-center space-x-2"
            >
              <span>Créer mon compte</span>
              <ArrowRightIcon className="w-5 h-5" />
            </Link>
          </div>
        )}
      </div>
    </div>
  );
};

export default Templates;