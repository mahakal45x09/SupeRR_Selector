/**
 * SupeRR Selector — REST API Client
 */

const API_BASE = window.location.origin.includes('http') ? window.location.origin : 'http://127.0.0.1:8000';

export async function fetchOverview() {
  try {
    const res = await fetch(`${API_BASE}/api/overview`);
    if (!res.ok) throw new Error('API error');
    return await res.json();
  } catch (err) {
    console.warn('API fallback to local data:', err);
    return null;
  }
}

export async function fetchBatters(params = {}) {
  try {
    const query = new URLSearchParams(params).toString();
    const res = await fetch(`${API_BASE}/api/batters?${query}`);
    if (!res.ok) throw new Error('API error');
    const json = await res.json();
    return json.data;
  } catch (err) {
    console.warn('API fallback to local data:', err);
    return window.__FALLBACK_DATA?.batters || [];
  }
}

export async function fetchBowlers(params = {}) {
  try {
    const query = new URLSearchParams(params).toString();
    const res = await fetch(`${API_BASE}/api/bowlers?${query}`);
    if (!res.ok) throw new Error('API error');
    const json = await res.json();
    return json.data;
  } catch (err) {
    console.warn('API fallback to local data:', err);
    return window.__FALLBACK_DATA?.bowlers || [];
  }
}

export async function fetchPlayerDeepDive(playerId) {
  try {
    const res = await fetch(`${API_BASE}/api/players/${playerId}`);
    if (!res.ok) throw new Error('API error');
    return await res.json();
  } catch (err) {
    console.warn('Deep dive API error:', err);
    return null;
  }
}

export async function fetchClutchXI() {
  try {
    const res = await fetch(`${API_BASE}/api/clutch-xi`);
    if (!res.ok) throw new Error('API error');
    return await res.json();
  } catch (err) {
    console.warn('Clutch XI API error:', err);
    return null;
  }
}

export async function fetchMethodology() {
  try {
    const res = await fetch(`${API_BASE}/api/methodology`);
    if (!res.ok) throw new Error('API error');
    return await res.json();
  } catch (err) {
    console.warn('Methodology API error:', err);
    return null;
  }
}
