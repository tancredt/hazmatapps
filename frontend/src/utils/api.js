// Utility functions for API calls with CSRF token handling

// Helper function to get CSRF token from cookie
const getCsrfTokenFromCookie = () => {
  const name = 'csrftoken';
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
};

// Async helper function to get CSRF token from API if not in cookie
const getCsrfTokenFromApi = async () => {
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

// Async function to get CSRF token (from cookie or API)
const getCsrfToken = async () => {
  const tokenFromCookie = getCsrfTokenFromCookie();
  if (tokenFromCookie) {
    return tokenFromCookie;
  }
  
  // If not in cookie, try to get from API
  return await getCsrfTokenFromApi();
};

// Main API function that handles CSRF tokens
export const apiCall = async (url, options = {}) => {
  // Get the CSRF token asynchronously
  let csrfToken = await getCsrfToken();

  // Set default options
  const defaultOptions = {
    credentials: 'include', // Important for session cookies
    headers: {
      'Content-Type': 'application/json',
      ...(csrfToken ? { 'X-CSRFToken': csrfToken } : {}), // Include CSRF token if available
    }
  };

  // Merge user options with defaults
  const mergedOptions = {
    ...defaultOptions,
    ...options,
    headers: {
      ...defaultOptions.headers,
      ...options.headers
    }
  };

  // If the method is dangerous and we still don't have a CSRF token, warn
  const dangerousMethods = ['POST', 'PUT', 'PATCH', 'DELETE'];
  if (dangerousMethods.includes(options.method?.toUpperCase()) && !csrfToken) {
    console.warn('CSRF token not found but required for this request');
  }

  const response = await fetch(url, mergedOptions);

  // If the response is JSON, parse it
  const contentType = response.headers.get('content-type');
  if (contentType && contentType.includes('application/json')) {
    return {
      ok: response.ok,
      status: response.status,
      data: await response.json()
    };
  } else {
    // For non-JSON responses, return text
    return {
      ok: response.ok,
      status: response.status,
      data: await response.text()
    };
  }
};

// Convenience methods
export const get = async (url, options = {}) => {
  return apiCall(url, { ...options, method: 'GET' });
};

export const post = async (url, body, options = {}) => {
  return apiCall(url, {
    ...options,
    method: 'POST',
    body: typeof body === 'string' ? body : JSON.stringify(body)
  });
};

export const put = async (url, body, options = {}) => {
  return apiCall(url, {
    ...options,
    method: 'PUT',
    body: typeof body === 'string' ? body : JSON.stringify(body)
  });
};

export const del = async (url, options = {}) => {
  return apiCall(url, { ...options, method: 'DELETE' });
};

export const patch = async (url, body, options = {}) => {
  return apiCall(url, {
    ...options,
    method: 'PATCH',
    body: typeof body === 'string' ? body : JSON.stringify(body)
  });
};
