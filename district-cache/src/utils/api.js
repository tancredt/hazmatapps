let csrfToken = null;

export async function apiFetch(endpoint, options = {}) {
  const url = endpoint.startsWith('http') ? endpoint : `/api/inventory${endpoint}`;
  
  // Fetch CSRF token if we are making a state-changing request
  if (!csrfToken && options.method && options.method !== 'GET') {
    try {
      // FIX: Added /inventory here too
      const csrfRes = await fetch('/api/inventory/csrf-token/', { credentials: 'include' });
      if (csrfRes.ok) {
        const csrfData = await csrfRes.json();
        csrfToken = csrfData.csrfToken;
      }
    } catch (e) {
      console.warn("Could not fetch CSRF token", e);
    }
  }

  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {})
  };

  if (csrfToken && options.method !== 'GET') {
    headers['X-CSRFToken'] = csrfToken;
  }

  const response = await fetch(url, {
    ...options,
    headers,
    credentials: 'include' // Crucial for Django session cookies
  });

  if (response.status === 401 || response.status === 403) {
    // Session timed out or unauthorized. Force redirect to login.
    const currentPath = window.location.pathname + window.location.search;
    window.location.href = `/login?redirect=${encodeURIComponent(currentPath)}`;
  
    return Promise.reject(new Error('Session expired'));
  }
  const contentType = response.headers.get('content-type');
  if (contentType && contentType.includes('application/json')) {
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.message || data.detail || 'An error occurred');
    }
    return response.status === 204 ? null : data;
  } 
  
  // If Django returned HTML (like a 404 or 500 error page), throw a readable error
  throw new Error(`Server returned ${response.status}. Check backend console for details.`);
}

