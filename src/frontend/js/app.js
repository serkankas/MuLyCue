/**
 * Main application JavaScript for MuLyCue
 * Handles common functionality across all pages
 */

// API Configuration
const API_BASE = window.location.origin;
const API_URL = `${API_BASE}/api`;
const WS_URL = `ws://${window.location.host}/ws`;

// Utility Functions
function formatTime(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}

function formatTimeMs(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = (seconds % 60).toFixed(3);
    return `${mins.toString().padStart(2, '0')}:${secs.padStart(6, '0')}`;
}

// API Helper Functions
async function apiGet(endpoint) {
    const response = await fetch(`${API_URL}${endpoint}`);
    if (!response.ok) {
        throw new Error(`API Error: ${response.statusText}`);
    }
    return await response.json();
}

async function apiPost(endpoint, data) {
    const response = await fetch(`${API_URL}${endpoint}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    });
    if (!response.ok) {
        throw new Error(`API Error: ${response.statusText}`);
    }
    return await response.json();
}

async function apiPut(endpoint, data) {
    const response = await fetch(`${API_URL}${endpoint}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    });
    if (!response.ok) {
        throw new Error(`API Error: ${response.statusText}`);
    }
    return await response.json();
}

async function apiDelete(endpoint) {
    const response = await fetch(`${API_URL}${endpoint}`, {
        method: 'DELETE'
    });
    if (!response.ok) {
        throw new Error(`API Error: ${response.statusText}`);
    }
    return await response.json();
}

// File Upload Helper
async function uploadFile(endpoint, formData) {
    const response = await fetch(`${API_URL}${endpoint}`, {
        method: 'POST',
        body: formData
    });
    if (!response.ok) {
        throw new Error(`Upload Error: ${response.statusText}`);
    }
    return await response.json();
}

// Local Storage Helpers
function saveToLocalStorage(key, value) {
    try {
        localStorage.setItem(key, JSON.stringify(value));
    } catch (e) {
        console.error('Error saving to localStorage:', e);
    }
}

function loadFromLocalStorage(key, defaultValue = null) {
    try {
        const item = localStorage.getItem(key);
        return item ? JSON.parse(item) : defaultValue;
    } catch (e) {
        console.error('Error loading from localStorage:', e);
        return defaultValue;
    }
}

// Toast Notification System
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    
    document.body.appendChild(toast);
    
    // Animate in
    setTimeout(() => toast.classList.add('show'), 10);
    
    // Remove after 3 seconds
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Keyboard Shortcuts
document.addEventListener('keydown', (e) => {
    // Ctrl+S / Cmd+S - Save (prevent default browser save)
    if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault();
        if (typeof saveSong === 'function') {
            saveSong();
        }
    }
    
    // Space - Play/Pause (only if not in input field)
    if (e.code === 'Space' && !['INPUT', 'TEXTAREA'].includes(e.target.tagName)) {
        e.preventDefault();
        if (typeof togglePlay === 'function') {
            togglePlay();
        }
    }
});

// Error Handler
window.addEventListener('error', (e) => {
    console.error('Global error:', e.error);
    showToast('An error occurred. Check console for details.', 'error');
});

// Page Load Handler
document.addEventListener('DOMContentLoaded', () => {
    console.log('MuLyCue loaded');
    
    // Check API health
    fetch(`${API_URL}/../health`)
        .then(res => res.json())
        .then(data => {
            console.log('API Status:', data);
        })
        .catch(err => {
            console.error('API not available:', err);
            showToast('Warning: API connection failed', 'warning');
        });
});

