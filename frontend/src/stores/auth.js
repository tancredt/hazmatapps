import { defineStore } from 'pinia';
import { ref } from 'vue';

// Helper function to get CSRF token - exported for use in components
export const getCsrfToken = async () => {
  // Try to get the CSRF token from cookie first
  const cookies = document.cookie.split(';');
  for (let i = 0; i < cookies.length; i++) {
    const cookie = cookies[i].trim();
    if (cookie.startsWith('csrftoken=')) {
      return cookie.substring('csrftoken='.length, cookie.length);
    }
  }

  // If not found in cookie, try to get it from the Django API
  try {
    const response = await fetch('/api/inventory/csrf-token/', {
      method: 'GET',
      credentials: 'include'
    });

    if (response.ok) {
      const data = await response.json();
      // Set the cookie for future requests
      document.cookie = `csrftoken=${data.csrfToken}; path=/; SameSite=Strict`;
      return data.csrfToken;
    }
  } catch (error) {
    console.warn('Could not fetch CSRF token from API:', error);
  }

  return null;
};

export const useAuthStore = defineStore('auth', () => {
  const isAuthenticated = ref(false);
  const currentUser = ref(null);
  const loading = ref(false);

  // Check if user is authenticated
  const checkAuth = async () => {
    loading.value = true;
    try {
      const response = await fetch('/api/inventory/auth/current-user/', {
        credentials: 'include'  // Important for session cookies
      });

      const data = await response.json();

      if (data.authenticated) {
        isAuthenticated.value = true;
        currentUser.value = data.user;
      } else {
        isAuthenticated.value = false;
        currentUser.value = null;
      }
    } catch (error) {
      console.error('Error checking auth status:', error);
      isAuthenticated.value = false;
      currentUser.value = null;
    } finally {
      loading.value = false;
    }
  };

  // Login user
  const login = async (username, password) => {
    loading.value = true;
    try {
      const csrfToken = await getCsrfToken();

      const response = await fetch('/api/inventory/auth/login/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken || '',  // Include CSRF token in header
        },
        body: JSON.stringify({
          username,
          password
        }),
        credentials: 'include'  // Important for session cookies
      });

      const data = await response.json();

      if (data.success) {
        isAuthenticated.value = true;
        currentUser.value = data.user;
        return { success: true, user: data.user };
      } else {
        return { success: false, message: data.message };
      }
    } catch (error) {
      console.error('Login error:', error);
      return { success: false, message: 'Network error occurred' };
    } finally {
      loading.value = false;
    }
  };

  // Logout user
  const logout = async () => {
    loading.value = true;
    try {
      const csrfToken = await getCsrfToken();

      const response = await fetch('/api/inventory/auth/logout/', {
        method: 'POST',
        headers: {
          'X-CSRFToken': csrfToken || '',  // Include CSRF token in header
        },
        credentials: 'include'  // Important for session cookies
      });

      const data = await response.json();

      if (data.success) {
        isAuthenticated.value = false;
        currentUser.value = null;
        return { success: true };
      } else {
        return { success: false, message: data.message };
      }
    } catch (error) {
      console.error('Logout error:', error);
      return { success: false, message: 'Network error occurred' };
    } finally {
      loading.value = false;
    }
  };

  return {
    isAuthenticated,
    currentUser,
    loading,
    checkAuth,
    login,
    logout
  };
});