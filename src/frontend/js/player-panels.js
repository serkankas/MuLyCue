/**
 * Player with Panels - Main Logic
 * Integrates WebSocket, playback controls, and panel system
 */

// Global state
let ws = null;
let currentSong = null;
let currentTranspose = 0;
let isPlaying = false;
let currentPosition = 0;
let duration = 0;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    console.log('Player-panels.js: DOM loaded');
    
    // Wait for panel manager to be ready
    const checkPanelManager = () => {
        if (window.panelManager) {
            console.log('Panel Manager ready, initializing player...');
            initializePlayer();
        } else {
            console.log('Waiting for Panel Manager...');
            setTimeout(checkPanelManager, 50);
        }
    };
    
    checkPanelManager();
});

function initializePlayer() {
    console.log('Initializing player...');
    
    // Connect WebSocket
    ws = new MuLyCueWebSocket();
    ws.connect();
    
    // Set up WebSocket callbacks
    setupWebSocketCallbacks();
    
    // Load song from URL parameter if present
    const urlParams = new URLSearchParams(window.location.search);
    const songId = urlParams.get('song');
    if (songId) {
        loadSong(songId);
    }
    
    // Update panel toggles based on loaded panels
    updatePanelToggles();
    
    console.log('Player initialized successfully');
}

function setupWebSocketCallbacks() {
    ws.on('position_update', (data) => {
        updatePosition(data.position);
        broadcastToAllPanels({
            position: data.position,
            duration: duration
        });
    });
    
    ws.on('entry_change', (data) => {
        broadcastToAllPanels({
            currentLine: data.entry.word,
            currentChord: data.entry.chords,
            currentSection: data.entry.section
        });
    });
    
    ws.on('section_change', (data) => {
        broadcastToAllPanels({
            currentSection: data.section.name
        });
    });
    
    ws.on('beat_tick', (data) => {
        broadcastToAllPanels({
            currentBeat: data.beat
        });
    });
    
    ws.on('playback_state', (data) => {
        updatePlaybackState(data.state);
    });
    
    ws.on('song_loaded', (data) => {
        handleSongLoaded(data.song);
    });
}

function broadcastToAllPanels(data) {
    if (window.panelManager) {
        // Add current song data
        const fullData = {
            ...data,
            bpm: currentSong?.meta?.bpm || 120,
            transpose: currentTranspose
        };
        
        window.panelManager.broadcast(fullData);
    }
}

async function loadSong(songId) {
    try {
        showToast('Loading song...', 'info');
        
        const response = await fetch(`${API_URL}/songs/${songId}?transpose=${currentTranspose}`);
        const song = await response.json();
        
        currentSong = song;
        duration = song.meta.duration;
        
        displaySongInfo(song);
        
        // Load song for playback
        await fetch(`${API_URL}/playback/load`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ song_id: songId })
        });
        
        // Broadcast to panels
        broadcastToAllPanels({
            bpm: song.meta.bpm,
            currentSection: song.sections[0]?.name || '-',
            duration: duration
        });
        
        showToast('Song loaded successfully', 'success');
    } catch (error) {
        console.error('Error loading song:', error);
        showToast('Error loading song', 'error');
    }
}

function displaySongInfo(song) {
    document.getElementById('songTitle').textContent = song.meta.title;
    document.getElementById('songArtist').textContent = song.meta.artist;
    document.getElementById('durationDisplay').textContent = formatTime(duration);
}

function updatePosition(position) {
    currentPosition = position;
    document.getElementById('currentTimeDisplay').textContent = formatTime(position);
    
    // Update progress slider
    const progressSlider = document.getElementById('progressSlider');
    if (duration > 0) {
        progressSlider.value = (position / duration) * 100;
    }
}

function updatePlaybackState(state) {
    isPlaying = (state === 'playing');
    const playPauseBtn = document.getElementById('playPauseBtn');
    
    if (isPlaying) {
        playPauseBtn.textContent = '⏸';
        playPauseBtn.classList.add('playing');
    } else {
        playPauseBtn.textContent = '▶️';
        playPauseBtn.classList.remove('playing');
    }
}

function handleSongLoaded(song) {
    currentSong = song;
    displaySongInfo(song);
}

