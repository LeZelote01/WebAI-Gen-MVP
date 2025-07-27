import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { websiteAPI, templateAPI } from '../services/api';
import { 
  DocumentTextIcon,
  EyeIcon,
  CloudArrowUpIcon,
  CogIcon,
  SparklesIcon,
  ArrowLeftIcon,
  BookmarkIcon,
  ArrowDownTrayIcon
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

const WebsiteEditor = () => {
  const { websiteId } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  
  const [website, setWebsite] = useState(null);
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [activeTab, setActiveTab] = useState('content');
  
  // Form data for new website
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    template_id: '',
    meta_title: '',
    meta_description: ''
  });

  useEffect(() => {
    if (websiteId) {
      fetchWebsite();
    } else {
      fetchTemplates();
    }
  }, [websiteId]);

  const fetchWebsite = async () => {
    try {
      setLoading(true);
      const response = await websiteAPI.getWebsite(websiteId);
      setWebsite(response.data);
      setFormData({
        name: response.data.name || '',
        description: response.data.description || '',
        template_id: response.data.template_id || '',
        meta_title: response.data.meta_title || '',
        meta_description: response.data.meta_description || ''
      });
    } catch (error) {
      toast.error('Erreur lors du chargement du site');
      navigate('/dashboard');
    } finally {
      setLoading(false);
    }
  };

  const fetchTemplates = async () => {
    try {
      setLoading(true);
      const response = await templateAPI.getTemplates();
      setTemplates(response.data.items || []);
    } catch (error) {
      toast.error('Erreur lors du chargement des templates');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSave = async () => {
    if (!formData.name.trim()) {
      toast.error('Le nom du site est requis');
      return;
    }

    try {
      setSaving(true);
      
      if (websiteId) {
        // Update existing website
        await websiteAPI.updateWebsite(websiteId, formData);
        toast.success('Site mis à jour avec succès');
        fetchWebsite();
      } else {
        // Create new website
        if (!formData.template_id) {
          toast.error('Veuillez sélectionner un template');
          return;
        }
        
        const response = await websiteAPI.createWebsite(formData);
        toast.success('Site créé avec succès');
        navigate(`/editor/${response.data.id}`);
      }
    } catch (error) {
      toast.error('Erreur lors de la sauvegarde');
    } finally {
      setSaving(false);
    }
  };

  const handleQuickGenerate = async () => {
    if (!formData.name.trim() || !formData.template_id) {
      toast.error('Veuillez remplir le nom et sélectionner un template');
      return;
    }

    try {
      setSaving(true);
      const response = await websiteAPI.generateWebsite({
        template_id: formData.template_id,
        website_name: formData.name,
        website_description: formData.description
      });
      
      toast.success('Site généré avec succès !');
      navigate(`/editor/${response.data.id}`);
    } catch (error) {
      toast.error('Erreur lors de la génération');
    } finally {
      setSaving(false);
    }
  };

  const handleExportWebsite = async () => {
    if (!website) {
      toast.error('Aucun site à exporter');
      return;
    }

    try {
      toast.loading('Préparation de l\'export...', { id: 'export' });
      
      const response = await websiteAPI.exportWebsite(website.id);
      
      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      
      // Generate filename
      const safeName = website.slug || website.name.replace(/\s+/g, '-').toLowerCase();
      link.setAttribute('download', `${safeName}-export.zip`);
      
      // Trigger download
      document.body.appendChild(link);
      link.click();
      link.remove();
      
      // Clean up
      window.URL.revokeObjectURL(url);
      
      toast.success('Site exporté avec succès !', { id: 'export' });
    } catch (error) {
      console.error('Export error:', error);
      toast.error('Erreur lors de l\'export', { id: 'export' });
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Chargement de l'éditeur...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center">
              <button
                onClick={() => navigate('/dashboard')}
                className="flex items-center space-x-2 text-gray-600 hover:text-gray-900 mr-4"
              >
                <ArrowLeftIcon className="w-5 h-5" />
                <span>Retour</span>
              </button>
              <h1 className="text-xl font-semibold text-gray-900">
                {websiteId ? 'Modifier le site' : 'Créer un nouveau site'}
              </h1>
            </div>
            
            <div className="flex items-center space-x-4">
              {website && (
                <>
                  <button 
                    className="flex items-center space-x-2 text-gray-600 hover:text-gray-900"
                  >
                    <EyeIcon className="w-5 h-5" />
                    <span>Aperçu</span>
                  </button>
                  
                  <button
                    onClick={handleExportWebsite}
                    className="flex items-center space-x-2 text-green-600 hover:text-green-900"
                    title="Exporter le code source"
                  >
                    <ArrowDownTrayIcon className="w-5 h-5" />
                    <span>Exporter</span>
                  </button>
                </>
              )}
              
              <button
                onClick={handleSave}
                disabled={saving}
                className="bg-blue-600 text-white px-4 py-2 rounded-lg font-semibold hover:bg-blue-700 transition-colors flex items-center space-x-2 disabled:opacity-50"
              >
                {saving ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    <span>Sauvegarde...</span>
                  </>
                ) : (
                  <>
                    <BookmarkIcon className="w-4 h-4" />
                    <span>Sauvegarder</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Main Content */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-sm">
              {/* Tabs */}
              <div className="border-b border-gray-200">
                <nav className="flex space-x-8 px-6">
                  <button
                    onClick={() => setActiveTab('content')}
                    className={`py-4 text-sm font-medium border-b-2 ${
                      activeTab === 'content'
                        ? 'text-blue-600 border-blue-600'
                        : 'text-gray-500 border-transparent hover:text-gray-700'
                    }`}
                  >
                    Contenu
                  </button>
                  <button
                    onClick={() => setActiveTab('settings')}
                    className={`py-4 text-sm font-medium border-b-2 ${
                      activeTab === 'settings'
                        ? 'text-blue-600 border-blue-600'
                        : 'text-gray-500 border-transparent hover:text-gray-700'
                    }`}
                  >
                    Paramètres
                  </button>
                </nav>
              </div>

              {/* Tab Content */}
              <div className="p-6">
                {activeTab === 'content' && (
                  <div className="space-y-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Nom du site *
                      </label>
                      <input
                        type="text"
                        name="name"
                        value={formData.name}
                        onChange={handleInputChange}
                        placeholder="Mon site web"
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Description
                      </label>
                      <textarea
                        name="description"
                        value={formData.description}
                        onChange={handleInputChange}
                        rows={3}
                        placeholder="Description de votre site web..."
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      />
                    </div>

                    {!websiteId && (
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Template *
                        </label>
                        <select
                          name="template_id"
                          value={formData.template_id}
                          onChange={handleInputChange}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                        >
                          <option value="">Sélectionner un template</option>
                          {templates.map(template => (
                            <option key={template.id} value={template.id}>
                              {template.name} - {template.category}
                            </option>
                          ))}
                        </select>
                      </div>
                    )}

                    {!websiteId && (
                      <div className="bg-blue-50 p-4 rounded-lg">
                        <div className="flex items-center space-x-2 mb-2">
                          <SparklesIcon className="w-5 h-5 text-blue-600" />
                          <span className="font-medium text-blue-900">Génération IA</span>
                        </div>
                        <p className="text-blue-700 text-sm mb-4">
                          Générez automatiquement votre site avec du contenu personnalisé grâce à notre IA.
                        </p>
                        <button
                          onClick={handleQuickGenerate}
                          disabled={saving}
                          className="bg-blue-600 text-white px-4 py-2 rounded-lg font-semibold hover:bg-blue-700 transition-colors flex items-center space-x-2 disabled:opacity-50"
                        >
                          {saving ? (
                            <>
                              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                              <span>Génération...</span>
                            </>
                          ) : (
                            <>
                              <SparklesIcon className="w-4 h-4" />
                              <span>Générer avec IA</span>
                            </>
                          )}
                        </button>
                      </div>
                    )}

                    {website && (
                      <div className="bg-gray-50 p-4 rounded-lg">
                        <h3 className="font-medium text-gray-900 mb-2">Aperçu du contenu</h3>
                        <p className="text-sm text-gray-600 mb-4">
                          L'éditeur visuel sera bientôt disponible. Pour l'instant, vous pouvez modifier les informations de base.
                        </p>
                        <div className="text-sm text-gray-500">
                          <p><strong>Statut:</strong> {website.status}</p>
                          <p><strong>Créé:</strong> {new Date(website.created_at).toLocaleDateString('fr-FR')}</p>
                          <p><strong>Modifié:</strong> {new Date(website.updated_at).toLocaleDateString('fr-FR')}</p>
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {activeTab === 'settings' && (
                  <div className="space-y-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Titre SEO
                      </label>
                      <input
                        type="text"
                        name="meta_title"
                        value={formData.meta_title}
                        onChange={handleInputChange}
                        placeholder="Titre pour les moteurs de recherche"
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Description SEO
                      </label>
                      <textarea
                        name="meta_description"
                        value={formData.meta_description}
                        onChange={handleInputChange}
                        rows={3}
                        placeholder="Description pour les moteurs de recherche"
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      />
                    </div>

                    <div className="bg-yellow-50 p-4 rounded-lg">
                      <div className="flex items-center space-x-2 mb-2">
                        <CogIcon className="w-5 h-5 text-yellow-600" />
                        <span className="font-medium text-yellow-900">Paramètres avancés</span>
                      </div>
                      <p className="text-yellow-700 text-sm">
                        Les paramètres avancés (domaine personnalisé, SSL, etc.) seront disponibles dans la prochaine version.
                      </p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Sidebar */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h3 className="font-medium text-gray-900 mb-4">Actions rapides</h3>
              
              <div className="space-y-3">
                <button
                  onClick={handleSave}
                  disabled={saving}
                  className="w-full bg-blue-600 text-white px-4 py-2 rounded-lg font-semibold hover:bg-blue-700 transition-colors flex items-center justify-center space-x-2 disabled:opacity-50"
                >
                  <BookmarkIcon className="w-4 h-4" />
                  <span>Sauvegarder</span>
                </button>

                {website && (
                  <>
                    <button 
                      onClick={handleExportWebsite}
                      className="w-full bg-green-600 text-white px-4 py-2 rounded-lg font-semibold hover:bg-green-700 transition-colors flex items-center justify-center space-x-2"
                    >
                      <ArrowDownTrayIcon className="w-4 h-4" />
                      <span>Exporter le code</span>
                    </button>
                    
                    <button className="w-full bg-purple-600 text-white px-4 py-2 rounded-lg font-semibold hover:bg-purple-700 transition-colors flex items-center justify-center space-x-2">
                      <CloudArrowUpIcon className="w-4 h-4" />
                      <span>Publier</span>
                    </button>
                  </>
                )}
              </div>

              {website && (
                <div className="mt-6 pt-6 border-t border-gray-200">
                  <h4 className="font-medium text-gray-900 mb-2">Informations</h4>
                  <div className="text-sm text-gray-600 space-y-1">
                    <p><strong>Vues:</strong> {website.view_count}</p>
                    <p><strong>Statut:</strong> {website.status}</p>
                    <p><strong>Slug:</strong> {website.slug}</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WebsiteEditor;