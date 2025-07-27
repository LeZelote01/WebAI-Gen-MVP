import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { QueryClient, QueryClientProvider } from 'react-query';

// Components
import Navbar from './components/Navbar';
import Footer from './components/Footer';

// Pages
import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Templates from './pages/Templates';
import WebsiteEditor from './pages/WebsiteEditor';
import NotFound from './pages/NotFound';

// Hooks and Context
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <Router>
          <div className="min-h-screen bg-secondary-50 flex flex-col">
            <Toaster 
              position="top-right"
              toastOptions={{
                duration: 4000,
                className: 'text-sm',
                style: {
                  borderRadius: '8px',
                  padding: '12px 16px',
                },
              }}
            />
            
            <Navbar />
            
            <main className="flex-grow">
              <Routes>
                {/* Public routes */}
                <Route path="/" element={<Home />} />
                <Route path="/login" element={<Login />} />
                <Route path="/register" element={<Register />} />
                <Route path="/templates" element={<Templates />} />
                
                {/* Protected routes */}
                <Route path="/dashboard" element={
                  <ProtectedRoute>
                    <Dashboard />
                  </ProtectedRoute>
                } />
                <Route path="/editor/:websiteId?" element={
                  <ProtectedRoute>
                    <WebsiteEditor />
                  </ProtectedRoute>
                } />
                
                {/* 404 */}
                <Route path="*" element={<NotFound />} />
              </Routes>
            </main>
            
            <Footer />
          </div>
        </Router>
      </AuthProvider>
    </QueryClientProvider>
  );
}

export default App;