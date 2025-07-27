import React, { createContext, useContext, useReducer, useEffect } from 'react';
import { authAPI } from '../services/api';
import toast from 'react-hot-toast';

// Initial state
const initialState = {
  user: null,
  token: null,
  loading: true,
  isAuthenticated: false,
};

// Action types
const AUTH_ACTIONS = {
  SET_LOADING: 'SET_LOADING',
  LOGIN_SUCCESS: 'LOGIN_SUCCESS',
  LOGOUT: 'LOGOUT',
  UPDATE_USER: 'UPDATE_USER',
  SET_ERROR: 'SET_ERROR',
};

// Reducer
const authReducer = (state, action) => {
  switch (action.type) {
    case AUTH_ACTIONS.SET_LOADING:
      return {
        ...state,
        loading: action.payload,
      };
    
    case AUTH_ACTIONS.LOGIN_SUCCESS:
      return {
        ...state,
        user: action.payload.user,
        token: action.payload.token,
        isAuthenticated: true,
        loading: false,
      };
    
    case AUTH_ACTIONS.LOGOUT:
      return {
        ...state,
        user: null,
        token: null,
        isAuthenticated: false,
        loading: false,
      };
    
    case AUTH_ACTIONS.UPDATE_USER:
      return {
        ...state,
        user: { ...state.user, ...action.payload },
      };
    
    default:
      return state;
  }
};

// Create context
const AuthContext = createContext();

// Auth provider component
export const AuthProvider = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, initialState);

  // Check for existing token on mount
  useEffect(() => {
    const initAuth = async () => {
      try {
        const token = localStorage.getItem('token');
        const userData = localStorage.getItem('user');

        if (token && userData) {
          // Verify token is still valid
          const response = await authAPI.getCurrentUser();
          
          dispatch({
            type: AUTH_ACTIONS.LOGIN_SUCCESS,
            payload: {
              user: response.data,
              token: token,
            },
          });
        }
      } catch (error) {
        // Token is invalid, clear storage
        localStorage.removeItem('token');
        localStorage.removeItem('user');
      } finally {
        dispatch({
          type: AUTH_ACTIONS.SET_LOADING,
          payload: false,
        });
      }
    };

    initAuth();
  }, []);

  // Login function
  const login = async (credentials) => {
    try {
      dispatch({ type: AUTH_ACTIONS.SET_LOADING, payload: true });
      
      const response = await authAPI.login(credentials);
      const { access_token } = response.data;

      // Get user data
      const userResponse = await authAPI.getCurrentUser();
      const userData = userResponse.data;

      // Store in localStorage
      localStorage.setItem('token', access_token);
      localStorage.setItem('user', JSON.stringify(userData));

      dispatch({
        type: AUTH_ACTIONS.LOGIN_SUCCESS,
        payload: {
          user: userData,
          token: access_token,
        },
      });

      toast.success('Connexion réussie !');
      return { success: true };
    } catch (error) {
      const message = error.response?.data?.error || 'Erreur de connexion';
      toast.error(message);
      return { success: false, error: message };
    } finally {
      dispatch({ type: AUTH_ACTIONS.SET_LOADING, payload: false });
    }
  };

  // Register function
  const register = async (userData) => {
    try {
      dispatch({ type: AUTH_ACTIONS.SET_LOADING, payload: true });
      
      await authAPI.register(userData);
      
      toast.success('Inscription réussie ! Vous pouvez maintenant vous connecter.');
      return { success: true };
    } catch (error) {
      const message = error.response?.data?.error || 'Erreur lors de l\'inscription';
      toast.error(message);
      return { success: false, error: message };
    } finally {
      dispatch({ type: AUTH_ACTIONS.SET_LOADING, payload: false });
    }
  };

  // Logout function
  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    
    dispatch({ type: AUTH_ACTIONS.LOGOUT });
    toast.success('Déconnexion réussie');
  };

  // Update user profile
  const updateProfile = async (userData) => {
    try {
      const response = await authAPI.updateProfile(userData);
      const updatedUser = response.data;

      localStorage.setItem('user', JSON.stringify(updatedUser));
      
      dispatch({
        type: AUTH_ACTIONS.UPDATE_USER,
        payload: updatedUser,
      });

      toast.success('Profil mis à jour avec succès');
      return { success: true };
    } catch (error) {
      const message = error.response?.data?.error || 'Erreur lors de la mise à jour';
      toast.error(message);
      return { success: false, error: message };
    }
  };

  const value = {
    ...state,
    login,
    register,
    logout,
    updateProfile,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

// Custom hook to use auth context
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export default AuthContext;