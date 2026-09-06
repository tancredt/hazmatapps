import { defineStore } from 'pinia';
import { ref } from 'vue';

// Helper function to get CSRF token
export const getCsrfToken = async () => {
  const cookies = document.cookie.split(';');
  for (let i = 0; i < cookies.length; i++) {
    const cookie = cookies[i].trim();
    if (cookie.startsWith('csrftoken=')) {
      return cookie.substring('csrftoken='.length, cookie.length);
    }
  }
  
  try {
    const response = await fetch('/api/inventory/csrf-token/', {
      method: 'GET',
      credentials: 'include'
    });
    if (response.ok) {
      const data = await response.json();
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

  const checkAuth = async () => {
    loading.value = true;
    try {
      const response = await fetch('/api/inventory/auth/current-user/', {
        credentials: 'include'
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

  // Standard login (kept just in case you need it later)
  const login = async (username, password) => {
    loading.value = true;
    try {
      const csrfToken = await getCsrfToken();
      const response = await fetch('/api/inventory/auth/login/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken || '',
        },
        body: JSON.stringify({ username, password }),
        credentials: 'include'
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

  // 👇 NEW: PIN Login specifically for the Location Changer App 👇
  const pinLogin = async (pin) => {
    loading.value = true;
    try {
      const csrfToken = await getCsrfToken();
      const response = await fetch('/api/inventory/auth/pin-login/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken || '',
        },
        body: JSON.stringify({ pin }), // Only sends the 4-digit PIN
        credentials: 'include'
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
      console.error('PIN Login error:', error);
      return { success: false, message: 'Network error occurred' };
    } finally {
      loading.value = false;
    }
  };

  const logout = async () => {
    loading.value = true;
    try {
      const csrfToken = await getCsrfToken();
      const response = await fetch('/api/inventory/auth/logout/', {
        method: 'POST',
        headers: {
          'X-CSRFToken': csrfToken || '',
        },
        credentials: 'include'
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
    pinLogin, 
    logout
  };
});
