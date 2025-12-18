/**
 * Player mode JavaScript for MuLyCue
 * Handles real-time playback and display
 */

// Global state
let ws = null;
let currentSong = null;
let currentTranspose = 0;
let isPlaying = false;
let currentPosition = 0;
let duration = 0;

// Initialize player
document.addEventListener('DOMContentLoaded', () => {
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
    
    // Load settings from localStorage
    loadSettings();
});

function setupWebSocketCallbacks() {
    ws.on('position_update', (data) => {
        updatePosition(data.position);
    });
    
    ws.on('entry_change', (data) => {
        updateEntry(data.entry);
    });
    
    ws.on('section_change', (data) => {
        updateSection(data.section);
    });
    
    ws.on('beat_tick', (data) => {
        updateBeat(data.beat);
    });
    
    ws.on('playback_state', (data) => {
        updatePlaybackState(data.state);
    });
    
    ws.on('song_loaded', (data) => {
        handleSongLoaded(data.song);
    });
}

async function loadSong(songId) {
    try {
        const response = await fetch(`${API_URL}/songs/${songId}?transpose=${currentTranspose}`);
        const song = await response.json();
        
        currentSong = song;
        displaySongInfo(song);
        
        // Load song for playback
        await fetch(`${API_URL}/playback/load`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ song_id: songId })
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
    document.getElementById('bpmValue').textContent = song.meta.bpm;
    duration = song.meta.duration;
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

function updateEntry(entry) {
    // Update lyrics display
    const currentLine = document.getElementById('currentLine');
    const word = entry.word || '';
    currentLine.textContent = word;
    
    // Update chord display
    const currentChord = document.getElementById('currentChord');
    const chord = entry.chords || '-';
    currentChord.textContent = chord;
    
    // Animate entry change
    currentLine.classList.add('highlight');
    setTimeout(() => currentLine.classList.remove('highlight'), 300);
}

function updateSection(section) {
    const currentSection = document.getElementById('currentSection');
    currentSection.textContent = section.name;
    
    // Animate section change
    currentSection.classList.add('highlight');
    setTimeout(() => currentSection.classList.remove('highlight'), 500);
}

function updateBeat(beat) {
    // Clear all beat indicators
    for (let i = 1; i <= 4; i++) {
        const beatDot = document.getElementById(`beat${i}`);
        beatDot.classList.remove('active');
    }
    
    // Highlight current beat
    const currentBeat = document.getElementById(`beat${beat}`);
    if (currentBeat) {
        currentBeat.classList.add('active');
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
    if (isPlaying) {
        await fetch(`${API_URL}/playback/pause`, { method: 'POST' });
        ws.pause();
    } else {
        await fetch(`${API_URL}/playback/play`, { method: 'POST' });
        ws.play();
    }
}

async function stop() {
    await fetch(`${API_URL}/playback/stop`, { method: 'POST' });
    ws.stop();
    currentPosition = 0;
    updatePosition(0);
}

function skipBackward() {
    const newPosition = Math.max(0, currentPosition - 10);
    seekTo((newPosition / duration) * 100);
}

function skipForward() {
    const newPosition = Math.min(duration, currentPosition + 10);
    seekTo((newPosition / duration) * 100);
}

async function seekTo(percentage) {
    const position = (percentage / 100) * duration;
    await fetch(`${API_URL}/playback/seek?position=${position}`, { method: 'POST' });
    ws.seek(position);
}

function setVolume(value) {
    // Volume control would be handled by audio engine
    console.log('Set volume:', value);
}

// Transpose Controls
async function transposeUp() {
    currentTranspose++;
    updateTranspose();
}

async function transposeDown() {
    currentTranspose--;
    updateTranspose();
}

async function updateTranspose() {
    document.getElementById('transposeValue').textContent = currentTranspose > 0 ? `+${currentTranspose}` : currentTranspose;
    
    if (currentSong) {
        // Reload song with new transpose
        const urlParams = new URLSearchParams(window.location.search);
        const songId = urlParams.get('song');
        if (songId) {
            await loadSong(songId);
        }
    }
}

// Settings
function toggleSettings() {
    const panel = document.getElementById('settingsPanel');
    panel.style.display = panel.style.display === 'none' ? 'block' : 'none';
}

function changeFontSize(value) {
    document.getElementById('fontSizeValue').textContent = `${value}px`;
    document.querySelector('.lyrics-display').style.fontSize = `${value}px`;
    saveSettings();
}

function changeDisplayMode(mode) {
    // Implement display mode changes
    console.log('Display mode:', mode);
    saveSettings();
}

function changeChordNotation(notation) {
    // Reload song with new notation preference
    console.log('Chord notation:', notation);
    saveSettings();
}

function changeTheme(theme) {
    document.body.className = `theme-${theme}`;
    saveSettings();
}

function toggleChords(show) {
    const chordDisplay = document.querySelector('.chord-display');
    chordDisplay.style.display = show ? 'flex' : 'none';
    saveSettings();
}

function toggleBeat(show) {
    const beatIndicator = document.querySelector('.beat-indicator');
    beatIndicator.style.display = show ? 'flex' : 'none';
    saveSettings();
}

function saveSettings() {
    const settings = {
        fontSize: document.getElementById('fontSizeSlider').value,
        displayMode: document.getElementById('displayMode').value,
        chordNotation: document.getElementById('chordNotation').value,
        theme: document.getElementById('theme').value,
        showChords: document.getElementById('showChords').checked,
        showBeat: document.getElementById('showBeat').checked
    };
    localStorage.setItem('playerSettings', JSON.stringify(settings));
}

function loadSettings() {
    const settings = JSON.parse(localStorage.getItem('playerSettings') || '{}');
    
    if (settings.fontSize) {
        document.getElementById('fontSizeSlider').value = settings.fontSize;
        changeFontSize(settings.fontSize);
    }
    if (settings.displayMode) {
        document.getElementById('displayMode').value = settings.displayMode;
    }
    if (settings.chordNotation) {
        document.getElementById('chordNotation').value = settings.chordNotation;
    }
    if (settings.theme) {
        document.getElementById('theme').value = settings.theme;
        changeTheme(settings.theme);
    }
    if (settings.showChords !== undefined) {
        document.getElementById('showChords').checked = settings.showChords;
        toggleChords(settings.showChords);
    }
    if (settings.showBeat !== undefined) {
        document.getElementById('showBeat').checked = settings.showBeat;
        toggleBeat(settings.showBeat);
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

