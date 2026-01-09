/**
 * Application configuration.
 * Reads API URL from environment variables with fallback for local development.
 */
let API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Ensure API_URL is a full URL (not a relative path)
if (API_URL && !API_URL.startsWith('http://') && !API_URL.startsWith('https://')) {
    // If it's a relative path, prepend https://
    API_URL = `https://${API_URL}`;
}

// Remove trailing slash if present
API_URL = API_URL.replace(/\/$/, '');

export { API_URL };
