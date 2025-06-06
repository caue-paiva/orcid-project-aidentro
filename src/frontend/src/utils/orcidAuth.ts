/**
 * Utility functions for managing ORCID authentication state
 */

export const getStoredOrcidId = (): string | null => {
  return localStorage.getItem('orcid_id');
};

export const getStoredAuthStatus = (): boolean => {
  return localStorage.getItem('orcid_authenticated') === 'true';
};

export const clearOrcidAuth = (): void => {
  localStorage.removeItem('orcid_id');
  localStorage.removeItem('orcid_authenticated');
};

export const setOrcidAuth = (orcidId: string): void => {
  localStorage.setItem('orcid_id', orcidId);
  localStorage.setItem('orcid_authenticated', 'true');
};

export const isOrcidAuthenticated = (): boolean => {
  const orcidId = getStoredOrcidId();
  const isAuthenticated = getStoredAuthStatus();
  return !!(orcidId && isAuthenticated);
}; 