/**
 * Application configuration.
 * Reads API URL from environment variables with fallback for local development.
 */
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export { API_URL };