// Playback Controls
async function togglePlay() {
    try {
        if (isPlaying) {
            await fetch(`${API_URL}/playback/pause`, { method: 'POST' });
            ws.pause();
        } else {
            await fetch(`${API_URL}/playback/play`, { method: 'POST' });
            ws.play();
        }
    } catch (error) {
        console.error('Error toggling playback:', error);
        showToast('Playback error', 'error');
    }
}

async function stop() {
    try {
        await fetch(`${API_URL}/playback/stop`, { method: 'POST' });
        ws.stop();
        currentPosition = 0;
        updatePosition(0);
    } catch (error) {
        console.error('Error stopping playback:', error);
    }
}

function skipBackward() {
    showToast('Seeking not available in v0.1.0', 'warning');
}

function skipForward() {
    showToast('Seeking not available in v0.1.0', 'warning');
}

function setVolume(value) {
    // Volume control would be handled by audio engine
    console.log('Set volume:', value);
}

// Transpose Controls
async function transposeUp() {
    currentTranspose++;
    await updateTranspose();
}

async function transposeDown() {
    currentTranspose--;
    await updateTranspose();
}

async function updateTranspose() {
    broadcastToAllPanels({
        transpose: currentTranspose
    });
    
    if (currentSong) {
        const urlParams = new URLSearchParams(window.location.search);
        const songId = urlParams.get('song');
        if (songId) {
            await loadSong(songId);
        }
    }
}

// Layout Controls
function toggleLayoutControls() {
    const controls = document.getElementById('layoutControls');
    controls.style.display = controls.style.display === 'none' ? 'block' : 'none';
}

function loadPreset(presetName) {
    if (presetName && window.panelManager) {
        window.panelManager.loadLayout(presetName);
        updatePanelToggles();
    }
}

function togglePanel(type, enabled) {
    if (!window.panelManager) return;
    
    if (enabled) {
        // Add panel with default config
        window.panelManager.addPanel(type);
    } else {
        // Remove all panels of this type
        const panels = window.panelManager.getPanelsByType(type);
        panels.forEach(panel => window.panelManager.removePanel(panel.id));
    }
}

function updatePanelToggles() {
    if (!window.panelManager) return;
    
    const types = ['lyrics', 'chords', 'bpm', 'beat', 'section', 'timeline', 'transpose'];
    
    types.forEach(type => {
        const checkbox = document.getElementById(`toggle-${type}`);
        if (checkbox) {
            const panels = window.panelManager.getPanelsByType(type);
            checkbox.checked = panels.length > 0;
        }
    });
}

function toggleSnap(enabled) {
    if (window.panelManager) {
        window.panelManager.snapToEdges = enabled;
    }
}

function importLayout(file) {
    if (file && window.panelManager) {
        window.panelManager.importLayout(file);
        updatePanelToggles();
    }
}

// Song Selector
async function showSongSelector() {
    const selector = document.getElementById('songSelector');
    selector.style.display = selector.style.display === 'none' ? 'block' : 'none';
    
    if (selector.style.display === 'block') {
        await loadSongList();
    }
}

async function loadSongList() {
    try {
        const response = await fetch(`${API_URL}/songs`);
        const data = await response.json();
        displaySongList(data.songs);
    } catch (error) {
        console.error('Error loading songs:', error);
        document.getElementById('songListContainer').innerHTML = '<p class="error">Error loading songs</p>';
    }
}

function displaySongList(songs) {
    const container = document.getElementById('songListContainer');
    
    if (songs.length === 0) {
        container.innerHTML = '<p class="empty">No songs found</p>';
        return;
    }
    
    container.innerHTML = songs.map(song => `
        <div class="song-item" onclick="selectSong('${song.id}')">
            <h3>${song.title}</h3>
            <p>${song.artist}</p>
            <p class="meta">Key: ${song.key} | BPM: ${song.bpm}</p>
        </div>
    `).join('');
}

function filterSongList() {
    // Implement song filtering
    const searchTerm = document.getElementById('songSearch').value.toLowerCase();
    // Filter logic here
}

async function selectSong(songId) {
    showSongSelector(); // Close selector
    await loadSong(songId);
    
    // Update URL without reload
    const url = new URL(window.location);
    url.searchParams.set('song', songId);
    window.history.pushState({}, '', url);
}

// Helper function
function formatTime(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
}

