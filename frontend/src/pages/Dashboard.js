import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { websiteAPI, hostingAPI } from '../services/api';
import { 
  PlusIcon,
  EyeIcon,
  PencilIcon,
  TrashIcon,
  GlobeAltIcon,
  CalendarIcon,
  ChartBarIcon,
  UserIcon,
  DocumentTextIcon,
  SparklesIcon,
  ArrowDownTrayIcon,
  CloudArrowUpIcon,
  CloudArrowDownIcon,
  ShieldCheckIcon,
  LinkIcon
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

const Dashboard = () => {
  const { user } = useAuth();
  const [websites, setWebsites] = useState([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    totalSites: 0,
    publishedSites: 0,
    draftSites: 0,
    totalViews: 0
  });

  useEffect(() => {
    fetchWebsites();
  }, []);

  const fetchWebsites = async () => {
    try {
      setLoading(true);
      const response = await websiteAPI.getWebsites();
      const sitesData = response.data.items || [];
      setWebsites(sitesData);
      
      // Calculate stats
      const totalSites = sitesData.length;
      const publishedSites = sitesData.filter(site => site.status === 'published').length;
      const draftSites = sitesData.filter(site => site.status === 'draft').length;
      const totalViews = sitesData.reduce((sum, site) => sum + site.view_count, 0);
      
      setStats({
        totalSites,
        publishedSites,
        draftSites,
        totalViews
      });
    } catch (error) {
      toast.error('Erreur lors du chargement des sites');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteWebsite = async (websiteId) => {
    if (!window.confirm('Êtes-vous sûr de vouloir supprimer ce site ?')) return;
    
    try {
      await websiteAPI.deleteWebsite(websiteId);
      toast.success('Site supprimé avec succès');
      fetchWebsites();
    } catch (error) {
      toast.error('Erreur lors de la suppression');
    }
  };

  const handleExportWebsite = async (website) => {
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

  const handleDeployWebsite = async (website) => {
    try {
      toast.loading('Déploiement en cours...', { id: 'deploy' });
      
      const response = await websiteAPI.deployWebsite(website.id);
      
      toast.success('Site déployé avec succès !', { id: 'deploy' });
      
      // Refresh websites list to get updated info
      fetchWebsites();
    } catch (error) {
      console.error('Deploy error:', error);
      toast.error('Erreur lors du déploiement', { id: 'deploy' });
    }
  };

  const handleUndeployWebsite = async (website) => {
    if (!window.confirm('Êtes-vous sûr de vouloir retirer ce site de l\'hébergement ?')) return;
    
    try {
      toast.loading('Suppression de l\'hébergement...', { id: 'undeploy' });
      
      await websiteAPI.undeployWebsite(website.id);
      
      toast.success('Site retiré de l\'hébergement', { id: 'undeploy' });
      
      // Refresh websites list
      fetchWebsites();
    } catch (error) {
      console.error('Undeploy error:', error);
      toast.error('Erreur lors de la suppression', { id: 'undeploy' });
    }
  };

  const handleRedeployWebsite = async (website) => {
    try {
      toast.loading('Redéploiement en cours...', { id: 'redeploy' });
      
      await websiteAPI.redeployWebsite(website.id);
      
      toast.success('Site redéployé avec succès !', { id: 'redeploy' });
      
      // Refresh websites list
      fetchWebsites();
    } catch (error) {
      console.error('Redeploy error:', error);
      toast.error('Erreur lors du redéploiement', { id: 'redeploy' });
    }
  };

  const handleConfigureSSL = async (website) => {
    try {
      toast.loading('Configuration SSL...', { id: 'ssl' });
      
      await websiteAPI.configureSSL(website.id);
      
      toast.success('SSL configuré avec succès !', { id: 'ssl' });
      
      // Refresh websites list
      fetchWebsites();
    } catch (error) {
      console.error('SSL error:', error);
      toast.error('Erreur lors de la configuration SSL', { id: 'ssl' });
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('fr-FR', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'published': return 'bg-green-100 text-green-800';
      case 'draft': return 'bg-yellow-100 text-yellow-800';
      case 'archived': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'published': return 'Publié';
      case 'draft': return 'Brouillon';
      case 'archived': return 'Archivé';
      default: return 'Inconnu';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Chargement de votre dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
              <p className="text-gray-600 mt-1">
                Bienvenue, {user?.full_name || user?.username} ! Gérez vos sites web ici.
              </p>
            </div>
            <Link
              to="/editor"
              className="bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors flex items-center space-x-2"
            >
              <PlusIcon className="w-5 h-5" />
              <span>Créer un nouveau site</span>
            </Link>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow-sm p-6">
            <div className="flex items-center">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <DocumentTextIcon className="w-6 h-6 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Sites</p>
                <p className="text-2xl font-bold text-gray-900">{stats.totalSites}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm p-6">
            <div className="flex items-center">
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                <GlobeAltIcon className="w-6 h-6 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Sites Publiés</p>
                <p className="text-2xl font-bold text-gray-900">{stats.publishedSites}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm p-6">
            <div className="flex items-center">
              <div className="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center">
                <PencilIcon className="w-6 h-6 text-yellow-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Brouillons</p>
                <p className="text-2xl font-bold text-gray-900">{stats.draftSites}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm p-6">
            <div className="flex items-center">
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                <ChartBarIcon className="w-6 h-6 text-purple-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Vues</p>
                <p className="text-2xl font-bold text-gray-900">{stats.totalViews}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Websites List */}
        <div className="bg-white rounded-lg shadow-sm">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">Mes Sites Web</h2>
          </div>
          
          {websites.length === 0 ? (
            <div className="p-12 text-center">
              <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <SparklesIcon className="w-8 h-8 text-gray-400" />
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                Aucun site créé pour le moment
              </h3>
              <p className="text-gray-600 mb-6">
                Créez votre premier site web avec notre générateur IA en quelques minutes.
              </p>
              <Link
                to="/editor"
                className="bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors inline-flex items-center space-x-2"
              >
                <PlusIcon className="w-5 h-5" />
                <span>Créer mon premier site</span>
              </Link>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Site
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Statut
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Hébergement
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Vues
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Modifié
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {websites.map((website) => (
                    <tr key={website.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center mr-3">
                            <DocumentTextIcon className="w-5 h-5 text-white" />
                          </div>
                          <div>
                            <div className="text-sm font-medium text-gray-900">
                              {website.name}
                            </div>
                            <div className="text-sm text-gray-500">
                              {website.description || 'Aucune description'}
                            </div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(website.status)}`}>
                          {getStatusText(website.status)}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center space-x-2">
                          {website.is_hosted ? (
                            <div className="flex items-center space-x-1">
                              <GlobeAltIcon className="w-4 h-4 text-green-600" />
                              <span className="text-sm text-green-600 font-medium">Hébergé</span>
                              {website.ssl_enabled && (
                                <ShieldCheckIcon className="w-4 h-4 text-green-600" title="SSL activé" />
                              )}
                            </div>
                          ) : (
                            <span className="text-sm text-gray-500">Non hébergé</span>
                          )}
                        </div>
                        {website.hosting_url && (
                          <div className="text-xs text-gray-500 mt-1">
                            <a 
                              href={website.hosting_url} 
                              target="_blank" 
                              rel="noopener noreferrer"
                              className="hover:text-blue-600 flex items-center space-x-1"
                            >
                              <LinkIcon className="w-3 h-3" />
                              <span className="truncate max-w-40">{website.hosting_url}</span>
                            </a>
                          </div>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {website.view_count}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        <div className="flex items-center">
                          <CalendarIcon className="w-4 h-4 mr-1" />
                          {formatDate(website.updated_at)}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <div className="flex space-x-1">
                          {website.status === 'published' && website.hosting_url && (
                            <a
                              href={website.hosting_url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-blue-600 hover:text-blue-900 p-1 rounded"
                              title="Voir le site"
                            >
                              <EyeIcon className="w-4 h-4" />
                            </a>
                          )}
                          <Link
                            to={`/editor/${website.id}`}
                            className="text-indigo-600 hover:text-indigo-900 p-1 rounded"
                            title="Modifier"
                          >
                            <PencilIcon className="w-4 h-4" />
                          </Link>
                          <button
                            onClick={() => handleExportWebsite(website)}
                            className="text-green-600 hover:text-green-900 p-1 rounded"
                            title="Exporter le code"
                          >
                            <ArrowDownTrayIcon className="w-4 h-4" />
                          </button>
                          
                          {/* Hosting actions */}
                          {website.is_hosted ? (
                            <>
                              <button
                                onClick={() => handleRedeployWebsite(website)}
                                className="text-purple-600 hover:text-purple-900 p-1 rounded"
                                title="Redéployer"
                              >
                                <CloudArrowUpIcon className="w-4 h-4" />
                              </button>
                              {!website.ssl_enabled && (
                                <button
                                  onClick={() => handleConfigureSSL(website)}
                                  className="text-yellow-600 hover:text-yellow-900 p-1 rounded"
                                  title="Configurer SSL"
                                >
                                  <ShieldCheckIcon className="w-4 h-4" />
                                </button>
                              )}
                              <button
                                onClick={() => handleUndeployWebsite(website)}
                                className="text-orange-600 hover:text-orange-900 p-1 rounded"
                                title="Retirer de l'hébergement"
                              >
                                <CloudArrowDownIcon className="w-4 h-4" />
                              </button>
                            </>
                          ) : (
                            <button
                              onClick={() => handleDeployWebsite(website)}
                              className="text-blue-600 hover:text-blue-900 p-1 rounded"
                              title="Déployer le site"
                            >
                              <CloudArrowUpIcon className="w-4 h-4" />
                            </button>
                          )}
                          
                          <button
                            onClick={() => handleDeleteWebsite(website.id)}
                            className="text-red-600 hover:text-red-900 p-1 rounded"
                            title="Supprimer"
                          >
                            <TrashIcon className="w-4 h-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;